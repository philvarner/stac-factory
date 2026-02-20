import json

from pathlib import Path

import pytest

from stac_factory.cli.__main__ import app

fixture_dir = Path(__file__).parent.absolute() / "fixtures"


def test_cli_validate_valid(capsys: pytest.CaptureFixture[str]) -> None:
    app(["validate", str(fixture_dir / "minimal.json")])
    assert "Success" in capsys.readouterr().out


def test_cli_validate_invalid(capsys: pytest.CaptureFixture[str]) -> None:
    app(["validate", str(fixture_dir / "invalid.json")])
    assert "Failure" in capsys.readouterr().out


def test_cli_json_schema(capsys: pytest.CaptureFixture[str]) -> None:
    app(["json-schema"])
    schema = json.loads(capsys.readouterr().out)
    assert schema["title"] == "Item"
