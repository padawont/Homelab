---
title: "LLM — Streaming Endpoint"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - llm
  - streaming
  - sse
sources:
  - url: "https://fastapi.tiangolo.com/"
    title: "FastAPI Documentation"
last_audit_date: 2026-06-09
---

# LLM — Streaming Endpoint

Stream LLM responses via Server-Sent Events:

```python
import json
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


async def generate_chat_stream(prompt: str):
    # Simulate streaming tokens from an LLM
    response = f"Hello! You said: {prompt}. Let me think..."
    for word in response.split():
        await asyncio.sleep(0.05)  # Simulate generation delay
        yield f"data: {json.dumps({'token': word + ' ', 'done': False})}\n\n"
    yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
    yield "data: [DONE]\n\n"


@app.get("/chat/stream")
async def chat_stream(prompt: str):
    return StreamingResponse(
        generate_chat_stream(prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

## Client (JavaScript)

```javascript
const source = new EventSource(`/chat/stream?prompt=Hello`);
source.onmessage = (event) => {
    if (event.data === "[DONE]") {
        source.close();
        return;
    }
    const data = JSON.parse(event.data);
    if (!data.done) {
        outputElement.textContent += data.token;
    }
};
```

## Error handling

```python
try:
    async for token in llm_service.generate(prompt):
        yield f"data: {json.dumps({'token': token})}\n\n"
except Exception as e:
    yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
```

See [streaming-sse.md](./streaming-sse.md) for SSE patterns and [llm-evaluation-endpoint.md](./llm-evaluation-endpoint.md) for evaluation.
