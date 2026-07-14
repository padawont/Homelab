---
title: "Security — OAuth2 Scopes"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - security
  - scopes
sources:
  - url: "https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/"
    title: "FastAPI Docs — OAuth2 Scopes"
last_audit_date: 2026-06-09
---

# Security — OAuth2 Scopes

Implement fine-grained permissions with OAuth2 scopes:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    scopes={
        "items:read": "Read items",
        "items:write": "Write items",
        "admin": "Admin access",
    },
)


async def verify_scopes(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
):
    # Decode token and extract scopes
    payload = decode_token(token)
    token_scopes = payload.get("scopes", [])

    # Check all required scopes are present
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing scope: {scope}",
            )
    return payload


@app.get("/items", dependencies=[Depends(verify_scopes)])
async def list_items():
    return [{"name": "Foo"}]


@app.post("/items", dependencies=[Depends(verify_scopes)])
async def create_item():
    return {"message": "created"}
```

## Scopes in `SecurityScopes`

`SecurityScopes` is injected with the required scopes for each route. It populates OpenAPI documentation automatically.

## Token with scopes

```python
def create_token(user: str, scopes: list[str]) -> str:
    return jwt.encode(
        {"sub": user, "scopes": scopes, "exp": expire},
        SECRET_KEY,
    )
```

See [security-jwt.md](./security-jwt.md) for JWT creation and [security-oauth2-password.md](./security-oauth2-password.md) for the login flow.
