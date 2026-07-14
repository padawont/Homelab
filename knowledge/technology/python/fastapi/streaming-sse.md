---
title: "Streaming — Server-Sent Events"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - streaming
  - sse
sources:
  - url: "https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse"
    title: "FastAPI Docs — StreamingResponse"
last_audit_date: 2026-06-09
---

# Streaming — Server-Sent Events

Implement SSE (Server-Sent Events) using `StreamingResponse`:

```python
import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


async def event_generator():
    for i in range(100):
        await asyncio.sleep(1)
        data = json.dumps({"id": i, "message": f"Event {i}"})
        yield f"data: {data}\n\n"
    yield "event: complete\ndata: {}\n\n"


@app.get("/events")
async def sse_endpoint():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
```

## SSE message format

```
data: {"message": "hello"}\n\n          # Simple data
event: update\ndata: {...}\n\n           # Named event
id: 42\ndata: {...}\n\n                   # Event ID
retry: 5000\ndata: {...}\n\n              # Reconnection time
```

## Client consumption

```javascript
const source = new EventSource("/events");
source.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

## SSE vs WebSocket

| Feature | SSE | WebSocket |
|---|---|---|
| Direction | Server → Client | Bidirectional |
| Protocol | HTTP | WS |
| Auto-reconnect | Built-in | Manual |
| Binary data | Text only (base64) | Full binary |

See [streaming-response.md](./streaming-response.md) for `StreamingResponse` and [websockets-intro.md](./websockets-intro.md) for WebSocket alternatives.
