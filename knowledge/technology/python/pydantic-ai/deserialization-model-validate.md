---
title: "Deserialization — model_validate()"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - deserialization
  - model-validate
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/models/#model_validate"
    title: "Pydantic model_validate"
last_audit_date: 2026-06-09
---

# Deserialization — model_validate()

## From Dict

Parse and validate a dict into a model instance:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

data = {"id": 1, "name": "Alice", "email": "alice@example.com"}
user = User.model_validate(data)
```

## Strict Mode

```python
user = User.model_validate(data, strict=True)
```

## With Context

Pass runtime context to validators:

```python
user = User.model_validate(data, context={"role": "admin"})
```

See [validation context](./validation-context.md) for consuming context in validators.

## From Other Model Instances

```python
existing = User(id=1, name="Alice", email="alice@x.com")
copy = User.model_validate(existing)
```

See [deserialization from json](./deserialization-from-json.md) for parsing JSON strings.
