---
title: "Single Dependency Override"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testing
  - dependency-injection
sources:
  - url: "https://fastapi.tiangolo.com/advanced/testing-dependencies/"
    title: "FastAPI — Testing Dependencies"
last_audit_date: 2026-06-09
---

# Single Dependency Override

Override a FastAPI dependency in tests using `app.dependency_overrides`.

## Basic Pattern

```python
from myapp import app, get_current_user

def override_get_current_user():
    return {"username": "testuser", "role": "admin"}

app.dependency_overrides[get_current_user] = override_get_current_user

def test_protected_endpoint(client):
    response = client.get("/protected")
    assert response.status_code == 200
    assert response.json()["user"] == "testuser"
```

## With Fixtures

```python
import pytest
from myapp import app, get_db

@pytest.fixture
def test_db():
    db = create_test_database()
    yield db
    drop_test_database()

@pytest.fixture(autouse=True)
def override_db(test_db):
    app.dependency_overrides[get_db] = lambda: test_db
    yield
    app.dependency_overrides.clear()
```

## Override in TestFile

```python
def test_with_specific_override(client):
    app.dependency_overrides[get_settings] = lambda: Settings(debug=True)
    response = client.get("/settings")
    assert response.json()["debug"] is True
```

Always clean up after overriding — see [fastapi-dependency-override-clear](./fastapi-dependency-override-clear.md).
