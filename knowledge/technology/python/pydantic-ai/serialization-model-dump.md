---
title: "Serialization — model_dump()"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - serialization
  - model-dump
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/serialization/#model_dump"
    title: "Pydantic model_dump"
last_audit_date: 2026-06-09
---

# Serialization — model_dump()

## Basic Usage

Convert a model instance to a dict:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

user = User(id=1, name="Alice")
data = user.model_dump()
# {"id": 1, "name": "Alice"}
```

## exclude / include

```python
data = user.model_dump(exclude={"id"})
# {"name": "Alice"}

data = user.model_dump(include={"name"})
# {"name": "Alice"}
```

## by_alias

Respect [field aliases](./field-aliases.md):

```python
data = user.model_dump(by_alias=True)
```

## exclude_unset / exclude_defaults

```python
data = user.model_dump(exclude_unset=True)    # omit unset fields
data = user.model_dump(exclude_defaults=True) # omit default-valued fields
```

See [serialization json](./serialization-json.md) for JSON output.
