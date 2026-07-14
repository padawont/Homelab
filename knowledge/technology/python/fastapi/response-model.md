---
title: "Response Model"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - response
  - pydantic
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/response-model/"
    title: "FastAPI Docs — Response Model"
last_audit_date: 2026-06-09
---

# Response Model

Filter and validate outgoing data with `response_model`:

```python
from pydantic import BaseModel
from fastapi import FastAPI


class ItemIn(BaseModel):
    name: str
    price: float
    secret_pin: str


class ItemOut(BaseModel):
    name: str
    price: float


app = FastAPI()


@app.post("/items", response_model=ItemOut)
async def create_item(item: ItemIn):
    return item
```

## What it does

- Filters the returned dict/model to only fields in `ItemOut`
- Validates the output against `ItemOut` (type coercion)
- Adds `ItemOut` to the OpenAPI response schema

## Return type vs `response_model`

- `response_model` always wins for filtering
- The return annotation is used for editor support, not filtering
- Use `response_model` to enforce an API contract independent of internal logic

## Excluding fields

For the reverse (excluding specific fields), see [response-model-exclude.md](./response-model-exclude.md).

See also [response-status-code.md](./response-status-code.md) and [response-headers.md](./response-headers.md).
