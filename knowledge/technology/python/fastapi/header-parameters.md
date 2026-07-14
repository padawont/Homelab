---
title: "Header Parameters"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - headers
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/header-params/"
    title: "FastAPI Docs — Header Parameters"
last_audit_date: 2026-06-09
---

# Header Parameters

Read HTTP headers from incoming requests using `Header()`:

```python
from fastapi import FastAPI, Header

app = FastAPI()


@app.get("/items")
async def read_items(
    user_agent: str | None = Header(default=None),
    x_token: str | None = Header(default=None, alias="X-Token"),
):
    return {"User-Agent": user_agent, "X-Token": x_token}
```

## Header conversion

- Header names are case-insensitive per HTTP spec
- FastAPI converts `_` to `-` automatically (no capitalization): `user_agent` → `user-agent`
- HTTP header matching is case-insensitive per the HTTP spec, so `user-agent` matches `User-Agent` at the protocol level
- Use `alias` for non-standard or mixed-case headers when you need exact control

## Duplicate headers

```python
@app.get("/items")
async def read_items(x_tags: list[str] = Header(default=[])):
    return {"X-Tags": x_tags}
```

Duplicate headers with the same name are collected into a list.

## Validation

Supports the same validators as `Query()`: `min_length`, `max_length`, `pattern`, etc.

See [query-parameters-str-validation.md](./query-parameters-str-validation.md) for string validation details.
