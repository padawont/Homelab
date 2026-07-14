---
title: "Redirect Response"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - response
  - redirect
sources:
  - url: "https://fastapi.tiangolo.com/advanced/custom-response/#redirectresponse"
    title: "FastAPI Docs — RedirectResponse"
last_audit_date: 2026-06-09
---

# Redirect Response

Redirect clients to another URL:

```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/old-page")
async def redirect_old():
    return RedirectResponse(url="/new-page")


@app.get("/external")
async def redirect_external():
    return RedirectResponse(url="https://example.com")
```

## Status codes

```python
from fastapi import status

# Temporary redirect (default)
return RedirectResponse(url="/new", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

# Permanent redirect
return RedirectResponse(url="/new", status_code=status.HTTP_301_MOVED_PERMANENTLY)

# See Other (redirect after POST)
return RedirectResponse(url="/success", status_code=status.HTTP_303_SEE_OTHER)
```

## Redirect codes

| Code | Constant | Meaning |
|---|---|---|
| 301 | `HTTP_301_MOVED_PERMANENTLY` | Resource moved, update bookmarks |
| 302 | `HTTP_302_FOUND` | Temporary redirect (default in some clients) |
| 303 | `HTTP_303_SEE_OTHER` | Redirect via GET (after POST) |
| 307 | `HTTP_307_TEMPORARY_REDIRECT` | Preserve HTTP method |
| 308 | `HTTP_308_PERMANENT_REDIRECT` | Preserve method, permanent |

## 307 vs 302

- 307 preserves the original HTTP method (POST→POST)
- 302 may change POST to GET (per browser behavior)

## Relative redirects

```python
@app.get("/docs/latest")
async def latest_docs():
    return RedirectResponse(url="./v2/")
```

See [response-status-code.md](./response-status-code.md) for other status code patterns.
