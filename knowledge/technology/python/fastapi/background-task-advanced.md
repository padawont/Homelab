---
title: "Background Tasks — Advanced"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - background-tasks
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/background-tasks/"
    title: "FastAPI Docs — Background Tasks"
last_audit_date: 2026-06-09
---

# Background Tasks — Advanced

## Background tasks with dependencies

Combine `BackgroundTasks` with dependency injection:

```python
from fastapi import FastAPI, BackgroundTasks, Depends

app = FastAPI()


def get_db():
    return {"connection": "db-connection"}


def log_event(db: dict, event: str):
    # db is captured at schedule-time, not run-time
    print(f"Logging {event} to {db['connection']}")


@app.post("/events")
async def create_event(
    event: str,
    tasks: BackgroundTasks,
    db: dict = Depends(get_db),
):
    tasks.add_task(log_event, db, event)
    return {"message": "event will be logged"}
```

## Using `BackgroundTask` directly

```python
from starlette.background import BackgroundTask

@app.post("/direct")
async def direct_task():
    task = BackgroundTask(send_email, to="user@example.com")
    return JSONResponse({"status": "ok"}, background=task)
```

## Task ordering

Tasks are executed in the order they were added. If any task raises an exception, subsequent tasks still run (exceptions are not propagated to the response).

## When to use alternatives

| Tool | Use case |
|---|---|
| `BackgroundTasks` | Lightweight, fire-and-forget within same process |
| Celery / ARQ | Distributed, persistent, retryable task queue |
| FastAPI's `lifespan` | Startup/shutdown one-time tasks |

See [background-tasks.md](./background-tasks.md) for basic usage.
