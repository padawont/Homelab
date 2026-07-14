---
title: "Defining Models"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - basemodel
  - models
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/models/"
    title: "Pydantic Models Documentation"
last_audit_date: 2026-06-09
---

# Defining Models

## BaseModel

Pydantic models are defined by subclassing `BaseModel`:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
```

## Instantiation

Pass keyword arguments — validation runs immediately:

```python
user = User(id=1, name="Alice", email="alice@example.com")
```

Invalid data raises `ValidationError` — see [error handling](./error-handling.md).

## Field Types

Fields use Python type annotations. See [field types](./field-types.md) for the full list. See [field defaults](./field-defaults.md) for default values and factory patterns.

## Model Config

Customize model behaviour with `model_config` — see [model config](./model-config.md).
