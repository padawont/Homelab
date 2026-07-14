---
title: "Request Body — Nested Models"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - request-body
  - pydantic
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/body-nested-models/"
    title: "FastAPI Docs — Nested Models"
last_audit_date: 2026-06-09
---

# Request Body — Nested Models

Pydantic models support nesting, lists, and deep structures:

```python
from pydantic import BaseModel
from fastapi import FastAPI


class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    price: float
    images: list[Image] | None = None
    tags: set[str] = set()


app = FastAPI()


@app.post("/items")
async def create_item(item: Item):
    return item
```

## Deep nesting

Models can be nested arbitrarily deep:

```python
class Offer(BaseModel):
    name: str
    items: list[Item]
```

## Submodel type casting

FastAPI deep-coerces nested JSON — all submodels are validated recursively.

## Model `model_dump()` vs `model_dump(mode="json")`

- `model_dump()` — returns dict with Python types
- `model_dump(mode="json")` — returns JSON-compatible types (e.g., `str` for dates)

See [request-body-single.md](./request-body-single.md) for the basics of Pydantic body models.
