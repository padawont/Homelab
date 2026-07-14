---
title: "Testing — Dependency Override Patterns"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testing
  - dependency-injection
sources:
  - url: "https://fastapi.tiangolo.com/advanced/testing-dependencies/"
    title: "FastAPI Docs — Testing Dependencies"
last_audit_date: 2026-06-09
---

# Testing — Dependency Override Patterns

Systematically override dependencies in tests:

## Fixture-based override

```python
import pytest
from fastapi.testclient import TestClient
from main import app, get_db


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = lambda: {"connection": "test"}
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_items(client):
    response = client.get("/items")
    assert response.status_code == 200
```

## Override with state

```python
test_db = []


def fake_get_db():
    return test_db


def test_with_state():
    app.dependency_overrides[get_db] = fake_get_db
    client = TestClient(app)

    # Test data is managed in test state
    test_db.clear()
    test_db.append({"name": "test"})

    response = client.get("/items")
    assert response.status_code == 200
    app.dependency_overrides.clear()
```

## Multiple overrides

```python
def test_full_override():
    app.dependency_overrides = {
        get_db: lambda: {"db": "mock"},
        get_current_user: lambda: {"username": "tester"},
        send_email: lambda *a, **kw: None,
    }
    with TestClient(app) as client:
        ...
    app.dependency_overrides.clear()
```

## Override context manager helper

```python
from contextlib import contextmanager


@contextmanager
def override_deps(app, **overrides):
    app.dependency_overrides.update(overrides)
    try:
        yield
    finally:
        app.dependency_overrides.clear()


def test_with_helper():
    with override_deps(app, get_db=fake_db):
        with TestClient(app) as client:
            ...
```

See [dependency-override-testing.md](./dependency-override-testing.md) for basic override setup.
