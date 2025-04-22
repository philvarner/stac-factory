from pydantic import ValidationError
import pytest
from phil_stac.models import BBox, BBox2d, Item, Lat, Lon, Polygon


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


def test_item() -> None:
    Item.model_validate(
        {
            "type": "Feature",
            "stac_version": "1.1.0",
            "id": "S2B_T38XNF_20250422T091553_L2A",
            "stac_extensions": [
                "https://stac-extensions.github.io/eo/v1.1.0/schema.json",
                "https://stac-extensions.github.io/file/v2.1.0/schema.json",
                "https://stac-extensions.github.io/grid/v1.1.0/schema.json",
                "https://stac-extensions.github.io/mgrs/v1.0.0/schema.json",
                "https://stac-extensions.github.io/processing/v1.1.0/schema.json",
                "https://stac-extensions.github.io/projection/v1.1.0/schema.json",
                "https://stac-extensions.github.io/raster/v1.1.0/schema.json",
                "https://stac-extensions.github.io/sentinel-2/v1.0.0/schema.json",
                "https://stac-extensions.github.io/storage/v1.0.0/schema.json",
                "https://stac-extensions.github.io/view/v1.0.0/schema.json",
            ],
            "collection": "sentinel-2-c1-l2a",
        }
    )
