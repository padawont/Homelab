---
title: "Nested Models"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - nested-models
  - composition
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/models/#nested-models"
    title: "Pydantic Nested Models"
last_audit_date: 2026-06-09
---

# Nested Models

## Basic Nesting

Models can contain other models as fields:

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    address: Address
    previous_addresses: List[Address] = []
```

## Nested Validation

```python
data = {
    "name": "Alice",
    "address": {"street": "123 Main", "city": "Springfield", "zip_code": "12345"}
}
user = User.model_validate(data)
```

## Recursive Models

Use `ForwardRef` or `from __future__ import annotations` for self-referencing models:

```python
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional

class TreeNode(BaseModel):
    value: int
    left: Optional[TreeNode] = None
    right: Optional[TreeNode] = None
```

See [union types](./union-types.md) for heterogeneous nesting, and [discriminated unions](./discriminated-unions.md) for polymorphic patterns.
