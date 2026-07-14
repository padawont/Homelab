---
title: "FastAPI TestClient"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testclient
  - testing
  - starlette
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/testing/"
    title: "FastAPI Testing Guide"
last_audit_date: 2026-06-09
---

# FastAPI TestClient

FastAPI ships with `TestClient` from Starlette for synchronous HTTP testing.

## Basic Usage

```python
from fastapi.testclient import TestClient
from myapp import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
```

## Supported Methods

```python
client.get("/url")
client.post("/url", json={...})
client.put("/url", json={...})
client.patch("/url", json={...})
client.delete("/url")
client.options("/url")
client.head("/url")
```

## How It Works

`TestClient` wraps [httpx](https://www.python-httpx.org/) internally. Requests are made directly to the ASGI app without a live server.

## Context Manager

Use the `with` statement for better lifecycle management:

```python
def test_with_context():
    with TestClient(app) as client:
        resp = client.get("/")
        assert resp.status_code == 200
```

See [fastapi-testclient-context](./fastapi-testclient-context.md) for more context patterns.
