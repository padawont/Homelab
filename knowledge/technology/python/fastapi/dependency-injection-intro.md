---
title: "Dependency Injection — Introduction"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - dependency-injection
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/dependencies/"
    title: "FastAPI Docs — Dependencies"
last_audit_date: 2026-06-09
---

# Dependency Injection — Introduction

FastAPI's dependency injection system uses `Depends()` to share logic across routes.

## The problem

Without DI, you repeat authentication, DB sessions, or logging in every handler.

## The solution

```python
from fastapi import FastAPI, Depends

app = FastAPI()


def common_params(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items")
async def read_items(params: dict = Depends(common_params)):
    return params


@app.get("/users")
async def read_users(params: dict = Depends(common_params)):
    return params
```

## Key behaviors

- Dependencies run before the path operation
- Results are injected into the handler
- Dependencies can themselves have dependencies (nesting)
- FastAPI caches results within a request (singleton per request)
- Dependencies can be functions, classes, or callables

## Override for testing

Dependencies can be overridden with `app.dependency_overrides` — see [dependency-override-testing.md](./dependency-override-testing.md).

See also [dependency-functions.md](./dependency-functions.md) and [dependency-classes.md](./dependency-classes.md) for detailed patterns.
