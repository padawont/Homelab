---
title: "Testing — TestClient Setup"
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

# Testing — TestClient Setup

Test FastAPI applications using Starlette's `TestClient`:

```python
# test_main.py
from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

## Requirements

```bash
uv add httpx
```

`TestClient` requires `httpx` for making requests.

## Running tests

```bash
uv run pytest test_main.py -v
```

## Key methods

| Method | Usage |
|---|---|
| `client.get(url, params=..., headers=...)` | GET |
| `client.post(url, json=..., data=...)` | POST |
| `client.put(url, json=...)` | PUT |
| `client.delete(url)` | DELETE |
| `client.patch(url, json=...)` | PATCH |

## Response assertions

```python
response = client.get("/items")
assert response.status_code == 200
assert response.json() == [{"name": "Foo"}]
assert response.headers["content-type"] == "application/json"
```

See [testing-testclient-call.md](./testing-testclient-call.md) for context manager usage and [testing-json-params.md](./testing-json-params.md) for JSON testing patterns.
