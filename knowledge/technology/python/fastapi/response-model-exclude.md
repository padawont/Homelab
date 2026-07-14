---
title: "Response Model — Exclude/Include"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - response
  - pydantic
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/response-model/#response_model_exclude_unset-and-others"
    title: "FastAPI Docs — Response Model Exclude"
last_audit_date: 2026-06-09
---

# Response Model — Exclude/Include

Control which fields appear in the response without creating a separate model:

```python
from pydantic import BaseModel
from fastapi import FastAPI


class Item(BaseModel):
    name: str
    price: float
    secret_pin: str
    internal_notes: str


app = FastAPI()


@app.get("/items/{item_id}", response_model=Item, response_model_exclude={"secret_pin", "internal_notes"})
async def read_item(item_id: int):
    return {"name": "Foo", "price": 42.0, "secret_pin": "1234", "internal_notes": "..."}
```

## Available parameters

| Parameter | Type | Effect |
|---|---|---|
| `response_model_exclude` | set | Exclude these fields |
| `response_model_include` | set | Only include these fields |
| `response_model_exclude_unset` | bool | Omit fields not explicitly set |
| `response_model_exclude_none` | bool | Omit `None` values |
| `response_model_exclude_defaults` | bool | Omit fields with default values |

## Precedence

`response_model_exclude` and `response_model_include` are mutually exclusive — use one or the other.

See [response-model.md](./response-model.md) for the base pattern.
