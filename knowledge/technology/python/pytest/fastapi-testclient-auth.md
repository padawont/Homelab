---
title: "Auth Header Patterns with TestClient"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testclient
  - authentication
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/testing/"
    title: "FastAPI Testing Guide"
last_audit_date: 2026-06-09
---

# Auth Header Patterns with TestClient

Common patterns for passing authentication in tests.

## Bearer Token

```python
def test_bearer_token(client):
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer test-token-123"},
    )
    assert response.status_code == 200
```

## API Key Header

```python
def test_api_key(client):
    response = client.get("/resources", headers={"X-API-Key": "test-key"})
    assert response.status_code == 200
```

## Basic Auth

```python
from requests.auth import HTTPBasicAuth  # Not recommended — use headers instead

def test_basic_auth(client):
    import base64
    creds = base64.b64encode(b"user:pass").decode()
    response = client.get("/basic-auth", headers={"Authorization": f"Basic {creds}"})
```

## Cookie-Based Auth

```python
def test_cookie_auth(client):
    # Login first
    client.post("/login", json={"user": "alice", "pass": "secret"})
    # Cookie is stored and sent automatically
    response = client.get("/profile")
    assert response.status_code == 200
```

## Fixture for Auth

```python
@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

def test_with_auth_fixture(client, auth_headers):
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 200
```

See [fastapi-dependency-override-single](./fastapi-dependency-override-single.md) for overriding auth dependencies directly.
