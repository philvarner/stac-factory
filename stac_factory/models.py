from datetime import timezone
from typing import Annotated, Any, Literal, NamedTuple, Self

from annotated_types import Ge, Le
from pydantic import (
    AfterValidator,
    AnyUrl,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    PositiveFloat,
    PrivateAttr,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    Strict,
    StringConstraints,
    field_validator,
    model_serializer,
    model_validator,
)

from stac_factory.constants import HttpMethod

# MD - STAC Item spec: https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md
# JS - JSON schema: https://github.com/radiantearth/stac-spec/tree/master/item-spec/json-schema
# BP - Best Practices https://github.com/radiantearth/stac-spec/blob/master/best-practices.md
# GJ - GeoJSON spec: https://datatracker.ietf.org/doc/html/rfc7946

# Basic JSON object type annotation
type JSONFieldName = Annotated[
    str, StringConstraints(min_length=1, max_length=100, pattern=r"^[-_.:a-zA-Z0-9]+$"), Strict()
]
type JSONValue = (
    str | URI | int | float | bool | None | dict[str, "JSONValue"] | list["JSONValue"]
)  # todo: constrain strs here?
type JSONObject = dict[JSONFieldName, JSONValue]

type ShortStr = Annotated[str, StringConstraints(min_length=1, max_length=100, pattern=r"^[-_.a-zA-Z0-9]+$"), Strict()]
type LongishStr = Annotated[
    str, StringConstraints(min_length=1, max_length=1000, pattern=r"^[-_.a-zA-Z0-9]+$"), Strict()
]
type LicenseStr = ShortStr  # todo: make better with literal enums and SPDX
type BodyStr = Annotated[str, StringConstraints(min_length=1, max_length=10000)]

# BP - searchable identifiers lowercase characters, numbers, _, and -
type Identifier = ShortStr
type ItemIdentifier = Identifier
type CollectionIdentifier = Identifier
type StacExtensionIdentifier = Annotated[
    str,
    StringConstraints(min_length=1, max_length=100, pattern=r"^[-_.:/a-zA-Z0-9]+$"),  # TODO: URI?
]

type ZeroTo90 = Annotated[float, Ge(0.0), Le(90.0)]
type ZeroTo360 = Annotated[float, Ge(0.0), Le(360.0)]
type Negative90To90 = Annotated[float, Ge(-90.0), Le(90.0)]
type Percentage = Annotated[float, Ge(0.0), Le(100)]
type Lat = Annotated[float, Ge(-90.0), Le(90)]
type Lon = Annotated[float, Ge(-180.0), Le(180)]
type Elevation = Annotated[float, Ge(-10_000_000.0), Le(10_000_000.0)]


class StacBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)


class Position2D(NamedTuple):
    longitude: Lon
    latitude: Lat


class Position3D(NamedTuple):
    longitude: Lon
    latitude: Lat
    elevation: Elevation


type Position = Position2D | Position3D

type LinearRingCoordinates = Annotated[list[Position], Field(min_length=4, max_length=512)]
type PolygonCoordinates = Annotated[list[LinearRingCoordinates], Field(min_length=1, max_length=1)]
type MultiPolygonCoordinates = Annotated[list[PolygonCoordinates], Field(min_length=1, max_length=2)]


class Polygon(StacBaseModel):
    type: Literal["Polygon"]
    coordinates: PolygonCoordinates

    # simplify
    # validate no crossing, wound correctly, within 90/180, doesn't cross antimeridian
    #     @field_validator("coordinates")
    #     def check_closure(cls, coordinates: List) -> List:
    #         """Validate that Polygon is closed (first and last coordinate are the same)."""
    #         if any(ring[-1] != ring[0] for ring in coordinates):
    #             raise ValueError("All linear rings have the same start and end coordinates")

    #         return coordinates


