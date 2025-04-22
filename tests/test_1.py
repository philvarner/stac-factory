from pydantic import ValidationError
import pytest
from phil_stac.models import BBox, BBox2d, Lat, Lon, Polygon


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
