---
title: "Request Body — Single Model"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - request-body
  - pydantic
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/body/"
    title: "FastAPI Docs — Request Body"
last_audit_date: 2026-06-09
---

# Request Body — Single Model

Use Pydantic models for JSON request bodies:

```python
from pydantic import BaseModel
from fastapi import FastAPI


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


app = FastAPI()


@app.post("/items")
async def create_item(item: Item):
    return item
```

## How it works

- FastAPI reads the JSON body
- Validates it against the `Item` model
- Returns `422` on validation failure with per-field errors
- Injects the validated `Item` instance into the handler

## Auto-generated docs

The model appears in `/docs` (Swagger) and `/redoc` with full JSON Schema derived from Pydantic fields.

See [request-body-multiple.md](./request-body-multiple.md) for multiple body parameters and [request-body-nested.md](./request-body-nested.md) for nested models.
