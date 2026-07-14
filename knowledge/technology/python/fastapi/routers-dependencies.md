---
title: "Router Dependencies"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - routers
  - dependency-injection
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/bigger-applications/#import-apirouter"
    title: "FastAPI Docs — Router Dependencies"
last_audit_date: 2026-06-09
---

# Router Dependencies

Apply global dependencies to all routes on a router:

```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()


async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return authorization.split(" ")[1]


@router.get("/items")
async def list_items(token: str = Depends(verify_token)):
    return [{"name": "Foo"}]


# Or apply to all routes on this router:
router = APIRouter(dependencies=[Depends(verify_token)])


@router.get("/items")
async def list_items():
    return [{"name": "Foo"}]


@router.post("/items")
async def create_item():
    return {"message": "created"}
```

## Dependency cascade

Router deps → Path operation deps:

```
Request
  → Router-level dependencies (verify_token)
    → Path-level dependencies (get_db)
      → Handler
```

## Multiple routers, different deps

```python
public_router = APIRouter()                                # No auth
admin_router = APIRouter(dependencies=[Depends(verify_admin)])  # Auth required
internal_router = APIRouter(dependencies=[Depends(verify_internal)])  # Internal

app.include_router(public_router)
app.include_router(admin_router, prefix="/admin")
app.include_router(internal_router, prefix="/internal")
```

See [routers.md](./routers.md) for APIRouter setup and [dependency-global.md](./dependency-global.md) for app-level deps.
