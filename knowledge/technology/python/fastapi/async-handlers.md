---
title: "Async Handlers — async def vs def"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - async
  - performance
sources:
  - url: "https://fastapi.tiangolo.com/async/#path-operation-functions"
    title: "FastAPI Docs — async def vs def"
last_audit_date: 2026-06-09
---

# Async Handlers — async def vs def

## When to use each

| Declaration | Run in | Use case |
|---|---|---|
| `async def` | Asyncio event loop | Async I/O: DB queries, HTTP calls, file reads |
| `def` | Thread pool | Blocking I/O: sync ORM calls, disk I/O, blocking third-party libs |

## Sync handler (def)

```python
@app.get("/items")
def read_items():
    # Runs in a thread pool — won't block the event loop
    import time
    time.sleep(0.1)  # blocking but OK
    return [{"name": "Foo"}]
```

## Async handler (async def)

```python
@app.get("/items")
async def read_items():
    # Runs on the main event loop
    import asyncio
    await asyncio.sleep(0.1)  # non-blocking
    return [{"name": "Foo"}]
```

## What FastAPI does internally

- `def` handlers: runs in a thread pool via `run_in_executor`
- `async def` handlers: runs directly on the event loop
- Dependencies follow the same rules

## Rule of thumb

Use `async def` when your handler `await`s something, or for compute-only work (avoids unnecessary threadpool overhead). Use `def` only when your handler must call blocking sync I/O operations (e.g. a sync ORM or filesystem library).

For mixing sync blocking code in async handlers, see [blocking-io.md](./blocking-io.md).
