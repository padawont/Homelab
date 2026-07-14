---
title: "Model Validation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - validation
  - model-validators
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/validators/#model-validators"
    title: "Pydantic Model Validators"
last_audit_date: 2026-06-09
---

# Model Validation

## @model_validator

Validate the entire model after all fields are validated:

```python
from pydantic import BaseModel, model_validator

class Order(BaseModel):
    items: list[str]
    discount_code: str | None = None

    @model_validator(mode="after")
    def check_discount_requires_items(self) -> "Order":
        if self.discount_code and not self.items:
            raise ValueError(
                "discount requires at least one item"
            )
        return self
```

## mode="after"

Runs after field validators. Receives the fully-validated model instance. Must return the model.

## mode="before"

Runs before field validators. Receives raw input (`Any` type — not guaranteed to be a dict). Must return data as `Any` (not required to be a dict). When accessing dict-specific fields (e.g. `data["field"]`), guard with `isinstance(data, dict)` first, since input can be an arbitrary class instance (e.g. when `from_attributes` is enabled). See [validation before/after/wrap](./validation-before-after-wrap.md) for details on all modes.

See also [field validation](./field-validation.md) for per-field validators.
