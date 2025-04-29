import pytest

from pydantic import ValidationError

from stac_factory.constants import AssetRole, HttpMethod, LinkRelation, MediaType
from stac_factory.models import Asset, BBox2d, BBox3d, Link, Polygon


def test_bbox2d() -> None:
    bbox = BBox2d(w_lon=-150, s_lat=40, e_lon=-148, n_lat=42)

    assert bbox.w_lon == -150
    assert bbox.s_lat == 40
    assert bbox.e_lon == -148
    assert bbox.n_lat == 42

    assert bbox.model_dump(mode="json") == [-150, 40, -148, 42]


def test_bbox2d_with_inverted_latitude() -> None:
    with pytest.raises(ValidationError, match="South latitude must be less than or equal to north latitude"):
        BBox2d(w_lon=0, e_lon=1, s_lat=1, n_lat=0)


def test_bbox3d() -> None:
    bbox = BBox3d(
        w_lon=-150,
        s_lat=40,
        bottom_elevation=-1,
        e_lon=-148,
        n_lat=42,
        top_elevation=1000,
    )
    assert bbox.w_lon == -150
    assert bbox.s_lat == 40
    assert bbox.bottom_elevation == -1
    assert bbox.e_lon == -148
    assert bbox.n_lat == 42
    assert bbox.top_elevation == 1000

    assert bbox.model_dump(mode="json") == [-150, 40, -1, -148, 42, 1000]


def test_bbox3d_with_inverted_elevation() -> None:
    with pytest.raises(ValidationError, match="Bottom elevation is above top elevation"):
        BBox3d(w_lon=0, e_lon=1, s_lat=0, n_lat=1, bottom_elevation=1, top_elevation=0)


def test_polygon() -> None:
    Polygon.model_validate(
        {
            "type": "Polygon",
            "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]],
        }
    )


def test_polygon_with_holes_raises() -> None:
    with pytest.raises(ValidationError):
        Polygon.model_validate(
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [100.0, 0.0],
                        [101.0, 0.0],
                        [101.0, 1.0],
                        [100.0, 1.0],
                        [100.0, 0.0],
                    ],
                    [
                        [100.8, 0.8],
                        [100.8, 0.2],
                        [100.2, 0.2],
                        [100.2, 0.8],
                        [100.8, 0.8],
                    ],
                ],
            }
        )


def test_asset_create() -> None:
    Asset.create(
        href="https://api.example.com/x.json",
        title="an item",
        description="an item description",
        type=MediaType.JSON,
        roles=[AssetRole.data],
    )


def test_link_create() -> None:
    Link.create(
        href="https://api.example.com/x.json",
        rel=LinkRelation.canonical,
        type=MediaType.JSON,
        title="an item",
        method=HttpMethod.GET,
        headers=None,
        body=None,
    )
