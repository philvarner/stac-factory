# STAC Factory

[![CI](https://github.com/philvarner/stac-factory/actions/workflows/ci.yml/badge.svg)](https://github.com/philvarner/stac-factory/actions/workflows/continuous-integration.yml)
[![Release](https://github.com/philvarner/stac-factory/actions/workflows/release.yml/badge.svg)](https://github.com/philvarner/stac-factory/actions/workflows/release.yml)
[![PyPI version](https://badge.fury.io/py/stac-factory.svg)](https://badge.fury.io/py/stac-factory)
[![Documentation](https://readthedocs.org/projects/stac-factory/badge/?version=stable)](https://stac-factory.readthedocs.io)
[![codecov](https://codecov.io/gh/philvarner/stac-factory/branch/main/graph/badge.svg)](https://codecov.io/gh/philvarner/stac-factory)

![STAC Factory Logo](./stac-factory-logo.jpg)

## Overview

correct, not just valid wrt schema

## Installation

STAC Factory is published as `stac-factory` in PyPi.

## Why another Python STAC data model library?

Other libraries, such as pystac and stac-pydantic, are built for general-purpose use
and have relatively lax typing and validation. This aligns with the robustness principle (Postel's law)
of "be conservative in what you do, be liberal in what you accept from others". Since most consumers of
STAC objects have no control over the contents of the JSON-serialized objects, the libraries are liberal
in what they accept, and will try to read anything.  However, they leave the "conservative in what you do"
part up to the user -- they will also serialize any in-memory object to JSON, and leave it up to the rest
of the application to validate it is correct.

By comparison, STAC Factory is intended only for creating STAC entities and strongly validating correctness.

Refined types "refining types with type-level predicates which constrain
the set of values described by the refined type"

types are refined, and then can be constructed into a high-quality finished
product

<https://nikita-volkov.github.io/refined/>
<https://github.com/nikita-volkov/refined>
<https://github.com/fthomas/refined>

Opinionated.

A tightly-typed model for creating STAC Items.

Performance is not a driving concern, correctness is.

no primitives! all values are constrained in some way

"flat" model - properties are not nested in the object model

immutable, but not perfect.

## Example

Here's an example of a good one:

```python
    Item(
        stac_extensions=[],
        id="minimal-item",
        geometry={
            "type": "Polygon",
            "coordinates": [[[100.0, 0.0], [101.0, 0.0],
            [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]],
        },
        properties={"datetime": "2021-01-01T00:00:00Z"},
        bbox=[100, 0, 101, 1],
        assets={},
        links=[],
    )
```

In this one, oops, we flipped the order of the coordinates in the bbox. It's so subtle it's hard to even notice:

<!-- markdownlint-disable MD013 -->

```python
    Item(
        stac_extensions=[],
        id="minimal-item",
        geometry={
            "type": "Polygon",
            "coordinates": [[[85.0, 91.0], [86.0, 91.0], [86.0, 92.0], [85.0, 92.0], [85.0, 91.0]]],
        },
        properties={"datetime": "2021-01-01T00:00:00Z"},
        bbox=[85, 91, 86, 92],
        assets={},
        links=[],
    )
```

<!-- markdownlint-enable MD013 -->

But we get an error when constructing it:

<!-- markdownlint-disable MD013 -->

```text
E       pydantic_core._pydantic_core.ValidationError: 2 validation errors for Item
E       bbox.s_lat
E         Input should be less than or equal to 90 [type=less_than_equal, input_value=91, input_type=int]
E           For further information visit https://errors.pydantic.dev/2.11/v/less_than_equal
E       bbox.n_lat
E         Input should be less than or equal to 90 [type=less_than_equal, input_value=92, input_type=int]
E           For further information visit https://errors.pydantic.dev/2.11/v/less_than_equal
```

<!-- markdownlint-enable MD013 -->

## Possible errors

Sources:

- <https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md>
- <https://github.com/radiantearth/stac-spec/tree/master/item-spec/json-schema>
- <https://github.com/radiantearth/stac-spec/blob/master/best-practices.md>
- <https://github.com/stac-utils/stac-check>

Issues:

- ID
- Collection
  - must have link (or something)
- BBox
  - wrong coordinate order
  - antimeridian-crossing bbox inverts longitude values because compared by value
- Geometry
  - polygon or MP with no holes and no crossings
  - flip lat and lon in coordinate positions
  - wind clockwise instead of ccw
  - Polygon spans antimeridian -> MP
  - pole issues
- Other
  - proj:centroid doesnt' have the lat and lon attributes reversed

## Developing

uv

pre-commit install

## Acknowledgements

Borrows heavily from:

- pystac  (Apache-2.0) Copyright 2019-2024 the authors
- stac-pydantic (MIT) Copyright (c) 2020 Arturo AI
- geojson-pydantic (MIT) Copyright (c) 2020 Development Seed
- [rustac](https://github.com/stac-utils/rustac) (Apache-2.0, MIT) n/a
- [stac4s](https://github.com/stac-utils/stac4s) (Apache-2.0) n/a
- [Data.Geospatial](https://hackage.haskell.org/package/geojson-4.1.1/docs/Data-Geospatial.html)
  (Haskell) (BSD-style)
