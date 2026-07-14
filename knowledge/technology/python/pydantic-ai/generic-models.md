---
title: "Generic Models"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - generics
  - typevar
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/models/#generic-models"
    title: "Pydantic Generic Models"
last_audit_date: 2026-06-09
---

# Generic Models

## Generic[T]

Reuse model structure with a type parameter:

```python
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int

class User(BaseModel):
    id: int
    name: str

# Concrete usage
response = PaginatedResponse[User](
    items=[User(id=1, name="Alice")],
    total=1,
    page=1
)
```

## TypeVar Bounds

Constrain the type parameter:

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T", bound=BaseModel)

class Wrapper(BaseModel, Generic[T]):
    data: T
```

## Multiple TypeVars

```python
K = TypeVar("K")
V = TypeVar("V")

class KeyValue(BaseModel, Generic[K, V]):
    key: K
    value: V
```

See [nested models](./nested-models.md) for fixed-type composition, and [union types](./union-types.md) for heterogeneous alternatives.
