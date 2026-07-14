---
title: "Error Handling"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pydantic
  - error-handling
  - validationerror
sources:
  - url: "https://docs.pydantic.dev/latest/concepts/models/#error-handling"
    title: "Pydantic Error Handling"
last_audit_date: 2026-06-09
---

# Error Handling

## ValidationError Structure

When validation fails, a `ValidationError` is raised:

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    name: str
    age: int

try:
    user = User(name="Alice", age="not a number")
except ValidationError as e:
    print(e.errors())
```

## errors() Output

```python
[
    {
        "type": "int_parsing",
        "loc": ("age",),
        "msg": "Input should be a valid integer",
        "input": "not a number",
        "url": "https://errors.pydantic.dev/.../int_parsing"
    }
]
```

## Accessing Specific Errors

```python
except ValidationError as e:
    for err in e.errors():
        field = ".".join(str(x) for x in err["loc"])
        msg = err["msg"]
        print(f"{field}: {msg}")
```

## Error Types Reference

Common `type` values: `missing`, `int_parsing`, `float_parsing`, `string_type`, `literal_error`, `union_tag_invalid`, `value_error`. See [validation context](./validation-context.md) for validators that raise `ValueError`.
