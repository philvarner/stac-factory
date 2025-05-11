import json

from pathlib import Path

import pystac
import pystac.utils
import pytest

from pydantic import ValidationError

from stac_factory.constants import AssetRole, HttpMethod, LinkRelation, MediaType
from stac_factory.models import Asset, EOExtension, Item, Link, ViewExtension


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
    item = Item.model_validate(item_dict)

    assert item.model_dump(mode="json") == {
        "assets": {
            "aot": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/AOT.tif",
                "roles": [
                    "data",
                ],
                "title": "Aerosol optical thickness (AOT)",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "blue": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B02.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "Blue - 10m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "cloud": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/CLD_20m.tif",
                "roles": [
                    "data",
                    "cloud",
                ],
                "title": "Cloud Probabilities",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "coastal": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B01.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "Coastal - 60m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "granule_metadata": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/metadata.xml",
                "roles": [
                    "metadata",
                ],
                "title": None,
                "type": "application/xml",
            },
            "green": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B03.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "Green - 10m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "nir": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B08.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "NIR 1 - 10m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "nir08": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B8A.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "NIR 2 - 20m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "nir09": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B09.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "NIR 3 - 60m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "preview": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/L2A_PVI.tif",
                "roles": [
                    "overview",
                ],
                "title": "True color preview",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "product_metadata": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/product_metadata.xml",
                "roles": [
                    "metadata",
                ],
                "title": None,
                "type": "application/xml",
            },
            "red": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B04.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "Red - 10m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "rededge1": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B05.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "Red Edge 1 - 20m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "rededge2": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B06.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "Red Edge 2 - 20m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "rededge3": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B07.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "Red Edge 3 - 20m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "scl": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/SCL.tif",
                "roles": [
                    "data",
                ],
                "title": "Scene classification map (SCL)",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "snow": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/SNW_20m.tif",
                "roles": [
                    "data",
                    "snow-ice",
                ],
                "title": "Snow Probabilities",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "swir16": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B11.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "SWIR 1.6μm - 20m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "swir22": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/B12.tif",
                "roles": [
                    "data",
                    "reflectance",
                ],
                "title": "SWIR 2.2μm - 20m",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "thumbnail": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/L2A_PVI.jpg",
                "roles": [
                    "thumbnail",
                ],
                "title": "Thumbnail of preview image",
                "type": "image/jpeg",
            },
            "tileinfo_metadata": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/tileInfo.json",
                "roles": [
                    "metadata",
                ],
                "title": None,
                "type": "application/json",
            },
            "visual": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/TCI.tif",
                "roles": [
                    "visual",
                ],
                "title": "True color image",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
            "wvp": {
                "description": None,
                "href": "https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/WVP.tif",
                "roles": [
                    "data",
                ],
                "title": "Water Vapour (WVP)",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            },
        },
        "bbox": [
            47.014448,
            72.738194,
            48.35946,
            72.985776,
        ],
        "collection": "sentinel-2-c1-l2a",
        "geometry": {
            "coordinates": [
                [
                    [
                        47.014447961653765,
                        72.98577616786422,
                    ],
                    [
                        48.31602812874022,
                        72.73819381414839,
                    ],
                    [
                        48.35945964281699,
                        72.96809534281054,
                    ],
                    [
                        47.014447961653765,
                        72.98577616786422,
                    ],
                ],
            ],
            "type": "Polygon",
        },
        "id": "S2B_T38XNF_20250422T091553_L2A",
        "links": [
            {
                "body": None,
                "description": None,
                "headers": None,
                "href": "https://earth-search.aws.element84.com/v1/collections/sentinel-2-c1-l2a/items/S2B_T38XNF_20250422T091553_L2A",
                "method": None,
                "rel": "self",
                "title": None,
                "type": "application/geo+json",
            },
            {
                "body": None,
                "description": None,
                "headers": None,
                "href": "s3://e84-earth-search-sentinel-data/sentinel-2-c1-l2a/38/X/NF/2025/4/S2B_T38XNF_20250422T091553_L2A/S2B_T38XNF_20250422T091553_L2A.json",
                "method": None,
                "rel": "canonical",
                "title": None,
                "type": "application/json",
            },
            {
                "body": None,
                "description": None,
                "headers": None,
                "href": "s3://sentinel-s2-l2a/tiles/38/X/NF/2025/4/22/0/metadata.xml",
                "method": None,
                "rel": "via",
                "title": "Granule Metadata in Sinergize RODA Archive",
                "type": "application/xml",
            },
            {
                "body": None,
                "description": None,
                "headers": None,
                "href": "https://earth-search.aws.element84.com/v1/collections/sentinel-2-c1-l2a",
                "method": None,
                "rel": "parent",
                "title": None,
                "type": "application/json",
            },
            {
                "body": None,
                "description": None,
                "headers": None,
                "href": "https://earth-search.aws.element84.com/v1/collections/sentinel-2-c1-l2a",
                "method": None,
                "rel": "collection",
                "title": None,
                "type": "application/json",
            },
            {
                "body": None,
                "description": None,
                "headers": None,
                "href": "https://earth-search.aws.element84.com/v1",
                "method": None,
                "rel": "root",
                "title": None,
                "type": "application/json",
            },
            {
                "body": None,
                "description": None,
                "headers": None,
                "href": "https://earth-search.aws.element84.com/v1/collections/sentinel-2-c1-l2a/items/S2B_T38XNF_20250422T091553_L2A/thumbnail",
                "method": None,
                "rel": "thumbnail",
                "title": None,
                "type": None,
            },
        ],
        "properties": {
            "datetime": "2025-04-22T09:19:42.556000Z",
            "end_datetime": None,
            "start_datetime": None,
            "bands": None,
            "constellation": None,
            "created": None,
            "description": None,
            "gsd": None,
            "instruments": None,
            "keywords": None,
            "license": None,
            "mission": None,
            "platform": None,
            "providers": None,
            "roles": None,
            "title": None,
            "updated": None,
        },
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
        "stac_version": "1.1.0",
        "type": "Feature",
    }


