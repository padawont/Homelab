---
title: "Performance — Async Paths"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - performance
  - async
sources:
  - url: "https://fastapi.tiangolo.com/async/"
    title: "FastAPI Docs — Async"
last_audit_date: 2026-06-09
---

# Performance — Async Paths

Keep routes non-blocking for maximum throughput:

## DO: async for I/O

```python
@app.get("/users")
async def get_users():
    users = await db.fetch_all("SELECT * FROM users")
    return users


@app.get("/data")
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
    return response.json()
```

## DON'T: block the event loop

```python
# BAD: Blocks the entire event loop
@app.get("/users")
async def get_users():
    import time
    time.sleep(2)  # Blocks all other requests
    return await db.fetch_all("SELECT * FROM users")


# GOOD: Use def (runs in thread pool)
@app.get("/users")
def get_users_sync():
    import time
    time.sleep(2)
    return db_query()
```

## Identify blocking code

| Blocking call | Fix |
|---|---|
| `time.sleep(n)` | `asyncio.sleep(n)` or move to sync handler |
| `requests.get(url)` | `httpx.AsyncClient()` |
| `open(file).read()` | `aiofiles.open()` or thread pool |
| Sync DB driver | `run_in_threadpool()` |
| CPU-heavy computation | Move to background worker |

## Async pool monitoring

Use `asyncio.all_tasks()` to monitor for stuck tasks:

```python
import asyncio
print(f"Active tasks: {len(asyncio.all_tasks())}")
```

See [blocking-io.md](./blocking-io.md) for handling sync code in async handlers and [async-handlers.md](./async-handlers.md) for the `async def` vs `def` decision.
