---
title: "Blocking I/O — run_in_threadpool"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - async
  - performance
sources:
  - url: "https://fastapi.tiangolo.com/async/#concurrency-and-async-await"
    title: "FastAPI Docs — Concurrency"
last_audit_date: 2026-06-09
---

# Blocking I/O — run_in_threadpool

Run synchronous blocking code without blocking the event loop:

```python
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
import time

app = FastAPI()


def blocking_operation(n: int) -> str:
    time.sleep(n)  # Simulates CPU/blocking work
    return f"Slept for {n}s"


@app.get("/process/{n}")
async def process(n: int):
    result = await run_in_threadpool(blocking_operation, n)
    return {"result": result}
```

## Using `asyncio.to_thread` (Python 3.9+)

```python
import asyncio

@app.get("/process/{n}")
async def process(n: int):
    result = await asyncio.to_thread(blocking_operation, n)
    return {"result": result}
```

## When to use

| Situation | Approach |
|---|---|
| Synchronous DB driver | `run_in_threadpool(db_query, ...)` |
| CPU-heavy computation | Consider `ProcessPoolExecutor` |
| File I/O | `asyncio.to_thread(read_file, path)` |
| Third-party sync SDK | `run_in_threadpool(sdk_call, ...)` |

## `run_sync` shortcut

```python
from fastapi.concurrency import run_sync

@app.get("/sync-task")
async def handler():
    result = await run_sync(sync_function)
    return {"result": result}
```

Rule: any `def` FastAPI handler already runs in a thread pool — you only need these utilities when calling sync code from an `async def` handler.

See [async-handlers.md](./async-handlers.md) for the fundamental `async def` vs `def` decision.
