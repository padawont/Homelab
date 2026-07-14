---
title: "Field Aliases"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - aliases
  - serialization
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/fields/#field-aliases"
    title: "Pydantic Field Aliases"
last_audit_date: 2026-06-09
---

# Field Aliases

## Alias Declaration

Use `Field(alias=...)` to map a Python field name to a different validation and serialization key:

```python
from pydantic import BaseModel, ConfigDict, Field

class User(BaseModel):
    full_name: str = Field(alias="fullName")
    user_id: int = Field(alias="userId")
```

## Validate by Name and Alias

Allow both the alias and the Python name during construction:

```python
class User(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    full_name: str = Field(alias="fullName")

# Both work:
User(fullName="Alice")
User(full_name="Alice")
```

## Serialization

Use `by_alias=True` in [model_dump](./serialization-model-dump.md) and [model_dump_json](./serialization-json.md):

```python
user.model_dump(by_alias=True)  # {"fullName": "Alice"}
```
