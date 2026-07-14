---
title: "Security — OAuth2 Password Flow"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - security
  - oauth2
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/"
    title: "FastAPI Docs — Simple OAuth2"
last_audit_date: 2026-06-09
---

# Security — OAuth2 Password Flow

Use `OAuth2PasswordBearer` for token-based auth:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def fake_decode_token(token: str) -> dict:
    return {"username": token}


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate credentials, return JWT
    return {"access_token": form_data.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    current_user = fake_decode_token(token)
    return current_user
```

## `OAuth2PasswordBearer`

- Extracts the `Bearer` token from `Authorization` header
- Auto-adds `401` response to OpenAPI docs
- `tokenUrl` points to the login endpoint

## `OAuth2PasswordRequestForm`

- Parses `username` and `password` from form data
- Optional fields: `scope`, `grant_type`, `client_id`, `client_secret`

## Full implementation

For production, pair with [security-jwt.md](./security-jwt.md) for JWT token creation and verification. See also [security-api-key.md](./security-api-key.md) for API key auth.
