---
title: "Testing — Async Client"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testing
  - async
sources:
  - url: "https://fastapi.tiangolo.com/advanced/async-tests/"
    title: "FastAPI Docs — Async Tests"
last_audit_date: 2026-06-09
---

# Testing — Async Client

Use `httpx.AsyncClient` for testing async endpoints directly:

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.anyio
async def test_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}
```

## With pytest-asyncio

```python
import pytest


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_create_item():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/items", json={"name": "Foo", "price": 42})
        assert response.status_code == 201
```

## When to use AsyncClient

| Situation | Client |
|---|---|
| Sync tests | `TestClient` |
| Async tests | `httpx.AsyncClient` |
| Testing async lifespan | `AsyncClient` via `ASGITransport` |

## Without `ASGITransport` (httpx < 0.28)

Before httpx 0.28, you could pass `app=app` directly to `AsyncClient`:

```python
async with AsyncClient(app=app, base_url="http://test") as client:
    ...
```

**httpx 0.28 removed the `app` parameter entirely.** If you're on httpx >= 0.28, the snippet above will raise a `TypeError`. You **must** use `ASGITransport` as shown in the examples at the top of this note.

## Installing test dependencies

```bash
uv add httpx pytest pytest-asyncio anyio
```

See [testing-testclient-intro.md](./testing-testclient-intro.md) for sync TestClient setup.
