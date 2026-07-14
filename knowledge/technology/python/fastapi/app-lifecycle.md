---
title: "Application Lifecycle"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - lifecycle
  - async
sources:
  - url: "https://fastapi.tiangolo.com/advanced/events/"
    title: "FastAPI Docs — Lifespan Events"
last_audit_date: 2026-06-09
---

# Application Lifecycle

Use the `lifespan` context manager pattern (recommended):

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    app.state.db_pool = await create_db_pool()
    app.state.cache = await init_cache()

    yield  # App runs here

    # Shutdown
    print("Shutting down...")
    await app.state.db_pool.close()
    await app.state.cache.close()


app = FastAPI(lifespan=lifespan)


@app.get("/items")
async def read_items():
    db = app.state.db_pool
    return await db.fetch("SELECT * FROM items")
```

## How it works

- Code before `yield` runs on startup
- Code after `yield` runs on shutdown
- `yield` itself is where the application serves requests
- `app.state` stores application-scoped objects

## Multiple startup tasks

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run multiple initializations
    db = await create_db_pool()
    cache = await init_cache()
    queue = await connect_queue()

    app.state.db = db
    app.state.cache = cache
    app.state.queue = queue

    yield

    # Cleanup in reverse order
    await queue.close()
    await cache.close()
    await db.close()
```

See [startup-shutdown.md](./startup-shutdown.md) for the legacy `@app.on_event` pattern.
