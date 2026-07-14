---
title: "OpenAPI Tags"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - openapi
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-tags"
    title: "FastAPI Docs — Tag Metadata"
last_audit_date: 2026-06-09
---

# OpenAPI Tags

Add metadata and ordering to OpenAPI tags:

```python
from fastapi import FastAPI

app = FastAPI()

tags_metadata = [
    {
        "name": "items",
        "description": "Operations on **items**. Full CRUD support.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://example.com/items-docs",
        },
    },
    {
        "name": "users",
        "description": "User management and authentication.",
    },
    {
        "name": "admin",
        "description": "Admin-only operations. Requires admin role.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)


@app.get("/items", tags=["items"])
async def read_items():
    return [{"name": "Foo"}]
```

## Tag ordering

Tags appear in the docs in the order they are defined in `openapi_tags`. Routes with tags not in the list appear at the end.

## Multiple tags per route

```python
@app.get("/admin/dashboard", tags=["admin", "dashboard"])
async def dashboard(): ...
```

## Tags with routers

```python
router = APIRouter(tags=["items"])
```

The tag applies to all routes on that router.

See [openapi-metadata.md](./openapi-metadata.md) for API-level metadata and [openapi-operation-id.md](./openapi-operation-id.md) for operation IDs.
