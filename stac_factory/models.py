from collections.abc import Mapping
from datetime import timezone
from typing import Annotated, Any, Literal, NamedTuple, Protocol, Self, TypedDict

from annotated_types import Ge, Le
from pydantic import (
    AfterValidator,
    AnyUrl,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
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


type Lat = Annotated[float, Ge(-90.0), Le(90)]
type Lon = Annotated[float, Ge(-180.0), Le(180)]
type Elevation = Annotated[float, Ge(-10_000_000.0), Le(10_000_000.0)]


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


class Polygon(BaseModel):
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

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)


class MultiPolygon(BaseModel):
    type: Literal["MultiPolygon"]
    coordinates: MultiPolygonCoordinates

    #     #     @field_validator("coordinates")
    #     #     def check_closure(cls, coordinates: List) -> List:
    #     #         """Validate that Polygon is closed (first and last coordinate are the same)."""
    #     #         if any(ring[-1] != ring[0] for polygon in coordinates for ring in polygon):
    #     #             raise ValueError("All linear rings have the same start and end coordinates")

    #     #         return coordinates

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)


class BBox2d(BaseModel):
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

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)


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


class ItemProperties(TypedDict): ...


type URI = AnyUrl


# Media type regex based on RFC 6838 syntax
type MediaType = Annotated[
    str,
    StringConstraints(pattern=r"^[a-zA-Z0-9][-a-zA-Z0-9.+]*/[a-zA-Z0-9][-a-zA-Z0-9.+]*(?:;.*)?$"),
    Strict(),
]

type Title = Annotated[str, StringConstraints(min_length=1, max_length=100), Strict()]
type Description = Annotated[str, StringConstraints(min_length=1, max_length=10000), Strict()]


class StacElement(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)


class Commons(StacElement): ...


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
        # TODO: description?
        method: HttpMethod | None = None,
        headers: dict[str, str | list[str]] | None = None,  # todo: strs
        body: BodyStr | JSONObject | None = None,
    ) -> Self:
        return cls.model_validate(
            {
                "href": href,
                "rel": rel,
                "type": type,
                "title": title,
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

    # The HTTP method that shall be used for the request to the target resource, in uppercase. GET by default
    method: HttpMethod | None = None

    # The HTTP headers to be sent for the request to the target resource.
    headers: dict[str, str | list[str]] | None = None  # todo: strs

    # The HTTP body to be sent to the target resource.
    body: BodyStr | JSONObject | None = None

    # TODO:
    # validate   - deprecated: image/vnd.stac.geotiff and Cloud Optimized GeoTiffs used
    # image/vnd.stac.geotiff; profile=cloud-optimized.


type Role = Annotated[str, StringConstraints(pattern=r"^[-a-zA-Z0-9]+$"), Strict()]


class NamelessAsset(BaseModel):
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
    roles: list[Role] | None = None

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
    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)


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
        roles: list[Role] | None = None,  # ?
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

    @classmethod
    def named(
        cls,
        *,
        name: AssetName,
        asset: Mapping[str, Any],
    ) -> Self:
        return cls.create(name=name, **asset)

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)


class ItemExtension(Protocol):
    def apply(self, item: "Item") -> "Item":
        return item


class Item(BaseModel):  # , Generic[Geom, Props]):
    @classmethod
    def create(
        cls,
        *extensions: ItemExtension,
        stac_extensions: list[StacExtensionIdentifier],
        id: ItemIdentifier,
        geometry: Polygon | MultiPolygon,
        bbox: BBox2d | BBox3d,
        links: list[Link],
        assets: list[Asset],
        properties: ItemProperties,
        collection: CollectionIdentifier | None,
        datetime: UtcDatetime,
        # **properties: Unpack[ItemProperties],
    ) -> "Item":
        x = cls.model_validate(
            {
                "type": "Feature",
                "stac_version": "1.1.0",
                "stac_extensions": stac_extensions,
                "id": id,
                "geometry": geometry,
                "bbox": bbox,
                "properties": properties,
                "links": links,
                "assets": assets,
                "collection": collection,
                "datetime": datetime,
            },
        )

        for extension in extensions:
            x = extension.apply(x)

        return x

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
    def transform_assets_dict_to_list(cls, v: list[Asset] | dict[str, Asset]) -> list[Asset]:
        if isinstance(v, list):
            return v
        if isinstance(v, dict):
            for asset_name, asset in v.items():
                asset.name = asset_name
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

    properties: ItemProperties

    # REQUIRED. The searchable date and time of the assets, which must be in UTC.
    # It is formatted according to RFC 3339, section 5.6. null is allowed, but
    # requires start_datetime and end_datetime from common metadata to be set.
    # todo: consider collapsing into single and interval?
    datetime: UtcDatetime | None
    start_datetime: UtcDatetime | None = None
    end_datetime: UtcDatetime | None = None

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

    _top_level: frozenset[str] = frozenset(
        {
            "type",
            "stac_version",
            "stac_extensions",
            "id",
            "geometry",
            "bbox",
            "links",
            "assets",
            "collection",
        }
    )

    @model_serializer(mode="wrap", when_used="json")
    def ser_model(self, nxt: SerializerFunctionWrapHandler, _info: SerializationInfo) -> dict[str, Any]:
        item_dict = {k: v for k, v in self if k in self._top_level}
        props_dict = {k: v for k, v in self if k not in self._top_level | {"properties"}}
        item_dict["assets"] = {asset.name: NamelessAsset.from_an(asset) for asset in item_dict["assets"]}

        return nxt(item_dict | {"properties": props_dict})

    model_config = ConfigDict(extra="ignore", frozen=True)


# https://github.com/radiantearth/stac-spec/blob/master/commons/common-metadata.md
class Common(BaseModel): ...


class Basics(Common):
    # A human readable title describing the STAC entity.
    title: Title

    # Detailed multi-line description to fully explain the STAC entity. CommonMark 0.29 syntax MAY be used for rich
    # text representation.
    description: Description

    # List of keywords describing the STAC entity.
    keywords: list[ShortStr]

    # The semantic roles of the entity, e.g. for assets, links, providers, bands, etc.
    roles: list[ShortStr]


class DateAndTime(Common):
    # Creation date and time of the corresponding STAC entity or Asset (see below), in UTC.
    created: UtcDatetime

    # Date and time the corresponding STAC entity or Asset (see below) was updated last, in UTC.
    updated: UtcDatetime

    # created and updated have different meaning depending on where they are used. If those fields are available in
    # a Collection, in a Catalog (both top-level), or in a Item (in the properties), the fields refer the metadata
    # (e.g., when the STAC metadata was created). Having those fields in the Assets or Links, they refer to the actual
    # data linked to (e.g., when the asset was created).

    # The first or start date and time for the resource, in UTC. It is formatted as date-time according to RFC 3339,
    # section 5.6.
    start_datetime: UtcDatetime

    # The last or end date and time for the resource, in UTC. It is formatted as date-time according to RFC 3339,
    # section 5.6.
    end_datetime: UtcDatetime


class SomethingElse(Common):
    # License(s) of the data as SPDX License identifier, SPDX License expression, or other (see below).
    license: LicenseStr

    # to be continued...
