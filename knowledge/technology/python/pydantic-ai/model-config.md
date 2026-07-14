---
title: "Model Config"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - model-config
  - configuration
sources:
  - url: "https://docs.pydantic.dev/latest/api/config/"
    title: "Pydantic Config Documentation"
last_audit_date: 2026-06-09
---

# Model Config

## model_config

Set behaviour via a class-level dict or `ConfigDict`:

```python
from pydantic import BaseModel, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,          # make model immutable after init
        extra="forbid",       # reject unknown fields
        # ⚠ populate_by_name is not recommended in v2.11+, will be deprecated in v3
        #    Use validate_by_name=True + validate_by_alias=True instead:
        validate_by_name=True,   # allow field access by Python name (v2.11+)
        validate_by_alias=True,  # allow field access by alias (v2.11+)
    )
    id: int
    name: str
```

## Common Options

| Option | Values | Effect |
|---|---|---|
| `frozen` | `True` / `False` | Prevents attribute mutation |
| `extra` | `"ignore"`, `"forbid"`, `"allow"` | Behaviour for unknown fields |
| `populate_by_name` | `True` / `False` | Accept alias or Python name — **⚠ Not recommended in v2.11+**, will be deprecated in v3; use `validate_by_name` + `validate_by_alias` instead |
| `validate_default` | `True` / `False` | Validate fields with default values |
| `arbitrary_types_allowed` | `True` / `False` | Allow non-standard types |

See [field aliases](./field-aliases.md) for `populate_by_name` usage, and [serialization model dump](./serialization-model-dump.md) for output control.
