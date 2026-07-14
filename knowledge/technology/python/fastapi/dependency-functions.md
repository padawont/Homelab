---
title: "Dependency Functions"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - dependency-injection
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/dependencies/"
    title: "FastAPI Docs — Dependencies"
last_audit_date: 2026-06-09
---

# Dependency Functions

Any callable can be a dependency. The most common form is a plain function:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def verify_token(token: str = Depends(oauth2_scheme)):
    # In practice, decode JWT here
    if token != "valid-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return {"username": "alice"}


@app.get("/users/me")
async def read_current_user(current_user: dict = Depends(verify_token)):
    return current_user
```

## Dependency patterns

| Pattern | Use case |
|---|---|
| Extract + validate token | `verify_token` |
| Get DB session | `get_db()` with yield |
| Parse common query params | `pagination(skip, limit)` |
| Permission checks | `require_admin(current_user)` |
| Rate limiting | `check_rate_limit(request)` |

## Async dependencies

```python
async def get_db():
    # async database session
    ...
```

FastAPI supports both `async def` and `def` in dependencies — same rules as path handlers.

See [dependency-injection-intro.md](./dependency-injection-intro.md) for the core concept and [dependency-classes.md](./dependency-classes.md) for class-based dependencies.
