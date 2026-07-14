---
title: "Response Cookies"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - response
  - cookies
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/response-cookies/"
    title: "FastAPI Docs — Response Cookies"
last_audit_date: 2026-06-09
---

# Response Cookies

Set cookies on the response:

```python
from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/set-cookie")
async def set_cookie(response: Response):
    response.set_cookie(
        key="session_id",
        value="abc123",
        max_age=3600,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {"message": "cookie set"}
```

## `Response.set_cookie()` parameters

| Parameter | Purpose |
|---|---|
| `key` | Cookie name |
| `value` | Cookie value |
| `max_age` | Lifetime in seconds |
| `expires` | Datetime of expiry |
| `path` | URL path scope (default `/`) |
| `domain` | Domain scope |
| `secure` | HTTPS only |
| `httponly` | JavaScript inaccessible |
| `samesite` | `"lax"`, `"strict"`, or `"none"` |

## Deleting cookies

```python
response.delete_cookie("session_id")
```

See [cookie-parameters.md](./cookie-parameters.md) for reading cookies from requests and [response-headers.md](./response-headers.md) for custom headers.
