---
title: "Path Parameters — Numeric Validation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - path-parameters
  - validation
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/"
    title: "FastAPI Docs — Path Parameter Numeric Validations"
last_audit_date: 2026-06-09
---

# Path Parameters — Numeric Validation

Add numeric constraints to path parameters using `Path()`:

```python
from fastapi import FastAPI, Path

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(gt=0, le=1000, description="The item ID"),
):
    return {"item_id": item_id}
```

## `Path()` parameters

| Parameter | Type | Purpose |
|---|---|---|
| `gt` | number | Greater than |
| `ge` | number | Greater than or equal |
| `lt` | number | Less than |
| `le` | number | Less than or equal |
| `title` | str | OpenAPI title |

## Path parameters are always required

Unlike `Query()`, path parameters cannot have defaults — they are always required by the URL structure.

```python
# Default is ignored — path params can't have defaults
@app.get("/items/{item_id}")
async def read_item(item_id: int = Path(default=5)): ...
```

## Multiple path params

```python
@app.get("/items/{item_id}/variants/{variant_id}")
async def read_variant(
    item_id: int = Path(gt=0),
    variant_id: int = Path(gt=0, le=100),
):
    ...
```

See [query-parameters-str-validation.md](./query-parameters-str-validation.md) for string validation equivalents on query parameters.
