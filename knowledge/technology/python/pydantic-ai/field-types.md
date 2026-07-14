---
title: "Field Types"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - field-types
  - types
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/fields/"
    title: "Pydantic Fields Documentation"
last_audit_date: 2026-06-09
---

# Field Types

## Built-in Types

```python
from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
from enum import Enum

class Color(str, Enum):
    red = "red"
    green = "green"

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool
    quantity: int
    color: Color
    size: Literal["S", "M", "L"]
    tags: Optional[List[str]] = None
    metadata: Dict[str, str] = {}
```

## Type Coercion

Pydantic coerces compatible types by default (e.g., `"42"` → `42` for `int`). Use `StrictInt` to disable coercion for integers:

```python
from pydantic import StrictInt

class StrictModel(BaseModel):
    count: StrictInt  # rejects strings
```

See [field validation](./field-validation.md) for custom validators, and [union types](./union-types.md) for `Union[A, B]` patterns.
