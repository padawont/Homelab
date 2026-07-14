---
title: "Testing — JSON Request/Response Endpoints"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testing
  - json
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/testing/"
    title: "FastAPI Docs — Testing"
last_audit_date: 2026-06-09
---

# Testing — JSON Request/Response Endpoints

Test endpoints with JSON request bodies:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_item():
    payload = {
        "name": "Foo",
        "price": 42.0,
        "description": "A foo item",
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Foo"
    assert data["price"] == 42.0
```

## Testing validation errors

```python
def test_invalid_item():
    response = client.post("/items", json={"name": "Foo"})  # missing price
    assert response.status_code == 422
    error_data = response.json()
    assert error_data["detail"][0]["loc"] == ["body", "price"]
```

## `json=` vs `data=`

| Parameter | Content-Type | Use case |
|---|---|---|
| `json=` | `application/json` | Sends serialized JSON |
| `data=` | Varies | Form data, raw bytes |

## Response assertions

```python
def test_response_shape():
    response = client.get("/items/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert isinstance(data["name"], str)
```

See [testing-testclient-intro.md](./testing-testclient-intro.md) for TestClient setup and [testing-query-params.md](./testing-query-params.md) for query string testing.
