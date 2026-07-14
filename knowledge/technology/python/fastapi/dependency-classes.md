---
title: "Dependency Classes"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - dependency-injection
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/"
    title: "FastAPI Docs — Classes as Dependencies"
last_audit_date: 2026-06-09
---

# Dependency Classes

Use classes (or `__call__` objects) as dependencies:

```python
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI()


class AdminChecker:
    def __init__(self, required_role: str = "admin"):
        self.required_role = required_role

    def __call__(self, user_id: int | None = None):
        if user_id is None or user_id < 1:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return {"user_id": user_id, "role": self.required_role}


admin_check = AdminChecker()


@app.get("/admin")
async def admin_route(current_user: dict = Depends(admin_check)):
    return current_user
```

## Using `__init__` for configuration

Dependencies with parameters via `__init__`:

```python
class Pagination:
    def __init__(self, default_limit: int = 10):
        self.default_limit = default_limit

    def __call__(self, skip: int = 0, limit: int | None = None):
        return {"skip": skip, "limit": limit or self.default_limit}


pagination = Pagination(default_limit=20)
```

## Yield (cleanup) in class dependencies

Use context manager protocol for setup/teardown:

```python
class DBSession:
    async def __call__(self):
        session = await create_session()
        try:
            yield session
        finally:
            await session.close()
```

See [dependency-functions.md](./dependency-functions.md) for function-based dependencies and [dependency-sub-dependencies.md](./dependency-sub-dependencies.md) for nesting.
