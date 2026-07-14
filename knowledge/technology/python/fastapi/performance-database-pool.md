---
title: "Performance — Database Connection Pooling"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - performance
  - database
sources:
  - url: "https://fastapi.tiangolo.com/"
    title: "FastAPI Documentation"
last_audit_date: 2026-06-09
---

# Performance — Database Connection Pooling

Use connection pools to avoid per-request connection overhead:

## Async SQLAlchemy

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
```

## Using the pool in endpoints

```python
from fastapi import Depends
from sqlalchemy import select


@app.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

## Pool configuration

| Parameter | Purpose | Recommendation |
|---|---|---|
| `pool_size` | Base pool connections | 10–20 per worker |
| `max_overflow` | Extra connections past `pool_size` | 5–10 |
| `pool_pre_ping` | Health check on checkout | `True` |
| `pool_recycle` | Max connection age (seconds) | 3600 |

## Redis connection pool

```python
import redis.asyncio as redis

redis_pool = redis.ConnectionPool(
    host="localhost",
    port=6379,
    max_connections=20,
)


async def get_redis():
    return redis.Redis(connection_pool=redis_pool)
```

See [app-lifecycle.md](./app-lifecycle.md) for pool initialization in the lifespan and [performance-async-paths.md](./performance-async-paths.md) for non-blocking route patterns.
