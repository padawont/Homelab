---
title: "Testing — Authentication"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testing
  - authentication
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/testing/"
    title: "FastAPI Docs — Testing"
last_audit_date: 2026-06-09
---

# Testing — Authentication

Test endpoints requiring authentication headers:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_with_bearer_token():
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer test-token-123"},
    )
    assert response.status_code == 200
```

## Testing unauthorized access

```python
def test_unauthorized():
    response = client.get("/users/me")
    assert response.status_code == 401
```

## Multiple auth headers

```python
def test_with_api_key():
    response = client.get(
        "/admin/dashboard",
        headers={
            "X-API-Key": "admin-key-456",
            "Authorization": "Bearer test-token",
        },
    )
    assert response.status_code == 200
```

## Cookie-based auth

```python
def test_with_cookie():
    response = client.get(
        "/items",
        cookies={"session_id": "abc123"},
    )
    assert response.status_code == 200
```

## Using dependency overrides for auth

```python
from main import app, get_current_user


def test_with_mock_auth():
    def fake_get_current_user():
        return {"username": "test_user", "role": "admin"}

    app.dependency_overrides[get_current_user] = fake_get_current_user

    with TestClient(app) as client:
        response = client.get("/users/me")
        assert response.json() == {"username": "test_user", "role": "admin"}

    app.dependency_overrides.clear()
```

See [dependency-override-testing.md](./dependency-override-testing.md) for more on overrides and [security-oauth2-password.md](./security-oauth2-password.md) for OAuth2 patterns.
