---
title: "Sub-Dependencies"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - dependency-injection
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/"
    title: "FastAPI Docs — Sub-Dependencies"
last_audit_date: 2026-06-09
---

# Sub-Dependencies

Dependencies can themselves depend on other dependencies:

```python
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI()


def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return current_user


@app.get("/admin/dashboard")
async def dashboard(admin: dict = Depends(get_admin_user)):
    return {"admin": admin["username"], "dashboard": "secure data"}
```

## Dependency graph

```
get_admin_user
  └── get_current_user
        └── oauth2_scheme
```

FastAPI builds the full graph automatically and resolves each dependency once per request.

## Caching

FastAPI caches dependency results per request — the same dependency is never called twice in the same request regardless of how many paths reference it.

## Reusability

Sub-dependencies make it easy to compose fine-grained checks:

```python
def verify_token(...) -> User
def require_role(role: str) -> Depends callable
def require_active(...) -> User
```

See [dependency-functions.md](./dependency-functions.md) and [dependency-global.md](./dependency-global.md) for other DI patterns.