class MultiPolygon(StacBaseModel):
    type: Literal["MultiPolygon"]
    coordinates: MultiPolygonCoordinates

    #     #     @field_validator("coordinates")
    #     #     def check_closure(cls, coordinates: List) -> List:
    #     #         """Validate that Polygon is closed (first and last coordinate are the same)."""
    #     #         if any(ring[-1] != ring[0] for polygon in coordinates for ring in polygon):
    #     #             raise ValueError("All linear rings have the same start and end coordinates")

    #     #         return coordinates


class BBox2d(StacBaseModel):
    # [sw_lon, sw_lat, ne_lon, ne_lat]
    w_lon: Lon
    s_lat: Lat
    e_lon: Lon
    n_lat: Lat

    @model_validator(mode="after")
    def validate_relative_latitudes(self) -> Self:
        if self.s_lat > self.n_lat:
            raise ValueError("South latitude must be less than or equal to north latitude")
        return self

    @model_serializer
    def ser_model(self) -> list[float]:
        return [self.w_lon, self.s_lat, self.e_lon, self.n_lat]

    # TODO: loader for array


class BBox3d(BBox2d):
    # [sw_lon, sw_lat, bottom_elevation, ne_lon, ne_lat, top_elevation]
    bottom_elevation: Elevation
    top_elevation: Elevation

    @model_validator(mode="after")
    def validate_relative_elevations(self) -> Self:
        if self.top_elevation <= self.bottom_elevation:
            raise ValueError("Bottom elevation is above top elevation")
        return self

    @model_serializer
    def ser_model(self) -> list[float]:
        return [
            self.w_lon,
            self.s_lat,
            self.bottom_elevation,
            self.e_lon,
            self.n_lat,
            self.top_elevation,
        ]


type UtcDatetime = Annotated[
    AwareDatetime,
    AfterValidator(lambda d: d.astimezone(timezone.utc)),
]

# todo: use for start/end?
type UtcDatetimeInterval = tuple[UtcDatetime | None, UtcDatetime | None]


type URI = AnyUrl


# Media type regex based on RFC 6838 syntax
type MediaType = Annotated[
    str,
    StringConstraints(pattern=r"^[a-zA-Z0-9][-a-zA-Z0-9.+]*/[a-zA-Z0-9][-a-zA-Z0-9.+]*(?:;.*)?$"),
    Strict(),
]

type Title = Annotated[str, StringConstraints(min_length=1, max_length=100), Strict()]
type Description = Annotated[str, StringConstraints(min_length=1, max_length=10000), Strict()]


class Commons(StacBaseModel): ...


type Rel = Annotated[str, StringConstraints(min_length=1, max_length=256), Strict()]


class Link(Commons):
    # https://github.com/radiantearth/stac-spec/blob/master/commons/links.md#link-object

    @classmethod
    def create(
        cls,
        *,
        href: URI,
        rel: Rel,
        type: MediaType | None = None,
        title: Title | None = None,
        description: Description | None = None,
        method: HttpMethod | None = None,
        headers: dict[ShortStr, LongishStr | list[LongishStr]] | None = None,
        body: BodyStr | JSONObject | None = None,
    ) -> Self:
        return cls.model_validate(
            {
                "href": href,
                "rel": rel,
                "type": type,
                "title": title,
                "description": description,
                "method": method,
                "headers": headers,
                "body": body,
            },
        )

    # REQUIRED. The actual link in the format of an URL. Relative and absolute links are both allowed.
    # Trailing slashes are significant.
    href: URI

    # REQUIRED. Relationship between the current document and the linked document.
    # See chapter "Relation types" for more information.
    # TODO "Link with relationship `self` must be absolute URI",
    rel: Rel

    # TODO: these are all optional -- allow or should they be?

    # Media type of the referenced entity.
    type: MediaType | None = None

    # A human readable title to be used in rendered displays of the link.
    title: Title | None = None

    # Description
    description: Description | None = None

    # The HTTP method that shall be used for the request to the target resource, in uppercase. GET by default
    method: HttpMethod | None = None

    # The HTTP headers to be sent for the request to the target resource.
    headers: dict[ShortStr, LongishStr | list[LongishStr]] | None = None

    # The HTTP body to be sent to the target resource.
    body: BodyStr | JSONObject | None = None

    # TODO:
    # validate   - deprecated: image/vnd.stac.geotiff and Cloud Optimized GeoTiffs used
    # image/vnd.stac.geotiff; profile=cloud-optimized.


