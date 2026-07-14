---
title: "Testing — Query String Endpoints"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testing
  - query-parameters
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/testing/"
    title: "FastAPI Docs — Testing"
last_audit_date: 2026-06-09
---

# Testing — Query String Endpoints

Test endpoints that accept query parameters:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_list_items_with_query_params():
    response = client.get("/items", params={"skip": 0, "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5
```

## Using `params=` dictionary

```python
# Instead of building the query string manually
client.get("/items?skip=0&limit=5")

# Use params dict (preferred)
client.get("/items", params={"skip": 0, "limit": 5, "q": "search"})
```

## Testing optional params

```python
def test_without_optional_params():
    response = client.get("/items")  # No query params
    assert response.status_code == 200


def test_with_some_params():
    response = client.get("/items", params={"q": "Foo"})
    assert response.status_code == 200
```

## Testing validation

```python
def test_invalid_query_param():
    # Param exceeds validation constraints
    response = client.get("/items", params={"q": "a"})  # min_length=3
    assert response.status_code == 422
```

See [query-parameters.md](./query-parameters.md) for query parameter definitions and [query-parameters-str-validation.md](./query-parameters-str-validation.md) for validation.
