---
title: "OpenAPI Metadata"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - openapi
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/metadata/"
    title: "FastAPI Docs — Metadata"
last_audit_date: 2026-06-09
---

# OpenAPI Metadata

Customize the OpenAPI documentation metadata:

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="A comprehensive API description with **Markdown** support.",
    version="2.5.0",
    summary="Short summary for API directories",
    contact={
        "name": "API Support",
        "url": "https://example.com/support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
```

## Common metadata fields

| Field | Type | Purpose |
|---|---|---|
| `title` | str | API title |
| `description` | str | Long description (Markdown) |
| `version` | str | API version string |
| `summary` | str | Short description |
| `contact` | dict | Contact info |
| `license_info` | dict | License details |
| `terms_of_service` | str | URL for ToS |

## URL customization

```python
app = FastAPI(
    docs_url=None,        # Disable Swagger UI
    redoc_url=None,        # Disable ReDoc
    openapi_url="/api/openapi.json",  # Custom path
)
```

## Hiding from docs

Set `docs_url=None` and `redoc_url=None` in production to disable public docs.

See [openapi-tags.md](./openapi-tags.md) for tag metadata and [openapi-operation-id.md](./openapi-operation-id.md) for operation IDs.
