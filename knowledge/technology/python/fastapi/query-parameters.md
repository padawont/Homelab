---
title: "Query Parameters"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - query-parameters
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/query-params/"
    title: "FastAPI Docs — Query Parameters"
last_audit_date: 2026-06-09
---

# Query Parameters

Function parameters not declared in the path are automatically interpreted as query parameters:

```python
from fastapi import FastAPI

app = FastAPI()

fake_db = [{"name": f"Item {i}"} for i in range(10)]


@app.get("/items")
async def list_items(skip: int = 0, limit: int = 10):
    return fake_db[skip : skip + limit]
```

## Default values

Parameters with defaults are optional:

```python
async def list_items(skip: int = 0, limit: int = 10):
```

- Request `GET /items?skip=0&limit=5` → `skip=0`, `limit=5`
- Request `GET /items` → `skip=0`, `limit=10`

## Required query parameters

Omit the default to make it required:

```python
@app.get("/items")
async def search_items(q: str):
    return {"q": q}
```

Without `?q=...`, FastAPI returns a `422` validation error.

## Type coercion

Query strings are strings; FastAPI coerces to the declared type (`int`, `bool`, `float`, etc.).

For string validation (min_length, regex), see [query-parameters-str-validation.md](./query-parameters-str-validation.md).