type AssetRole = Annotated[str, StringConstraints(pattern=r"^[-a-zA-Z0-9]+$"), Strict()]
type ProviderRole = Annotated[str, StringConstraints(pattern=r"^[-a-zA-Z0-9]+$"), Strict()]


class NamelessAsset(StacBaseModel):
    # https://github.com/radiantearth/stac-spec/blob/master/commons/assets.md

    # REQUIRED. URI to the asset object. Relative and absolute URI are both allowed. Trailing slashes are significant.
    href: URI

    # The displayed title for clients and users.
    title: Title | None = None

    # A description of the Asset providing additional details, such as how it was processed or created. CommonMark 0.29
    # syntax MAY be used for rich text representation.
    description: Description | None = None

    # Media type of the asset. See the common media types in the best practice doc for commonly used asset types.
    type: MediaType | None = Field(alias="type", default=None)

    # The semantic roles of the asset, similar to the use of rel in links.
    roles: list[AssetRole] | None = None

    # "$ref": "common.json"

    @classmethod
    def from_an(cls, asset: "Asset") -> Self:
        return cls.model_validate(
            {
                "href": asset.href,
                "title": asset.title,
                "description": asset.description,
                "type": asset.type,
                "roles": asset.roles,
            },
        )

    # TODO : validate
    #   - bands https://github.com/radiantearth/stac-spec/blob/master/best-practices.md#bands
    #   - eo:bands and raster:bands -> bands


type AssetName = Annotated[str, StringConstraints(min_length=1, max_length=32, pattern=r"^[-_.a-zA-Z0-9]+$"), Strict()]


class Asset(NamelessAsset):
    name: AssetName

    @classmethod
    def create(
        cls,
        *,
        name: AssetName,
        href: URI,
        title: Title | None = None,
        description: Description | None = None,
        type: MediaType | None = None,
        roles: list[AssetRole] | None = None,  # ?
        **_kwargs: dict[str, Any],
    ) -> Self:
        return cls.model_validate(
            {
                "name": name,
                "href": href,
                "title": title,
                "description": description,
                "type": type,
                "roles": roles,
            },
        )


class Provider(BaseModel):
    # REQUIRED. The name of the organization or the individual.
    name: ShortStr

    # Multi-line description to add further provider information such as processing details for processors and
    # producers, hosting details for hosts or basic contact information. CommonMark 0.29 syntax MAY be used for
    # rich text representation.
    description: Description

    # Roles of the provider. Any of licensor, producer, processor or host.
    roles: list[ProviderRole]
    # role validation
    # The provider's role(s) can be one or more of the following elements:
    # licensor: The organization that is licensing the dataset under the license specified in the Collection's license
    #   field.
    # producer: The producer of the data is the provider that initially captured and processed the source data,
    #   e.g. ESA for Sentinel-2 data.
    # processor: A processor is any provider who processed data to a derived product.
    # host: The host is the actual provider offering the data on their storage. There should be no more than one host,
    #   specified as the last element of the provider list.

    # Homepage on which the provider describes the dataset and publishes contact information.
    url: URI


class Band(BaseModel):
    # The name of the band (e.g., "B01", "B8", "band2", "red"), which should be unique across all bands defined in the
    #   list of bands. This is typically the name the data provider uses for the band.
    name: ShortStr
    # string	Description to fully explain the band. CommonMark 0.29 syntax MAY be used for rich text representation.
    description: Description


class ItemExtension(StacBaseModel):
    _id: StacExtensionIdentifier = PrivateAttr("")

    @property
    def id(self) -> StacExtensionIdentifier:
        return self._id


