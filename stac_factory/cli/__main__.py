import json

from pathlib import Path
from typing import Annotated

import cyclopts

from pydantic import ValidationError
from rich import print as rprint

from stac_factory.models import Item

type RequiredPath = Annotated[Path, cyclopts.Parameter()]

# type RequiredStrParameter = Annotated[str, cyclopts.Parameter()]
# type OptionalStrParameter = Annotated[str | None, cyclopts.Parameter()]

app = cyclopts.App(help="An application for validating STAC Item JSON.")


@app.command
def validate(filename: RequiredPath) -> None:
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
    app()
