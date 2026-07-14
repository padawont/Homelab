---
title: "Security — API Key"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - security
  - api-key
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/security/api-key-security/"
    title: "FastAPI Docs — API Key Security"
last_audit_date: 2026-06-09
---

# Security — API Key

Authenticate using API keys in headers or query params:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader, APIKeyQuery

app = FastAPI()

API_KEY = "secret-api-key-123"

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def verify_api_key(
    api_key_header: str | None = Depends(api_key_header),
    api_key_query: str | None = Depends(api_key_query),
):
    api_key = api_key_header or api_key_query
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing",
        )
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return api_key


@app.get("/secure-data")
async def secure_data(api_key: str = Depends(verify_api_key)):
    return {"data": "protected"}
```

## Available API key schemes

| Scheme | Location |
|---|---|
| `APIKeyHeader(name="X-API-Key")` | HTTP header |
| `APIKeyQuery(name="api_key")` | Query parameter |
| `APIKeyCookie(name="session")` | Cookie |

## `auto_error` parameter

- `auto_error=True` (default) — returns `403` automatically
- `auto_error=False` — returns `None` if missing (let your handler decide)

See [security-oauth2-password.md](./security-oauth2-password.md) for OAuth2 bearer flow and [security-jwt.md](./security-jwt.md) for JWT.
