---
title: "Global Dependencies"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - dependency-injection
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/dependencies/global-dependencies/"
    title: "FastAPI Docs — Global Dependencies"
last_audit_date: 2026-06-09
---

# Global Dependencies

Apply dependencies to every route on an app or router:

```python
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI()


def verify_api_key(api_key: str = Header(...)):
    if api_key != "secret-key":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return api_key


# All routes require the API key
app = FastAPI(dependencies=[Depends(verify_api_key)])


@app.get("/items")
async def read_items():
    return [{"name": "Foo"}]


@app.get("/users")
async def read_users():
    return [{"name": "Alice"}]
```

## Per-router global dependencies

```python
from fastapi import APIRouter, Depends

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/secure-data")
async def secure_data():
    return {"data": "protected"}
```

## Mixing global and per-route

Global dependencies run first, then per-route dependencies. Both can coexist.

## Skipping global deps

Global dependencies cannot be bypassed per-route. Setting `dependencies=None` on a route decorator
only clears that route's *own* dependency list — it does not affect app-level or router-level global
dependencies. FastAPI applies global dependencies to every route unconditionally.

If selective exclusion is needed, handle it inside the dependency itself by inspecting the request:

```python
from fastapi import FastAPI, Depends, HTTPException, status, Request

app = FastAPI(dependencies=[Depends(verify_api_key)])

# Routes that should skip the global dep check
SKIP_PATHS = {"/health", "/docs", "/openapi.json"}


def verify_api_key(request: Request, api_key: str | None = Header(default=None)):
    if request.url.path in SKIP_PATHS:
        return None  # Bypass auth for open endpoints
    if api_key != "secret-key":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return api_key
```

See [routers.md](./routers.md) for APIRouter setup and [dependency-override-testing.md](./dependency-override-testing.md) for testing with overrides.
