---
title: "Field Defaults"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - field-defaults
  - default-factory
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/fields/#default-values"
    title: "Pydantic Field Defaults"
last_audit_date: 2026-06-09
---

# Field Defaults

## Static Defaults

```python
from pydantic import BaseModel

class Config(BaseModel):
    host: str = "localhost"
    port: int = 8080
```

## default_factory

Use `default_factory` for mutable or dynamic defaults:

```python
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import uuid4
class Session(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    tags: list[str] = Field(default_factory=list)
```

## Required Fields

Fields without defaults are required. Use `...` (Ellipsis) with `Field(...)` for required fields with extra metadata — see [field aliases](./field-aliases.md).

> **Note:** Pydantic discourages `Field(..., ...)` for required fields with extra metadata in favor of `Annotated`. The `Annotated` approach separates the type from the metadata, which is cleaner and avoids the ellipsis pattern. Prefer this form for new code:
>
> ```python
> from typing import Annotated
> from pydantic import Field
>
> class Model(BaseModel):
>     name: Annotated[str, Field(min_length=1, max_length=100)]
>     aliases: Annotated[list[str], Field(default_factory=list)]
> ```
>
> Use `Field(...)` only for required fields that have *no* extra metadata (where `Annotated` would provide no benefit).
