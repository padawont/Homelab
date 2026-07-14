---
title: "Discriminated Unions"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - discriminated-unions
  - tagged-unions
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions"
    title: "Pydantic Unions — Discriminated Unions"
last_audit_date: 2026-06-09
---

# Discriminated Unions

## Tagged Union with Discriminator

Use `Discriminator` for efficient, type-safe polymorphic models:

```python
from pydantic import BaseModel, Discriminator, Tag
from typing import Annotated, Any, Literal, Optional, Union

class Circle(BaseModel):
    type: Literal['circle']
    radius: float

class Square(BaseModel):
    type: Literal['square']
    side: float

def shape_discriminator(v: Any) -> Optional[str]:
    if isinstance(v, dict):
        return v.get("type")
    return getattr(v, "type", None)

Shape = Annotated[
    Union[Annotated[Circle, Tag('circle')], Annotated[Square, Tag('square')]],
    Discriminator(shape_discriminator)
]

class Drawing(BaseModel):
    shapes: list[Shape]
```

## Why Use It

- Faster validation — Pydantic skips type-by-type trial matching
- Clearer error messages on mismatched types
- Schema generation (OpenAPI) produces proper `oneOf` with discriminator

See [union types](./union-types.md) for simpler union patterns, and [nested models](./nested-models.md) for composition.
