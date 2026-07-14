---
title: "Request Body — Field() Validations"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - request-body
  - pydantic
  - validation
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/body-fields/"
    title: "FastAPI Docs — Field"
last_audit_date: 2026-06-09
---

# Request Body — Field() Validations

Add metadata and constraints to Pydantic fields with `Field()`:

```python
from pydantic import BaseModel, Field
from fastapi import FastAPI


class Item(BaseModel):
    name: str = Field(title="Name", description="Item display name", max_length=100)
    price: float = Field(gt=0, description="Must be positive", examples=[9.99])
    tax: float | None = Field(default=None, ge=0, le=0.5)


app = FastAPI()


@app.post("/items")
async def create_item(item: Item):
    return item
```

## Common `Field()` parameters

| Parameter | Type | Purpose |
|---|---|---|
| `default` | any | Default value |
| `default_factory` | callable | Dynamic default |
| `alias` | str | JSON field alias |
| `title` | str | Schema title |
| `description` | str | Schema description |
| `examples` | list | OpenAPI examples |
| `gt` / `ge` | number | Greater than / greater or equal |
| `lt` / `le` | number | Less than / less or equal |
| `min_length` / `max_length` | int | String length bounds |
| `pattern` | str | Regex pattern |

The `examples` field populates Swagger UI's "Examples" dropdown.

See [request-body-single.md](./request-body-single.md) for basic body usage and [query-parameters-str-validation.md](./query-parameters-str-validation.md) for `Query()` equivalents.
