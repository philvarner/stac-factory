from enum import Enum, IntEnum
from typing import Annotated, Any, Literal, NamedTuple
from annotated_types import Ge, Le
from typing import Annotated
import re
from pydantic import StringConstraints
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_serializer,
    model_validator,
)


type Identifier = Annotated[str, StringConstraints(pattern=r"^[-_.a-zA-Z0-9]+$")]
type StacExtensionIdentifier = Annotated[
    str, StringConstraints(pattern=r"^[-_.:/a-zA-Z0-9]+$")
]

type ItemIdentifier = Identifier
type CollectionIdentifier = Identifier

# float or decimal? Decimal, and add a configuration for how many points


class Accuracy(Enum):
    # | Decimal Places | Degrees      | Distance  |
    # |---------------|--------------|-----------|
    # | 0             | 1.0          | 111 km    |
    # | 1             | 0.1          | 11.1 km   |
    # | 2             | 0.01         | 1.11 km   |
    # | 3             | 0.001        | 111 m     |
    # | 4             | 0.0001       | 11.1 m    |
    # | 5             | 0.00001      | 1.11 m    |
    # | 6             | 0.000001     | 111 mm    |
    # | 7             | 0.0000001    | 11.1 mm   |
    # | 8             | 0.00000001   | 1.11 mm   |

    # in meters
    _0_00111 = 8
    _0_0111 = 7
    _0_111 = 6
    _1_11 = 5
    _11_1 = 4
    _111 = 3
    _1110 = 2
    _11100 = 1
    _111000 = 0


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

    model_config = ConfigDict(extra="forbid")


class BBox3d(BBox2d):
    top_elevation: Elevation
    bottom_elevation: Elevation

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


type BBox = BBox2d | BBox3d

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
type MultiPolygonCoordinates = Annotated[
    list[PolygonCoordinates], Field(min_length=1, max_length=2)
]


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

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_bbox(cls, bbox: BBox) -> "Polygon":
        return cls(
            type="Polygon",
            coordinates=[
                [
                    Position2D(bbox.w_lon, bbox.s_lat),
                    Position2D(bbox.e_lon, bbox.s_lat),
                    Position2D(bbox.e_lon, bbox.n_lat),
                    Position2D(bbox.w_lon, bbox.n_lat),
                    Position2D(bbox.w_lon, bbox.s_lat),
                ]
            ],
        )

    model_config = ConfigDict(extra="forbid")


class MultiPolygon(BaseModel):
    type: Literal["MultiPolygon"]
    coordinates: MultiPolygonCoordinates

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    #     @field_validator("coordinates")
    #     def check_closure(cls, coordinates: List) -> List:
    #         """Validate that Polygon is closed (first and last coordinate are the same)."""
    #         if any(ring[-1] != ring[0] for polygon in coordinates for ring in polygon):
    #             raise ValueError("All linear rings have the same start and end coordinates")

    #         return coordinates

    model_config = ConfigDict(extra="forbid")


class Link(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Asset(BaseModel):
    model_config = ConfigDict(extra="forbid")


type ItemProperties = dict[str, Any]
# datetime validation

type Assets = dict[str, Asset]
type Links = list[Link]


class Item(BaseModel):  # , Generic[Geom, Props]):
    type: Literal["Feature"]
    stac_version: Literal["1.1.0"]
    stac_extensions: list[StacExtensionIdentifier] = []
    id: ItemIdentifier
    collection: CollectionIdentifier

    # bbox: BBox
    # geometry: Polygon | MultiPolygon

    # properties: ItemProperties

    # assets: Assets

    # links: Links

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    # collection/c_link validator

    model_config = ConfigDict(extra="forbid")


# class ItemWithoutCollection(Item):
#     collection: Identifier | None
#     bbox: BBox | None
#     geometry: Polygon | MultiPolygon | None

#     model_config = ConfigDict(extra="forbid")
