import json
from pathlib import Path
from pydantic import ValidationError
import pytest
from stac_factory.models import BBox2d, Item, Polygon


def test_1() -> None:
    bbox = BBox2d(w_lon=-150, s_lat=40, e_lon=-148, n_lat=42)

    assert bbox.w_lon == -150
    assert bbox.s_lat == 40
    assert bbox.e_lon == -148
    assert bbox.n_lat == 42

    assert bbox.model_dump(mode="json") == [-150, 40, -148, 42]


def test_2() -> None:
    with pytest.raises(ValidationError):
        BBox2d(w_lon=-150, s_lat=40, e_lon=-148, n_lat=38)


def test_polygon() -> None:
    Polygon.model_validate(
        {
            "type": "Polygon",
            "coordinates": [
                [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]
            ],
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


def test_inprogress_item() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "inprogress.json").read_text())
    Item.model_validate(item_dict)


@pytest.mark.skip(reason="failing because has elements that are not supported")
def test_typical() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "typical.json").read_text())
    Item.model_validate(item_dict)
