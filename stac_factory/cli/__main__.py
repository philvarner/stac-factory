import json

from pathlib import Path

import cyclopts

from pydantic import ValidationError
from rich import print as rprint

from stac_factory.models import Item

app = cyclopts.App(help="An application for validating STAC Item JSON.")


@app.command
def validate(filename: Path) -> None:
    try:
        Item.model_validate_json(filename.read_text())
        rprint("[green]Success![/green]")
    except ValidationError as e:
        rprint("[red]Failure:[/red]")
        print(e.json(indent=2))


@app.command
def json_schema() -> None:
    rprint(json.dumps(Item.model_json_schema(), indent=2))


if __name__ == "__main__":
    app()  # pragma: no cover
