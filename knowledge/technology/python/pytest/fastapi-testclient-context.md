---
title: "TestClient Context Manager"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testclient
  - context-manager
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/testing/"
    title: "FastAPI Testing Guide"
last_audit_date: 2026-06-09
---

# TestClient Context Manager

Use `TestClient` as a context manager to control lifespan events (startup/shutdown).

## With Statement

```python
from fastapi.testclient import TestClient
from myapp import app

def test_app_lifespan():
    with TestClient(app) as client:
        # Lifespan events (startup) have run
        resp = client.get("/")
        assert resp.status_code == 200
    # Lifespan shutdown has run
```

## Why Use It

- Triggers app lifespan handlers (`lifespan` context manager).
- Ensures clean teardown of async resources.
- Required for apps that depend on startup events (e.g., DB connection pool creation).

## Without Context Manager

Without `with`, lifespan events do not run. This is fine for stateless apps:

```python
client = TestClient(app)

def test_stateless():
    response = client.get("/health")
    assert response.status_code == 200
```

## Fixture Pattern

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_endpoint(client):
    resp = client.get("/items")
    assert resp.status_code == 200
```

See [fastapi-testclient-intro](./fastapi-testclient-intro.md) for basic usage.
