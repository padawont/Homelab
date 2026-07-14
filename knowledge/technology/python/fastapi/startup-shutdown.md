---
title: "Legacy Startup/Shutdown Events"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - lifecycle
sources:
  - url: "https://fastapi.tiangolo.com/advanced/events/"
    title: "FastAPI Docs — Lifespan Events"
last_audit_date: 2026-06-09
---

# Legacy Startup/Shutdown Events

> **Note**: The `@app.on_event` pattern is deprecated in favor of the `lifespan` context manager (see [app-lifecycle.md](./app-lifecycle.md)). Retained for backward compatibility.

```python
from fastapi import FastAPI

app = FastAPI()


@app.on_event("startup")
async def startup():
    print("Starting up...")
    app.state.db_pool = await create_db_pool()


@app.on_event("shutdown")
async def shutdown():
    print("Shutting down...")
    await app.state.db_pool.close()
```

## Problems with `@app.on_event`

- Order of execution is not guaranteed
- Cannot share state between startup and shutdown reliably
- Harder to compose multiple startup tasks
- The `lifespan` pattern replaces both events

## Migration to lifespan

```python
# Before
@app.on_event("startup")
async def startup(): ...
@app.on_event("shutdown")
async def shutdown(): ...

# After
@asynccontextmanager
async def lifespan(app):
    ...  # startup
    yield
    ...  # shutdown

app = FastAPI(lifespan=lifespan)
```

## When to keep `@app.on_event`

Only for codebases targeting very old FastAPI versions (< 0.95). All new code should use the `lifespan` pattern.