def test_item_sentinel_2_multipolygon() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "S2B_T01WCR_20250427T000611_L2A.json").read_text())
    Item.model_validate(item_dict)


def test_item_create_minimal() -> None:
    Item.create(
        extensions=[],
        id="minimal-item",
        geometry={
            "type": "Polygon",
            "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]],
        },
        bbox=[100, 0, 101, 1],
        assets=[],
        links=[],
        datetime="2021-01-01T00:00:00Z",
        collection=None,
    )


def test_item_create_minimal_mp() -> None:
    Item.create(
        extensions=[],
        id="minimal-item",
        geometry={
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [180, 68.4858038539966],
                        [178.11849452315352, 68.44150171742469],
                        [178.32076050993456, 67.46099994484686],
                        [180, 67.50167854411256],
                        [180, 68.4858038539966],
                    ]
                ],
                [
                    [
                        [-179.20556042231803, 68.49813373282021],
                        [-180, 68.4858038540324],
                        [-180, 67.50167854415058],
                        [-179.31735654435366, 67.51320396474968],
                        [-179.12603876314654, 67.65097850440162],
                        [-179.20556042231803, 68.49813373282021],
                    ]
                ],
            ],
        },
        bbox=[100, 0, 101, 1],
        assets=[],
        links=[],
        datetime="2021-01-01T00:00:00Z",
        collection=None,
    )


def test_item_create_typical() -> None:
    item = Item.create(
        id="normal-item-1",
        collection=None,
        geometry={
            "type": "Polygon",
            "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]],
        },
        bbox=[100, 0, 101, 1],
        assets=[
            Asset.create(
                name="asset1",
                href="https://api.example.com/x.json",
                title="an item",
                description="an item description",
                type=MediaType.JSON,
                roles=[AssetRole.data],
            ),
        ],
        links=[
            Link.create(
                href="https://api.example.com/x.json",
                rel=LinkRelation.canonical,
                type=MediaType.JSON,
                title="an item",
                method=HttpMethod.GET,
            ),
        ],
        datetime=pystac.utils.str_to_datetime("2021-01-01T00:00:00Z"),
        extensions=[
            EOExtension.create(cloud_cover=3.14, snow_cover=2.7),
            ViewExtension.create(
                off_nadir=10.5, incidence_angle=15.3, azimuth=230.1, sun_azimuth=120.5, sun_elevation=65.2
            ),
        ],
    )

    assert item.model_dump(mode="json") == {
        "type": "Feature",
        "stac_version": "1.1.0",
        "stac_extensions": [
            "https://stac-extensions.github.io/eo/v2.0.0/schema.json",
            "https://stac-extensions.github.io/view/v1.0.0/schema.json",
        ],
        "id": "normal-item-1",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]],
        },
        "bbox": [100.0, 0.0, 101.0, 1.0],
        "properties": {
            "title": None,
            "description": None,
            "bands": None,
            "constellation": None,
            "created": None,
            "datetime": "2021-01-01T00:00:00Z",
            "start_datetime": None,
            "end_datetime": None,
            "gsd": None,
            "instruments": None,
            "keywords": None,
            "license": None,
            "mission": None,
            "platform": None,
            "providers": None,
            "roles": None,
            "updated": None,
            "eo:cloud_cover": 3.14,
            "eo:snow_cover": 2.7,
            "view:azimuth": 230.1,
            "view:incidence_angle": 15.3,
            "view:off_nadir": 10.5,
            "view:sun_azimuth": 120.5,
            "view:sun_elevation": 65.2,
        },
        "links": [
            {
                "href": "https://api.example.com/x.json",
                "rel": "canonical",
                "type": "application/json",
                "title": "an item",
                "description": None,
                "method": "get",
                "headers": None,
                "body": None,
            }
        ],
        "assets": {
            "asset1": {
                "href": "https://api.example.com/x.json",
                "title": "an item",
                "description": "an item description",
                "type": "application/json",
                "roles": ["data"],
            }
        },
        "collection": None,
    }


def test_item_with_duplicate_stac_extensions() -> None:
    fixture_dir = Path(__file__).parent.absolute() / "fixtures"
    item_dict = json.loads(Path(fixture_dir / "minimal.json").read_text())
    item_dict["stac_extensions"] = ["same", "same"]
    with pytest.raises(ValidationError, match="stac_extensions must contain unique items"):
        Item.model_validate(item_dict)


# def test_json_schema() -> None:
#     fixture_dir = Path(__file__).parent.absolute() / "fixtures"
#     Path(fixture_dir / "schema.json").write_text(json.dumps(Item.model_json_schema(), indent=2))
