---
title: "Field Validation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - validation
  - field-validators
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/validators/#field-validators"
    title: "Pydantic Field Validators"
last_audit_date: 2026-06-09
---

# Field Validation

## @field_validator

Apply custom validation to individual fields:

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    age: int

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("age")
    @classmethod
    def age_must_be_positive(cls, v: int) -> int:
        if v < 0:
            raise ValueError("age must be >= 0")
        return v
```

## Multiple Fields

Pass multiple field names to a single validator:

```python
class User(BaseModel):
    name: str
    email: str

    @field_validator("name", "email")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("field must not be empty")
        return v
```

See [validation context](./validation-context.md) for accessing the full data during validation, and [validation before/after/wrap](./validation-before-after-wrap.md) for mode control.
