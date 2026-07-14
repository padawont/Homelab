---
title: "Query Parameters — String Validation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - query-parameters
  - validation
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/query-params-str-validations/"
    title: "FastAPI Docs — Query Parameter String Validations"
last_audit_date: 2026-06-09
---

# Query Parameters — String Validation

Add constraints to query parameters using `Query()`:

```python
from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/items")
async def read_items(
    q: str | None = Query(
        default=None,
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_]+$",
        description="Search query",
        examples=["hello_world"],
    ),
):
    return {"q": q}
```

## `Query()` parameters

| Parameter | Type | Purpose |
|---|---|---|
| `default` | any | Default value; omit for required |
| `min_length` | int | Minimum string length |
| `max_length` | int | Maximum string length |
| `pattern` | str | Regex pattern validation |
| `alias` | str | Alternative query param name |
| `deprecated` | bool | Mark as deprecated in docs |
| `include_in_schema` | bool | Hide from OpenAPI |
| `description` | str | OpenAPI description |
| `examples` | list | OpenAPI examples |

## Required with validation

Omit `default` to make it required while adding constraints:

```python
@app.get("/search")
async def search(q: str = Query(min_length=2)):
    return {"q": q}
```

For numeric constraints on query params, see [query-parameters.md](./query-parameters.md). For path parameter equivalents, see [path-parameters-validation.md](./path-parameters-validation.md).
