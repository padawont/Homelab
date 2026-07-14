---
title: "Troubleshooting"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - troubleshooting
  - errors
sources:
  - url: "https://docs.pydantic.dev/latest/errors/errors/"
    title: "Pydantic Error Documentation"
last_audit_date: 2026-06-09
---

# Troubleshooting

## Common Errors and Solutions

### ValidationError: Field required

```
Field `email` is required
```

**Fix**: The field has no default. Provide it during construction or add `= None` / `Field(default=...)`.

### ValidationError: Input should be a valid integer

```
type=int_parsing, input="not-a-number"
```

**Fix**: Pass the correct type, or add a `mode="before"` validator to coerce strings. See [field validation](./field-validation.md).

### ModuleNotFoundError: No module named 'pydantic_ai'

**Fix**: Install with `uv add pydantic-ai`. See [installation](./installation.md).

### Field alias not working during init

```python
User(name="Alice")  # raises ValidationError because populate_by_name is False by default, only alias is recognized for init
```

**Fix**: Set `model_config = {"populate_by_name": True}` and use `Field(alias="userName")`. See [field aliases](./field-aliases.md).

### Discriminated Union not matching

```python
Shape = Annotated[Union[Circle, Square], Discriminator(...)]
```

**Fix**: Ensure the discriminator function returns the exact string matching the `type` field in each variant. See [discriminated unions](./discriminated-unions.md).

### Slow validation on large datasets

**Fix**: Use `model_validate_json()` for JSON input, batch items in a list field, avoid deep union matching. See [performance optimization](./performance-optimization.md).
