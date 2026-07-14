---
title: "Async Fixtures for Database Setup/Teardown"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest-asyncio
  - fixtures
  - database
  - async
sources:
  - url: "https://pytest-asyncio.readthedocs.io/en/latest/concepts.html#async-fixtures"
    title: "pytest-asyncio — Async Fixtures"
last_audit_date: 2026-06-09
---

# Async Fixtures for Database Setup/Teardown

Use async fixtures to manage database connections and transactions.

## Connection Fixture

```python
import pytest_asyncio

@pytest_asyncio.fixture
async def db():
    conn = await asyncpg.connect(
        user="test", database="testdb"
    )
    yield conn
    await conn.close()
```

## Transaction Rollback Pattern

```python
@pytest_asyncio.fixture
async def db_session(db):
    async with db.transaction():
        yield db  # rolled back after test
```

## Session-Scoped Pool

```python
@pytest_asyncio.fixture(scope="session")
async def db_pool():
    pool = await asyncpg.create_pool(dsn="postgresql://test:test@localhost/testdb")
    yield pool
    await pool.close()

@pytest_asyncio.fixture
async def db(db_pool):
    async with db_pool.acquire() as conn:
        yield conn
```

## SQLAlchemy Async

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with AsyncSession(engine) as session:
        yield session
```

See [pytest-asyncio-scope](./pytest-asyncio-scope.md) for session scoping considerations and [async-fixtures-temporary-data](./async-fixtures-temporary-data.md) for test data creation.