class Item(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    _top_level: frozenset[str] = frozenset(
        {
            "type",
            "stac_version",
            "id",
            "geometry",
            "bbox",
            "links",
            "assets",
            "collection",
        }
    )

    _exclude: frozenset[str] = frozenset({"stac_extensions", "extensions"})

    @classmethod
    def create(
        cls,
        *,
        extensions: list[ItemExtension],
        id: ItemIdentifier,
        geometry: Polygon | MultiPolygon,
        bbox: BBox2d | BBox3d,
        links: list[Link],
        assets: list[Asset],
        collection: CollectionIdentifier | None,
        datetime: UtcDatetime | None,
        title: Title | None = None,
        description: Description | None = None,
        keywords: list[ShortStr] | None = None,
        roles: list[ShortStr] | None = None,
        start_datetime: UtcDatetime | None = None,
        end_datetime: UtcDatetime | None = None,
        created: UtcDatetime | None = None,
        updated: UtcDatetime | None = None,
        license: LicenseStr | None = None,
        providers: list[Provider] | None = None,
        platform: ShortStr | None = None,
        instruments: list[ShortStr] | None = None,
        constellation: ShortStr | None = None,
        mission: ShortStr | None = None,
        gsd: PositiveFloat | None = None,
        bands: list[Band] | None = None,
    ) -> "Item":
        return cls.model_validate(
            {
                "type": "Feature",
                "stac_version": "1.1.0",
                "stac_extensions": [],
                "id": id,
                "geometry": geometry,
                "bbox": bbox,
                "links": links,
                "assets": assets,
                "collection": collection,
                "datetime": datetime,
                "title": title,
                "description": description,
                "keywords": keywords,
                "roles": roles,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "created": created,
                "updated": updated,
                "license": license,
                "providers": providers,
                "platform": platform,
                "instruments": instruments,
                "constellation": constellation,
                "mission": mission,
                "gsd": gsd,
                "bands": bands,
                "extensions": extensions,
            },
        )

    @model_serializer(mode="wrap", when_used="json")
    def ser_model(self, nxt: SerializerFunctionWrapHandler, _info: SerializationInfo) -> dict[str, Any]:
        item = {k: v for k, v in self if k in self._top_level}
        if self.stac_extensions:
            item |= {"stac_extensions": self.stac_extensions}
        else:
            item |= {"stac_extensions": [x.id for x in self.extensions]}
        item["assets"] = {asset.name: NamelessAsset.from_an(asset) for asset in item["assets"]}

        properties: JSONObject = {}
        item["properties"] = properties
        properties |= {k: v for k, v in self if k not in self._top_level and k not in self._exclude}

        for ext in self.extensions:
            properties |= ext.model_dump(by_alias=True)

        return nxt(item)

    extensions: list[ItemExtension] = Field(default_factory=list)

    # REQUIRED. Type of the GeoJSON Object. MUST be set to Feature.
    type: Literal["Feature"]

    # REQUIRED. The STAC version the Item implements.
    # TODO: figure out how to support reading and writing differently?
    stac_version: Literal["1.1.0", "1.0.0"]

    # A list of extensions the Item implements.
    # -- unique and URI
    stac_extensions: list[StacExtensionIdentifier] = Field(default_factory=list)

    @field_validator("stac_extensions")
    @classmethod
    def validate_unique_stac_extensions(cls, v: list[StacExtensionIdentifier]) -> list[StacExtensionIdentifier]:
        if len(v) != len(set(v)):
            raise ValueError("stac_extensions must contain unique items")
        return v

    # REQUIRED. Provider identifier. The ID should be unique within the Collection that contains the Item.
    id: ItemIdentifier

    # REQUIRED. Defines the full footprint of the asset represented by this item, formatted according to
    # RFC 7946, section 3.1 if a geometry is provided or section 3.2 if no geometry is provided.
    # section 3.1: Geometry definitions and  section 3.2: null
    # -- GeometryCollection is disallowed, but no one uses the others either
    geometry: Polygon | MultiPolygon

    # REQUIRED if geometry is not null, prohibited if geometry is null. Bounding Box of the asset
    # represented by this Item, formatted according to RFC 7946, section 5.
    bbox: BBox2d | BBox3d

    @field_validator("bbox", mode="before")
    @classmethod
    def bbox_field_validator(cls, v: list[float] | BBox2d | BBox3d) -> BBox2d | BBox3d:
        if isinstance(v, list):
            match len(v):
                case 4:
                    return BBox2d(w_lon=v[0], s_lat=v[1], e_lon=v[2], n_lat=v[3])
                case 6:
                    return BBox3d(
                        w_lon=v[0],
                        s_lat=v[1],
                        bottom_elevation=v[2],
                        e_lon=v[3],
                        n_lat=v[4],
                        top_elevation=v[5],
                    )
                case _:
                    raise ValueError("BBox requires exactly 4 or 6 coordinates")
        return v

    # REQUIRED. List of link objects to resources and related URLs. See the best practices
    # https://github.com/radiantearth/stac-spec/blob/master/best-practices.md#use-of-links
    # for details on when the use self links is strongly recommended.
    links: list[Link]

    # REQUIRED. Dictionary of asset objects that can be downloaded, each with a unique key.
    # TODO: has an asset with `data`
    assets: list[Asset]

    @field_validator("assets", mode="before")
    @classmethod
    def transform_assets_dict_to_list(cls, v: list[dict[str, Any]] | dict[str, Any]) -> list[dict[str, Any]]:
        if isinstance(v, list):
            return v
        if isinstance(v, dict):
            for asset_name, asset in v.items():
                asset["name"] = asset_name
            return list(v.values())
        return v

    # The id of the STAC Collection this Item references to. This field is required if a
    # link with a collection relation type is present and is not allowed otherwise.
    # TODO - different than I expected!
    collection: CollectionIdentifier | None

    # Assets & Properties bands
    # If there is no asset with bands...
    #     ... then bands are not allowed in properties...
    #     ... otherwise bands are allowed in properties.

    # collection/c_link validator

    # -----------

    # REQUIRED. The searchable date and time of the assets, which must be in UTC.
    # It is formatted according to RFC 3339, section 5.6. null is allowed, but
    # requires start_datetime and end_datetime from common metadata to be set.
    # todo: consider collapsing into single and interval?
    datetime: UtcDatetime | None

    @model_validator(mode="before")
    @classmethod
    def populate_datetimes_from_properties(cls, data: dict[str, Any]) -> dict[str, Any]:
        for dt_type in ["datetime", "start_datetime", "end_datetime"]:
            if isinstance(data, dict) and (p := data.get("properties")) and (dt := p.pop(dt_type, None)):
                data[dt_type] = dt
        return data

    # todo: validate
    # datetime is not null or all three defined and s & e not null
    #                         "datetime",
    #                     "start_datetime",
    #                     "end_datetime"

    #############################################################################################
    ## Commons https://github.com/radiantearth/stac-spec/blob/master/commons/common-metadata.md #
    #############################################################################################

    # A human readable title describing the STAC entity.
    title: Title | None = None

    # Detailed multi-line description to fully explain the STAC entity. CommonMark 0.29 syntax MAY be used for rich
    # text representation.
    description: Description | None = None

    # List of keywords describing the STAC entity.
    keywords: list[ShortStr] | None = None

    # The semantic roles of the entity, e.g. for assets, links, providers, bands, etc.
    roles: list[ShortStr] | None = None

    # The first or start date and time for the resource, in UTC. It is formatted as date-time according to RFC 3339
    start_datetime: UtcDatetime | None = None

    # The last or end date and time for the resource, in UTC. It is formatted as date-time according to RFC 3339
    end_datetime: UtcDatetime | None = None

    # Creation date and time of the corresponding STAC entity or Asset (see below), in UTC.
    created: UtcDatetime | None = None

    # Date and time the corresponding STAC entity or Asset (see below) was updated last, in UTC.
    updated: UtcDatetime | None = None

    # License(s) of the data as SPDX License identifier, SPDX License expression, or "other" (see below).
    # various and proprietary are deprecated.
    # https://spdx.org/licenses/ identifier
    # https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/
    license: LicenseStr | None = None

    # Link relations valiations
    # commons: license The license URL(s) for the resource SHOULD be specified if the license field is
    # not a SPDX license identifier.

    # A list of providers, which may include all organizations capturing or processing the data or the hosting provider.
    # Providers should be listed in chronological order with the most recent provider being the last element of the list
    providers: list[Provider] | None = None

    # Unique name of the specific platform to which the instrument is attached. e.g., landsat-8
    # lower case
    platform: ShortStr | None = None

    # Name of instrument or sensor used (e.g., MODIS, ASTER, OLI, Canon F-1).
    # modis,
    instruments: list[ShortStr] | None = None  # todo: tighter and lc

    # Name of the constellation to which the platform belongs., e.g, sentinel-2
    constellation: ShortStr | None = None  # todo: tighter and lc

    # Name of the mission for which data is collected.
    mission: ShortStr | None = None  # todo: tighter and lc

    # Ground Sample Distance at the sensor, in meters (m), must be greater than 0.
    gsd: PositiveFloat | None = None  # maybe tighter? precision, can't be larger than the earth

    bands: list[Band] | None = None

    # Statistics of all the values.
    # statistics:	Statistics  TODO


class EOExtension(ItemExtension):
    _id: StacExtensionIdentifier = PrivateAttr("https://stac-extensions.github.io/eo/v2.0.0/schema.json")
    cloud_cover: Percentage | None = Field(alias="eo:cloud_cover", default=None)
    snow_cover: Percentage | None = Field(alias="eo:snow_cover", default=None)

    @classmethod
    def create(
        cls,
        *,
        cloud_cover: Percentage | None = None,
        snow_cover: Percentage | None = None,
    ) -> Self:
        return cls.model_validate(
            {
                "eo:cloud_cover": cloud_cover,
                "eo:snow_cover": snow_cover,
            }
        )


class ViewExtension(ItemExtension):
    _id: StacExtensionIdentifier = PrivateAttr("https://stac-extensions.github.io/view/v1.0.0/schema.json")

    # The angle from the sensor between nadir (straight down) and the scene center. Measured in degrees (0-90).
    off_nadir: ZeroTo90 | None = Field(alias="view:off_nadir", default=None)

    # The incidence angle is the angle between the vertical (normal) to the intercepting surface and the line of sight
    # back to the satellite at the scene center. Measured in degrees (0-90).
    incidence_angle: ZeroTo90 | None = Field(alias="view:incidence_angle", default=None)

    # Viewing azimuth angle. The angle measured from the sub-satellite point (point on the ground below the platform)
    # between the scene center and true north. Measured clockwise from north in degrees (0-360).
    azimuth: ZeroTo360 | None = Field(alias="view:azimuth", default=None)

    # Sun azimuth angle. From the scene center point on the ground, this is the angle between truth north and the sun.
    # Measured clockwise in degrees (0-360).
    sun_azimuth: ZeroTo360 | None = Field(alias="view:sun_azimuth", default=None)

    # Sun elevation angle. The angle from the tangent of the scene center point to the sun. Measured from the horizon
    # in degrees (-90-90). Negative values indicate the sun is below the horizon, e.g. sun elevation of -10° means the
    # data was captured during nautical twilight.
    sun_elevation: Negative90To90 | None = Field(alias="view:sun_elevation", default=None)

    @classmethod
    def create(
        cls,
        *,
        off_nadir: ZeroTo90 | None = None,
        incidence_angle: ZeroTo90 | None = None,
        azimuth: ZeroTo360 | None = None,
        sun_azimuth: ZeroTo360 | None = None,
        sun_elevation: Negative90To90 | None = None,
    ) -> Self:
        return cls.model_validate(
            {
                "view:off_nadir": off_nadir,
                "view:incidence_angle": incidence_angle,
                "view:azimuth": azimuth,
                "view:sun_azimuth": sun_azimuth,
                "view:sun_elevation": sun_elevation,
            }
        )
