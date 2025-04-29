import json

from pathlib import Path

import pytest

from pydantic import ValidationError

from stac_factory.constants import AssetRole, HttpMethod, LinkRelation, MediaType
from stac_factory.models import Asset, Item, Link


def test_item_with_bbox3d() -> None:
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


def test_item_minimal() -> None:
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


def test_item_inprogress() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "inprogress.json").read_text())
    Item.model_validate(item_dict)


# @pytest.mark.xfail(reason="failing because has elements that are not supported")
def test_item_typical() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "typical.json").read_text())
    Item.model_validate(item_dict)


# @pytest.mark.xfail(reason="failing because has elements that are not supported")
def test_item_sentinel_2() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "S2B_T38XNF_20250422T091553_L2A.json").read_text())
    Item.model_validate(item_dict)


def test_item_create_minimal() -> None:
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


def test_item_create_typical() -> None:
    Item.create(
        stac_extensions=["https://stac-extensions.github.io/eo/v2.0.0/schema.json"],
        id="normal-item-1",
        geometry={
            "type": "Polygon",
            "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]],
        },
        bbox=[100, 0, 101, 1],
        assets={
            "asset1": Asset.create(
                href="https://api.example.com/x.json",
                title="an item",
                description="an item description",
                type=MediaType.JSON,
                roles=[AssetRole.data],
            ),
        },
        links=[
            Link.create(
                href="https://api.example.com/x.json",
                rel=LinkRelation.canonical,
                type=MediaType.JSON,
                title="an item",
                method=HttpMethod.GET,
                headers=None,
                body=None,
            ),
        ],
        datetime="2021-01-01T00:00:00Z",
    )


def test_item_with_duplicate_stac_extensions() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "minimal.json").read_text())
    item_dict["stac_extensions"] = ["same", "same"]
    with pytest.raises(ValidationError, match="stac_extensions must contain unique items"):
        Item.model_validate(item_dict)


# def test_json_schema() -> None:
#     fixture_dir = Path(__file__).parent.absolute() / "fixtures"
#     Path(fixture_dir / "schema.json").write_text(json.dumps(Item.model_json_schema(), indent=2))
