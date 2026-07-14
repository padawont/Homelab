---
title: "Path Parameters"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - path-parameters
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/path-params/"
    title: "FastAPI Docs — Path Parameters"
last_audit_date: 2026-06-09
---

# Path Parameters

Extract values from the URL path by declaring them in the function signature:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

## Type validation

FastAPI uses Python type hints to:
- Validate the parameter type (e.g., `int`, `str`, `float`)
- Generate OpenAPI schema
- Return `422` on type mismatch

## Order matters

Static paths must be declared before dynamic ones:

```python
@app.get("/users/me")
async def read_current_user(): ...

@app.get("/users/{user_id}")
async def read_user(user_id: int): ...
```

## Path converter types

| Type | Example | Validation |
|---|---|---|
| `int` | `/items/{item_id}` | Must be integer |
| `str` | `/users/{name}` | Any string |
| `float` | `/prices/{value}` | Must be float |
| `path` | `/files/{filepath:path}` | Slash-containing string |

For advanced validations like `gt`, `ge`, see [path-parameters-validation.md](./path-parameters-validation.md).
