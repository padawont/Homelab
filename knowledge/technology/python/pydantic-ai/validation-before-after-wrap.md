---
title: "Validation Modes: Before, After, Wrap"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - validation
  - modes
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/validators/#validation-modes"
    title: "Pydantic Validation Modes"
last_audit_date: 2026-06-09
---

# Validation Modes: Before, After, Wrap

## Mode Overview

| Mode | When it runs | Receives | Must return |
|---|---|---|---|
| `before` | Before type coercion/validation | Raw value | Transformed raw value |
| `after` | After type coercion/validation | Coerced value | Coerced value (or raise) |
| `plain` | Terminates validation (no internal type check) | Raw value | Any value (bypasses type coercion) |
| `wrap` | Wraps the inner validation | Raw value + validator fn | Validated value |

## before

```python
from pydantic import BaseModel, field_validator

class Model(BaseModel):
    value: int

    @field_validator("value", mode="before")
    @classmethod
    def coerce_string(cls, v: object) -> object:
        if isinstance(v, str) and v.startswith("0x"):
            return int(v, 16)
        return v
```

## after

```python
@field_validator("value", mode="after")
@classmethod
def must_be_positive(cls, v: int) -> int:
    if v < 0:
        raise ValueError("must be positive")
    return v
```

## wrap

Wrap validators receive a callable to perform the inner validation:

```python
from pydantic import field_validator, ValidationInfo, ValidatorFunctionWrapHandler

@field_validator("value", mode="wrap")
@classmethod
def log_and_validate(
    cls, v: object, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> object:
    print(f"Validating {info.field_name}: {v!r}")
    result = handler(v)
    print(f"Result: {result}")
    return result
```

See [field validation](./field-validation.md) and [model validation](./model-validation.md) for base usage.
