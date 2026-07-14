---
title: "Routers — APIRouter"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - routers
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/bigger-applications/"
    title: "FastAPI Docs — Bigger Applications"
last_audit_date: 2026-06-09
---

# Routers — APIRouter

Organize routes into separate files using `APIRouter`:

```python
# app.py
from fastapi import FastAPI
from routers import items, users

app = FastAPI()

app.include_router(items.router)
app.include_router(users.router)
```

```python
# routers/items.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/items")
async def list_items():
    return [{"name": "Foo"}]


@router.post("/items")
async def create_item():
    return {"message": "created"}
```

```python
# routers/users.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/users")
async def list_users():
    return [{"name": "Alice"}]
```

## APIRouter features

`APIRouter` supports the same parameters as `FastAPI`:
- `prefix` — URL prefix for all routes (see [routers-prefix.md](./routers-prefix.md))
- `tags` — OpenAPI tags for grouping
- `dependencies` — global dependencies (see [routers-dependencies.md](./routers-dependencies.md))
- `responses` — shared response schemas

## include_router

```python
app.include_router(
    items.router,
    prefix="/api/v1",
    tags=["items"],
)
```

See [routers-prefix.md](./routers-prefix.md) for prefix options and [routers-dependencies.md](./routers-dependencies.md) for per-router DI.
