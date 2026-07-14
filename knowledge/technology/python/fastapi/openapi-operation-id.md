---
title: "OpenAPI Operation ID"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - openapi
sources:
  - url: "https://fastapi.tiangolo.com/how-to/custom-openapi-operation-id/"
    title: "FastAPI Docs — Custom Operation ID"
last_audit_date: 2026-06-09
---

# OpenAPI Operation ID

Customize the `operationId` in the generated OpenAPI schema:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/items", operation_id="list_items")
async def read_items():
    return [{"name": "Foo"}]
```

## Default behavior

By default, FastAPI generates `operationId` from:
- Route path
- HTTP method
- Function name

This often produces unwieldy IDs like `read_items_items__get`.

## When to customize

- Client code generation (OpenAPI Generator, openapi-typescript)
- Cleaner API surface for consumers
- Avoiding auto-generated name collisions

## Using `operation_id` with routers

```python
router = APIRouter()


@router.get("/items", operation_id="v2_list_items")
async def list_items():
    ...
```

## Generating unique IDs

```python
from fastapi.routing import APIRoute


def custom_operation_id(route: APIRoute):
    return f"{route.tags[0]}_{route.name}" if route.tags else route.name


app = FastAPI()
app.router.generate_unique_id_function = custom_operation_id
```

See [openapi-metadata.md](./openapi-metadata.md) for API-level metadata and [openapi-tags.md](./openapi-tags.md) for tag metadata.
