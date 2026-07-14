---
title: "Streaming Response"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - streaming
sources:
  - url: "https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse"
    title: "FastAPI Docs — StreamingResponse"
last_audit_date: 2026-06-09
---

# Streaming Response

Stream data incrementally using `StreamingResponse` with a generator:

```python
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


async def slow_numbers():
    for i in range(10):
        await asyncio.sleep(0.5)
        yield f"data: {i}\n\n"


@app.get("/stream")
async def stream_numbers():
    return StreamingResponse(
        slow_numbers(),
        media_type="text/event-stream",
    )
```

> [!TIP]
> **FastAPI docs guidance:** The FastAPI docs now recommend using the **"Stream Data"** pattern — setting `response_class=StreamingResponse` on the route decorator and yielding content directly from the path operation function. This is the recommended approach for new code:
>
> ```python
> @app.get("/stream", response_class=StreamingResponse)
> async def stream_numbers():
>     for i in range(10):
>         await asyncio.sleep(0.5)
>         yield f"data: {i}\n\n"
> ```
>
> This approach is more convenient than manually constructing `StreamingResponse(content=...)` and handles cancellation behind the scenes. If you do use the manual `StreamingResponse(content=...)` approach with an async generator, be aware that the generator may not be cancelled properly when the client disconnects; if your generator holds resources (open files, DB connections, etc.), consider adding cancellation handling or using an async iterator that respects `asyncio.CancelledError`. See the [FastAPI docs on `StreamingResponse`](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse) for the latest guidance.

## Generator types

| Generator | Use case |
|---|---|
| `async def` generator (async iterable) | Non-blocking async iteration |
| `def` generator (sync iterable) | Synchronous iteration |

## File streaming

```python
def read_large_file(filepath: str):
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            yield chunk


@app.get("/large-file")
async def stream_file():
    return StreamingResponse(
        read_large_file("data.csv"),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=data.csv"},
    )
```

## Custom headers

```python
return StreamingResponse(
    content=generator(),
    media_type="application/json",
    headers={"X-Stream-Version": "1.0"},
)
```

See [streaming-file.md](./streaming-file.md) for `FileResponse` and [streaming-sse.md](./streaming-sse.md) for Server-Sent Events.
