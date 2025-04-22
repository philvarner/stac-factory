# stac-factory

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

## Possible errors

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

## Developing

uv

pre-commit install

## Acknowledgements

Borrows heavily from:

- geojson-pydantic (MIT) Copyright (c) 2020 Development Seed
- stac-pydantic (MIT) Copyright (c) 2020 Arturo AI
- pystac  (Apache-2.0) Copyright 2019-2024 the authors
- [rustac](https://github.com/stac-utils/rustac) (Apache-2.0, MIT) n/a
- [stac4s](https://github.com/stac-utils/stac4s) (Apache-2.0) n/a
