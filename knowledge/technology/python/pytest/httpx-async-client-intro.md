---
title: "httpx AsyncClient"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - httpx
  - async
  - testing
  - client
sources:
  - url: "https://www.python-httpx.org/async/"
    title: "httpx — Async Client"
last_audit_date: 2026-06-09
---

# httpx AsyncClient

`httpx.AsyncClient` provides async HTTP request capabilities for testing.

## Basic Usage

```python
import httpx
import pytest

@pytest.mark.asyncio
async def test_async_get():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://httpbin.org/get")
        assert response.status_code == 200
```

## Key Methods

```python
async with httpx.AsyncClient() as client:
    await client.get(url)
    await client.post(url, json={...})
    await client.put(url, json={...})
    await client.patch(url, json={...})
    await client.delete(url)
```

## With FastAPI

Use `ASGITransport` to talk directly to a FastAPI app without a live server:

```python
from httpx import AsyncClient, ASGITransport
from myapp import app

@pytest.mark.asyncio
async def test_fastapi_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
```

See [httpx-async-client-fastapi](./httpx-async-client-fastapi.md) for more FastAPI patterns.
