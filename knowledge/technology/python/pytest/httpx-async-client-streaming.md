---
title: "Testing SSE and Streaming Endpoints"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - httpx
  - async
  - streaming
  - sse
sources:
  - url: "https://www.python-httpx.org/quickstart/#streaming-responses"
    title: "httpx — Streaming Responses"
last_audit_date: 2026-06-09
---

# Testing SSE and Streaming Endpoints

Test streaming endpoints (SSE, chunked responses) using `AsyncClient` with streaming enabled.

## Streaming Response

```python
@pytest.mark.asyncio
async def test_streaming_response(async_client):
    async with async_client.stream("GET", "/events") as response:
        chunks = []
        async for chunk in response.aiter_bytes():
            chunks.append(chunk)
    assert response.status_code == 200
    assert len(chunks) > 0
```

## SSE (Server-Sent Events)

```python
@pytest.mark.asyncio
async def test_sse_endpoint(async_client):
    async with async_client.stream("GET", "/sse") as response:
        events = []
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                events.append(line[5:].strip())
        assert len(events) >= 3
```

## Streaming Upload

```python
import httpx

async def upload_large_file(client):
    async def file_generator():
        for i in range(100):
            yield f"chunk-{i}\n".encode()

    response = await client.post("/upload", content=file_generator())
    assert response.status_code == 200
```

## Fixture with Stream Support

```python
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
```

See [httpx-async-client-fastapi](./httpx-async-client-fastapi.md) for the base fixture and [async-fixtures-api-client](./async-fixtures-api-client.md) for patterns.
