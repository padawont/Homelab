---
title: "AsyncClient with ASGITransport"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - httpx
  - async
  - fastapi
  - asgi-transport
sources:
  - url: "https://www.python-httpx.org/advanced/transports/"
    title: "httpx — Custom Transports"
last_audit_date: 2026-06-09
---

# AsyncClient with ASGITransport

Use `ASGITransport` to test ASGI applications (FastAPI, Starlette) with `AsyncClient` without a live server.

## Basic Pattern

```python
import pytest
from httpx import AsyncClient, ASGITransport
from myapp import app

@pytest.mark.asyncio
async def test_async_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/items")
        assert response.status_code == 200
```

## Fixture Pattern

```python
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_items(async_client):
    resp = await async_client.get("/items")
    assert resp.status_code == 200
```

## Why ASGITransport

- No live server required.
- Fast, direct ASGI calls.
- Supports the ASGI lifespan protocol but does not trigger lifespan events — use `asgi-lifespan`'s `LifespanManager` externally.
- Works with any ASGI app.

## VS TestClient

`AsyncClient` + `ASGITransport` provides async-native access vs. `TestClient`'s synchronous wrapper. Choose `AsyncClient` when you need true async I/O (e.g., streaming, WebSocket).

See [httpx-async-client-streaming](./httpx-async-client-streaming.md) and [httpx-async-client-websockets](./httpx-async-client-websockets.md).
