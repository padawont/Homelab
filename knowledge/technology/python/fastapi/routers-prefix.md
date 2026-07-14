---
title: "Router Prefix, Tags, and Responses"
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

# Router Prefix, Tags, and Responses

Configure `APIRouter` with shared settings:

```python
from fastapi import APIRouter, status

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={
        404: {"description": "Item not found"},
        403: {"description": "Forbidden"},
    },
)


@router.get("/")
async def list_items():
    return [{"name": "Foo"}]


@router.get("/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item():
    return {"message": "created"}
```

## Prefix

- `prefix="/items"` → `@router.get("/")` becomes `GET /items/`
- `prefix="/api/v1/items"` → `@router.get("/")` becomes `GET /api/v1/items/`
- Prefix is prepended at `include_router()` time or at declaration

## Tags

Tags group endpoints in OpenAPI docs. Multiple tags can be applied:

```python
router = APIRouter(tags=["items", "catalog"])
```

## Shared responses

The `responses` dict adds OpenAPI response schemas to all routes on the router. Individual routes can override with their own `responses`.

See [routers.md](./routers.md) for APIRouter fundamentals and [routers-dependencies.md](./routers-dependencies.md) for per-router DI.
