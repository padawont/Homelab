---
title: "Async Client Session Fixture"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest-asyncio
  - fixtures
  - httpx
  - async
sources:
  - url: "https://www.python-httpx.org/async/"
    title: "httpx — Async Client"
last_audit_date: 2026-06-09
---

# Async Client Session Fixture

Create a reusable `AsyncClient` fixture for testing async web apps.

## Basic Fixture

```python
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
```

## With Auth Headers

```python
@pytest_asyncio.fixture
async def auth_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": "Bearer test-token"},
    ) as client:
        yield client
```

## Configurable Client

```python
@pytest_asyncio.fixture
async def client_for_user(request):
    """Create a client with a specific user auth."""
    user = getattr(request, "param", "default_user")
    token = create_test_token(user)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        yield client
```

## Separate Base URL

```python
@pytest_asyncio.fixture
async def live_client():
    """For integration tests against a real server."""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        yield client
```

See [httpx-async-client-fastapi](./httpx-async-client-fastapi.md) for ASGITransport setup and [async-fixtures-temporary-data](./async-fixtures-temporary-data.md) for creating test data.
