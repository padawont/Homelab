---
title: "Request Body — Multiple Parameters"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - request-body
  - pydantic
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/body-multiple-params/"
    title: "FastAPI Docs — Multiple Body Params"
last_audit_date: 2026-06-09
---

# Request Body — Multiple Parameters

Declare multiple Pydantic models as body parameters:

```python
from pydantic import BaseModel
from fastapi import FastAPI


class Item(BaseModel):
    name: str
    price: float


class User(BaseModel):
    username: str


app = FastAPI()


@app.post("/create")
async def create(item: Item, user: User):
    return {"item": item, "user": user}
```

## Single-body JSON

FastAPI expects a JSON object with keys matching the parameter names:

```json
{
  "item": {"name": "Foo", "price": 42.0},
  "user": {"username": "alice"}
}
```

## Mixing with path/query params

```python
class Offer(BaseModel):
    name: str
    price: float
    discount_applied: bool = False


@app.post("/items/{item_id}/offers")
async def create_offer(
    item_id: int,
    offer: Offer,
    discount: float = 0.0,  # query parameter
):
    return {"item_id": item_id, **offer.model_dump()}
```

- Path params (`item_id`) come from the URL
- Query params (`discount`) are the remaining scalar params
- Body params are the Pydantic models

See [query-parameters.md](./query-parameters.md) and [path-parameters.md](./path-parameters.md).
