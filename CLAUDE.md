# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```shell
# Setup
uv venv --python 3.13
source .venv/bin/activate
uv sync

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_item.py::test_name -sv

# Lint, format, and type check
uv run pre-commit run --all-files

# Run across multiple Python versions
uv run nox

# Build and publish
uv build
uv publish
```

## Architecture

The library enforces correctness at construction time: `Item.create()` either returns a fully valid STAC Item or raises a `ValidationError`. There is no partially-constructed or mutable intermediate state.

### Object model vs. STAC JSON

The Python object model deliberately differs from STAC JSON format. Assets are stored as a `list[Asset]` in Python but serialized to a `dict` keyed by name in JSON. A custom `model_serializer` on `Item` handles the transformation. Extensions are stored as `list[ItemExtension]` in Python but flattened into `properties` in JSON.

### Refined types (`models.py`)

All values are constrained types — no raw primitives. Key types:

- `Lat` / `Lon`: bounded floats (-90..90, -180..180)
- `ZeroTo90`, `ZeroTo360`, `Percentage`: angular/ratio constraints
- `UtcDatetime`: timezone-aware, normalized to UTC
- `URI`, `MediaType`: validated URL and RFC 6838 strings
- `Title`, `Description`, `BodyStr`: length-constrained strings

### Core models (`models.py`)

- `StacBaseModel`: base with `frozen=True, extra="ignore"`
- `BBox2d` / `BBox3d`: validate south ≤ north and elevation ordering
- `Polygon`: no holes allowed (must have exactly one ring)
- `MultiPolygon`: max 2 polygons
- `Item`: the main class; `create()` is the sole construction path
- `ItemExtension` / `EOExtension` / `ViewExtension`: extension system; each extension carries a private `_id` used when serializing to `stac_extensions`

### Constants (`constants.py`)

Enums for `HttpMethod`, `AssetRole`, `LinkRelation`, and `MediaType` — use these rather than raw strings.

### CLI (`cli/__main__.py`)

Built with [cyclopts](https://github.com/BrianPugh/cyclopts). Two commands: `validate --filename <path>` and `json-schema`.

## Code Style

Prefer functional-style Python:

- Pure functions over stateful methods where possible
- Immutable data — all models are frozen; never mutate, construct new instances instead
- Comprehensions and `map`/`filter` over imperative loops
- Explicit data transformation pipelines rather than accumulating side effects
- Avoid classes that exist only to hold mutable state; prefer `dataclass(frozen=True)` or Pydantic models when a class is needed

## Testing

- 99% coverage enforced (`--cov-fail-under 99`)
- `tests/fixtures/` contains real and synthetic STAC JSON for round-trip testing
- `test_models.py` covers individual model types; `test_item.py` covers end-to-end `Item` creation and serialization
- Nox runs the test suite on Python 3.12 and 3.13
