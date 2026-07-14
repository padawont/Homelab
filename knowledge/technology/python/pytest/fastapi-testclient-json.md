---
title: "Sending and Receiving JSON"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testclient
  - json
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/testing/"
    title: "FastAPI Testing Guide"
last_audit_date: 2026-06-09
---

# Sending and Receiving JSON

TestClient handles JSON serialization and deserialization automatically.

## Sending JSON

```python
def test_create_item(client):
    response = client.post(
        "/items",
        json={"name": "Widget", "price": 9.99},
    )
    assert response.status_code == 201
```

The `json` parameter automatically sets `Content-Type: application/json` and serializes the dict.

## Receiving JSON

```python
def test_get_item(client):
    response = client.get("/items/1")
    data = response.json()
    assert data["name"] == "Widget"
    assert data["price"] == 9.99
```

## Sending Non-Dict JSON

```python
response = client.post("/items/bulk", json=[{"name": "A"}, {"name": "B"}])
```

## With Custom Status Codes

```python
def test_create_duplicate(client):
    client.post("/items", json={"name": "Widget"})
    response = client.post("/items", json={"name": "Widget"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Item already exists"
```

## Raw Data

For non-JSON payloads, use `content` instead of `json`:

```python
response = client.post("/upload", content=b"raw data", headers={"Content-Type": "text/plain"})
```

See [fastapi-testclient-headers](./fastapi-testclient-headers.md) for custom header patterns.
