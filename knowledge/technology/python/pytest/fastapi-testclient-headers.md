---
title: "Setting Headers on TestClient"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testclient
  - headers
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/testing/"
    title: "FastAPI Testing Guide"
last_audit_date: 2026-06-09
---

# Setting Headers on TestClient

Pass custom headers to `TestClient` requests.

## Per-Request Headers

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_with_headers():
    headers = {"X-Custom-Header": "value", "Accept": "application/json"}
    response = client.get("/items", headers=headers)
    assert response.status_code == 200
```

## Default Headers via TestClient Instance

```python
def test_default_headers():
    with TestClient(app, headers={"X-API-Key": "test-key"}) as client:
        # All requests use the default headers
        resp1 = client.get("/items")
        resp2 = client.post("/items", json={"name": "foo"})
```

## Merging

Per-request headers merge with default headers. Per-request values override defaults for the same key.

## Header for Authentication

```python
# Bearer token pattern
response = client.get(
    "/protected",
    headers={"Authorization": "Bearer test-token"}
)
```

See [fastapi-testclient-auth](./fastapi-testclient-auth.md) for auth-specific patterns and [fastapi-testclient-cookies](./fastapi-testclient-cookies.md) for cookie handling.
