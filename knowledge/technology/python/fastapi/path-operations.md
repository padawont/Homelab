---
title: "Path Operations"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - path-operations
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/first-steps/"
    title: "FastAPI Docs — First Steps"
last_audit_date: 2026-06-09
---

# Path Operations

Decorators on `app` define route handlers:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/items")
async def list_items():
    return [{"id": 1, "name": "Foo"}]


@app.post("/items")
async def create_item():
    return {"message": "created"}


@app.put("/items/{item_id}")
async def update_item(item_id: int):
    return {"item_id": item_id}


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"item_id": item_id, "deleted": True}


@app.patch("/items/{item_id}")
async def partial_update(item_id: int):
    return {"item_id": item_id, "patched": True}
```

## HTTP methods mapped

| Decorator | HTTP Method |
|---|---|
| `@app.get()` | GET |
| `@app.post()` | POST |
| `@app.put()` | PUT |
| `@app.delete()` | DELETE |
| `@app.patch()` | PATCH |

Each decorator accepts a path string and optional parameters (status_code, response_model, tags, dependencies).

See [path-parameters.md](./path-parameters.md) and [query-parameters.md](./query-parameters.md) for parameter details.
