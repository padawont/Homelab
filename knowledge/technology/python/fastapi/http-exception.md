---
title: "HTTPException"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - exceptions
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/handling-errors/#http-exception"
    title: "FastAPI Docs — HTTPException"
last_audit_date: 2026-06-09
---

# HTTPException

Raise standard HTTP errors with `HTTPException`:

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

items = {1: "Foo", 2: "Bar"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
            headers={"X-Error": "missing"},
        )
    return {"item_id": item_id, "name": items[item_id]}
```

## Parameters

| Parameter | Type | Purpose |
|---|---|---|
| `status_code` | int | HTTP status code |
| `detail` | str / dict / list | Error body |
| `headers` | dict | Custom response headers |

## Common status codes

| Code | Constant | Use case |
|---|---|---|
| 400 | `HTTP_400_BAD_REQUEST` | Malformed input |
| 401 | `HTTP_401_UNAUTHORIZED` | Missing/invalid auth |
| 403 | `HTTP_403_FORBIDDEN` | Insufficient permissions |
| 404 | `HTTP_404_NOT_FOUND` | Resource not found |
| 409 | `HTTP_409_CONFLICT` | Duplicate resource |
| 422 | `HTTP_422_UNPROCESSABLE_CONTENT` | Validation error |
| 429 | `HTTP_429_TOO_MANY_REQUESTS` | Rate limited |
| 500 | `HTTP_500_INTERNAL_SERVER_ERROR` | Server error |

## Custom detail

`detail` can be a string, dict, or list. Use a dict for structured error responses:

```python
raise HTTPException(
    status_code=422,
    detail={"field": "email", "message": "Invalid format"},
)
```

See [exception-handlers.md](./exception-handlers.md) for custom handler setup and [custom-exception-responses.md](./custom-exception-responses.md) for JSON error bodies.
