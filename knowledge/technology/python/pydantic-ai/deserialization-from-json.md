---
title: "Deserialization — model_validate_json()"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - deserialization
  - json
  - model-validate-json
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/models/#model_validate_json"
    title: "Pydantic model_validate_json"
last_audit_date: 2026-06-09
---

# Deserialization — model_validate_json()

## From JSON String

Parse and validate a JSON string directly:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

json_str = '{"id": 1, "name": "Alice", "email": "alice@example.com"}'
user = User.model_validate_json(json_str)
```

## Performance Advantage

`model_validate_json()` is faster than `json.loads()` + `model_validate()` because pydantic-core parses JSON directly in Rust, skipping the intermediate Python dict.

## Strict Mode

```python
user = User.model_validate_json(json_str, strict=True)
```

## With Context

```python
user = User.model_validate_json(json_str, context={"role": "admin"})
```

See [deserialization model validate](./deserialization-model-validate.md) for parsing from dicts, and [validation context](./validation-context.md) for runtime context.
