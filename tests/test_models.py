import json

from pathlib import Path

import pytest

from pydantic import ValidationError

from stac_factory.constants import AssetRole, HttpMethod, LinkRelation, MediaType
from stac_factory.models import Asset, BBox2d, BBox3d, Item, Link, Polygon


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


def test_bbox3d_item() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "minimal.json").read_text())
    item_dict["bbox"] = [47.014448, 72.738194, 0, 48.35946, 72.985776, 100]
    Item.model_validate(item_dict)


def test_item_with_invalid_bbox() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "minimal.json").read_text())
    item_dict["bbox"].append("0")
    with pytest.raises(ValidationError, match="BBox requires exactly 4 or 6 coordinates"):
        Item.model_validate(item_dict)


def test_minimal_item() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "minimal.json").read_text())
    Item.model_validate(item_dict)


def test_item_with_null_bbox() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "minimal.json").read_text())
    item_dict["bbox"] = None
    with pytest.raises(ValidationError) as e:
        Item.model_validate(item_dict)
    assert "Input should be a valid dictionary or instance of BBox2d" in str(e.value)
    assert "Input should be a valid dictionary or instance of BBox3d" in str(e.value)


def test_inprogress_item() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "inprogress.json").read_text())
    Item.model_validate(item_dict)


# @pytest.mark.xfail(reason="failing because has elements that are not supported")
def test_typical() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "typical.json").read_text())
    Item.model_validate(item_dict)


# @pytest.mark.xfail(reason="failing because has elements that are not supported")
def test_sentinel_2_item() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "S2B_T38XNF_20250422T091553_L2A.json").read_text())
    Item.model_validate(item_dict)


def test_minimal_item_obj() -> None:
    Item.create(
        stac_extensions=[],
        id="minimal-item",
        geometry={
            "type": "Polygon",
            "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]],
        },
        bbox=[100, 0, 101, 1],
        assets={},
        links=[],
        datetime="2021-01-01T00:00:00Z",
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


def test_duplicate_stac_extensions() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "minimal.json").read_text())
    item_dict["stac_extensions"] = ["same", "same"]
    with pytest.raises(ValidationError, match="stac_extensions must contain unique items"):
        Item.model_validate(item_dict)


def test_asset_create() -> None:
    Asset.create(
        href="https://api.example.com/x.json",
        title="an item",
        description="an item description",
        type=MediaType.JSON,
        roles=[AssetRole.data],
    )
