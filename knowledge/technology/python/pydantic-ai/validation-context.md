---
title: "Validation Context"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - validation
  - context
  - validationinfo
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/validators/#validation-context"
    title: "Pydantic Validation Context"
last_audit_date: 2026-06-09
---

# Validation Context

## ValidationInfo

Access context (other field values, configuration) inside validators:

```python
from pydantic import BaseModel, field_validator, ValidationInfo

class Signup(BaseModel):
    username: str
    password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("passwords do not match")
        return v
```

## Passing Context at Runtime

```python
from pydantic import BaseModel, field_validator, ValidationInfo

class Resource(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def check_permission(cls, v: str, info: ValidationInfo) -> str:
        user_role = info.context.get("role") if info.context else None
        if user_role != "admin" and v.startswith("secret_"):
            raise ValueError("not allowed")
        return v

result = Resource.model_validate(
    {"name": "secret_file"},
    context={"role": "user"}
)
```

See [field validation](./field-validation.md) for basic validator usage, and [model validation](./model-validation.md) for model-level validation.
