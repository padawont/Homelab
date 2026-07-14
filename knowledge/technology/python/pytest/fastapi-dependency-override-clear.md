---
title: "Clearing Dependency Overrides"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testing
  - dependency-injection
sources:
  - url: "https://fastapi.tiangolo.com/advanced/testing-dependencies/"
    title: "FastAPI — Testing Dependencies"
last_audit_date: 2026-06-09
---

# Clearing Dependency Overrides

Always clear `app.dependency_overrides` after tests to avoid cross-test contamination.

## The Problem

```python
def test_one(client):
    app.dependency_overrides[get_user] = lambda: mock_user_a()
    # ... test passes

def test_two(client):
    # Still has the override from test_one!
    # Expected default user but got mock_user_a()
```

## Manual Cleanup

```python
def test_with_override(client):
    app.dependency_overrides[get_db] = lambda: test_db
    try:
        response = client.get("/items")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()
```

## Fixture-Based Cleanup (Recommended)

```python
@pytest.fixture
def override_db():
    app.dependency_overrides[get_db] = lambda: test_db
    yield
    app.dependency_overrides.clear()

def test_with_db_override(client, override_db):
    response = client.get("/items")
    assert response.status_code == 200
```

## Autouse Fixture

```python
@pytest.fixture(autouse=True)
def clear_overrides():
    """Clear any leftover overrides before each test."""
    app.dependency_overrides.clear()
```

## Selective Clear

```python
# Clear only a specific override
del app.dependency_overrides[get_db]

# Or pop it
app.dependency_overrides.pop(get_db, None)
```

See [fastapi-dependency-override-single](./fastapi-dependency-override-single.md) for the override pattern.
