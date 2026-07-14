---
title: "Cookie Parameters"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - cookies
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/cookie-params/"
    title: "FastAPI Docs — Cookie Parameters"
last_audit_date: 2026-06-09
---

# Cookie Parameters

Read cookies from incoming requests using `Cookie()`:

```python
from fastapi import FastAPI, Cookie

app = FastAPI()


@app.get("/items")
async def read_items(session_id: str | None = Cookie(default=None)):
    return {"session_id": session_id}
```

## How it works

- `Cookie()` is a special function similar to `Query()` and `Header()`
- It extracts the named cookie from the `Cookie` request header
- Supports the same validation parameters as `Query()`:
  - `default` / `default=None` for optional cookies
  - `min_length`, `max_length`, `pattern`
  - `alias` to map to a different cookie name

## Required vs optional

```python
# Optional cookie
session_id: str | None = Cookie(default=None)

# Required cookie
session_token: str = Cookie()
```

## Type coercion

Cookie values are strings; FastAPI coerces to declared types (`int`, `bool`, etc.).

See [response-cookies.md](./response-cookies.md) for setting cookies and [query-parameters-str-validation.md](./query-parameters-str-validation.md) for similar validation patterns.
