---
title: "Response Headers"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - response
  - headers
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/response-headers/"
    title: "FastAPI Docs — Response Headers"
last_audit_date: 2026-06-09
---

# Response Headers

Set custom headers on responses:

```python
from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: int, response: Response):
    response.headers["X-Item-Version"] = "2.0"
    response.headers["X-Cache-Hit"] = "true"
    return {"item_id": item_id}
```

## Using `Response` parameter

Inject `Response` into the handler to modify headers, status code, or media type.

## Headers via `JSONResponse`

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/headers")
async def custom_headers():
    return JSONResponse(
        content={"message": "ok"},
        headers={"X-Custom": "value"},
    )
```

## Namespacing

Custom headers conventionally use the `X-` prefix (though this is deprecated by RFC 6648 — many APIs still use it).

See [response-cookies.md](./response-cookies.md) for setting cookies and [response-status-code.md](./response-status-code.md) for status codes.
