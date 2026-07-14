---
title: "Pydantic Union Types"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - union-types
  - annotated
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/unions/"
    title: "Pydantic Union Types"
last_audit_date: 2026-06-09
---

# Union Types

## Basic Union

```python
from pydantic import BaseModel
from typing import Literal, Union

class Cat(BaseModel):
    pet_type: Literal['cat'] = 'cat'
    meow_count: int

class Dog(BaseModel):
    pet_type: Literal['dog'] = 'dog'
    bark_loudness: float

class PetOwner(BaseModel):
    pet: Union[Cat, Dog]
```

## Smart Union Matching

Pydantic evaluates all union members, scores each by the number of valid fields set plus exactness of matches, and selects the best overall match. Use `left_to_right` mode if you need first-match-wins behaviour. Be specific with field types (e.g. `Literal`) to improve scoring accuracy.

## Annotated Validators

Use `Annotated` with a validator for Union discrimination:

```python
from typing import Annotated, Union
from pydantic import BaseModel, Field

class PetOwner(BaseModel):
    pet: Annotated[
        Union[Cat, Dog],
        Field(discriminator="pet_type")
    ]
```

For complex discrimination, see [discriminated unions](./discriminated-unions.md). See also [nested models](./nested-models.md) for composition patterns.
