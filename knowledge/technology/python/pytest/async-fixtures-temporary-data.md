---
title: "Test Data Creation Patterns"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest-asyncio
  - fixtures
  - test-data
  - async
sources:
  - url: "https://pytest-asyncio.readthedocs.io/en/latest/concepts.html#async-fixtures"
    title: "pytest-asyncio — Async Fixtures"
last_audit_date: 2026-06-09
---

# Test Data Creation Patterns

Create and clean up temporary test data with async fixtures.

## Single Record

```python
@pytest_asyncio.fixture
async def test_user(db):
    user = await db.execute(
        "INSERT INTO users (name) VALUES ('test') RETURNING id"
    )
    user_id = user.scalar()
    yield user_id
    await db.execute("DELETE FROM users WHERE id = $1", user_id)
```

## Factory Fixture Pattern

```python
@pytest_asyncio.fixture
async def create_user(db):
    created_ids = []

    async def _make(name="default", role="viewer"):
        result = await db.execute(
            "INSERT INTO users (name, role) VALUES ($1, $2) RETURNING id",
            name, role,
        )
        user_id = result.scalar()
        created_ids.append(user_id)
        return user_id

    yield _make

    # Cleanup all created users
    for uid in created_ids:
        await db.execute("DELETE FROM users WHERE id = $1", uid)
```

## Using the Factory

```python
@pytest.mark.asyncio
async def test_multiple_users(create_user):
    alice = await create_user("alice", "admin")
    bob = await create_user("bob", "viewer")
    assert alice != bob
```

## Bulk Data

```python
@pytest_asyncio.fixture
async def seed_data(db):
    for i in range(10):
        await db.execute("INSERT INTO items (name) VALUES ($1)", f"item-{i}")
    yield
    await db.execute("DELETE FROM items")
```

See [async-fixtures-database](./async-fixtures-database.md) for database connection fixtures and [fixtures-scope](./fixtures-scope.md) for scoping considerations.
