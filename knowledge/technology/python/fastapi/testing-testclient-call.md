---
title: "Testing — TestClient as Context Manager"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testing
  - testclient
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/testing/"
    title: "FastAPI Docs — Testing"
last_audit_date: 2026-06-09
---

# Testing — TestClient as Context Manager

Use `TestClient` as a context manager for proper lifespan handling:

```python
from fastapi.testclient import TestClient
from main import app


def test_app():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
```

## Why the context manager

The `with` block ensures:
- The application's `lifespan` context runs (startup/shutdown)
- ASGI lifespan events are triggered
- Resources are properly cleaned up

## Without context manager

```python
client = TestClient(app)


def test_without_lifespan():
    response = client.get("/items")
    # lifespan events may NOT run in some ASGI modes
    assert response.status_code == 200
```

For simple apps without `lifespan`, the non-context-manager form works fine. For apps with startup/shutdown logic (DB pools, cache connections), always use the context manager.

## Multiple tests

```python
def test_multiple():
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.post("/items", json={"name": "Foo"}).status_code == 201
```

See [testing-testclient-intro.md](./testing-testclient-intro.md) for basic setup.
