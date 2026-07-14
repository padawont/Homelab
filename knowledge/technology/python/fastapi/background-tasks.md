---
title: "Background Tasks"
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

# Background Tasks

Run operations after returning the response using `BackgroundTasks`:

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()


def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(f"{message}\n")


@app.post("/send-notification")
async def send_notification(email: str, tasks: BackgroundTasks):
    tasks.add_task(write_log, f"Notification sent to {email}")
    return {"message": "Notification sent"}
```

## How it works

- `BackgroundTasks` is injected via `Depends` or as a parameter
- `tasks.add_task(func, *args, **kwargs)` schedules the function
- The function runs after the response is sent (not awaited by the client)
- Tasks run in the same event loop — use `async def` for I/O tasks

## Multiple tasks

```python
@app.post("/process")
async def process(data: str, tasks: BackgroundTasks):
    tasks.add_task(send_email, data)
    tasks.add_task(update_database, data)
    tasks.add_task(cleanup_temp_files, data)
    return {"message": "processing started"}
```

## Caveats

- Not for CPU-heavy work (use Celery/ARQ for that)
- Not persisted — tasks are lost if the process crashes
- For long-running or critical work, use a task queue

See [background-task-advanced.md](./background-task-advanced.md) for dependencies in background tasks.
