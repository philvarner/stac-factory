from datetime import timezone
from enum import Enum
from typing import Annotated, Any, Literal, NamedTuple, TypedDict
from annotated_types import Ge, Le
from typing import Annotated
from pydantic import Strict, StringConstraints, field_validator
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_serializer,
    model_validator,
    AfterValidator,
    AwareDatetime,
)

# STAC Item spec: https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md
# GeoJSON spec: https://datatracker.ietf.org/doc/html/rfc7946

type Identifier = Annotated[
    str, StringConstraints(pattern=r"^[-_.a-zA-Z0-9]+$"), Strict()
]
type StacExtensionIdentifier = Annotated[
    str, StringConstraints(pattern=r"^[-_.:/a-zA-Z0-9]+$")  # todo: URI
]

type ItemIdentifier = Identifier
type CollectionIdentifier = Identifier

type UtcDatetime = Annotated[
    AwareDatetime,
    AfterValidator(lambda d: d.astimezone(timezone.utc)),
]

# float or decimal? Decimal, and add a configuration for how many points

type Lat = Annotated[float, Ge(-90.0), Le(90)]
type Lon = Annotated[float, Ge(-180.0), Le(180)]
type Elevation = Annotated[float, Ge(-10_000_000.0), Le(10_000_000.0)]


class BBox2d(BaseModel):
    # [sw_lon, sw_lat, ne_lon, ne_lat]
    w_lon: Lon
    s_lat: Lat
    e_lon: Lon
    n_lat: Lat

    @model_validator(mode="after")
    def validate_relative_latitudes(self):
        if self.s_lat > self.n_lat:
            raise ValueError(
                "South latitude must be less than or equal to north latitude"
            )
        return self

    @model_serializer
    def ser_model(self) -> list[float]:
        return [self.w_lon, self.s_lat, self.e_lon, self.n_lat]

    # todo: loader for array

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class BBox3d(BBox2d):
    bottom_elevation: Elevation
    top_elevation: Elevation

    @model_validator(mode="after")
    def validate_relative_elevations(self):
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


Position2D = NamedTuple("Position2D", [("longitude", Lon), ("latitude", Lat)])
Position3D = NamedTuple(
    "Position3D", [("longitude", Lon), ("latitude", Lat), ("elevation", Elevation)]
)
type Position = Position2D | Position3D

type LinearRingCoordinates = Annotated[
    list[Position], Field(min_length=4, max_length=512)
]
type PolygonCoordinates = Annotated[
    list[LinearRingCoordinates], Field(min_length=1, max_length=1)
]
# type MultiPolygonCoordinates = Annotated[
#     list[PolygonCoordinates], Field(min_length=1, max_length=2)
# ]


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

    # @property
    # def __geo_interface__(self) -> dict[str, Any]:
    #     return self.model_dump(mode="json")

    # @classmethod
    # def from_bbox(cls, bbox: BBox2d | BBox3d) -> "Polygon":
    #     return cls(
    #         type="Polygon",
    #         coordinates=[
    #             [
    #                 Position2D(bbox.w_lon, bbox.s_lat),
    #                 Position2D(bbox.e_lon, bbox.s_lat),
    #                 Position2D(bbox.e_lon, bbox.n_lat),
    #                 Position2D(bbox.w_lon, bbox.n_lat),
    #                 Position2D(bbox.w_lon, bbox.s_lat),
    #             ]
    #         ],
    #     )

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class Link(BaseModel):
    # https://github.com/radiantearth/stac-spec/blob/master/commons/links.md#link-object
    #      "rel", required
    # "href" required
    # "type":
    #             "title": {
    #             "method": {
    #             "headers": string or array of string
    #             "body": any type
    # self must be a uri

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class Asset(BaseModel):
    #  "href": {  "type": "string"
    #             "title": {  "type": "string"
    #             "description": {  "type": "string"
    #             "type": {  "type": "string"
    #             "roles": { #               "type": "array", #                 "type": "string"

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class ItemProperties(TypedDict):
    # REQUIRED. The searchable date and time of the assets, which must be in UTC.
    # It is formatted according to RFC 3339, section 5.6. null is allowed, but
    # requires start_datetime and end_datetime from common metadata to be set.
    datetime: UtcDatetime  # todo: validate

    # datetime is not null or all three defined and s & e not null
    #                         "datetime",
    #                     "start_datetime",
    #                     "end_datetime"
    # must be utc


type Assets = dict[str, Asset]
# https://github.com/radiantearth/stac-spec/blob/master/commons/assets.md


type Links = list[Link]


class Item(BaseModel):  # , Generic[Geom, Props]):
    # REQUIRED. Type of the GeoJSON Object. MUST be set to Feature.
    type: Literal["Feature"]

    # REQUIRED. The STAC version the Item implements.
    stac_version: Literal["1.1.0"]

    # A list of extensions the Item implements.
    # -- unique and URI
    stac_extensions: list[StacExtensionIdentifier] = Field(default_factory=list)

    # REQUIRED. Provider identifier. The ID should be unique within the Collection that contains the Item.
    id: ItemIdentifier

    # REQUIRED. Defines the full footprint of the asset represented by this item, formatted according to
    # RFC 7946, section 3.1 if a geometry is provided or section 3.2 if no geometry is provided.
    # section 3.1: Geometry definitions and  section 3.2: null
    # -- GeometryCollection is disallowed, but no one uses the others either
    geometry: Polygon  # | MultiPolygon

    # REQUIRED if geometry is not null, prohibited if geometry is null. Bounding Box of the asset
    # represented by this Item, formatted according to RFC 7946, section 5.
    bbox: BBox2d | BBox3d

    # REQUIRED. A dictionary of additional metadata for the Item.
    properties: ItemProperties

    # REQUIRED. List of link objects to resources and related URLs. See the best practices
    # https://github.com/radiantearth/stac-spec/blob/master/best-practices.md#use-of-links
    # for details on when the use self links is strongly recommended.
    links: Links

    # REQUIRED. Dictionary of asset objects that can be downloaded, each with a unique key.
    assets: Assets

    # The id of the STAC Collection this Item references to. This field is required if a
    # link with a collection relation type is present and is not allowed otherwise.
    # TODO - different than I expected!
    collection: CollectionIdentifier | None = None

    @field_validator("bbox", mode="before")
    @classmethod
    def bbox_field_validator(cls, v: list[float]) -> BBox2d | BBox3d:
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

    # Assets & Properties bands
    # If there is no asset with bands...
    #     ... then bands are not allowed in properties...
    #     ... otherwise bands are allowed in properties.

    # @property
    # def __geo_interface__(self) -> dict[str, Any]:
    #     return self.model_dump(mode="json")

    # collection/c_link validator

    model_config = ConfigDict(extra="forbid", frozen=True)
