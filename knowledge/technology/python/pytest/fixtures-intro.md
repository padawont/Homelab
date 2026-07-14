---
title: "Introduction to pytest Fixtures"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - fixtures
  - testing
sources:
  - url: "https://docs.pytest.org/en/stable/how-to/fixtures.html"
    title: "pytest Fixtures Documentation"
last_audit_date: 2026-06-09
---

# Introduction to pytest Fixtures

Fixtures provide a modular, reusable way to set up and tear down test dependencies.

## Defining a Fixture

```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "Alice", "score": 42}

def test_with_fixture(sample_data):
    assert sample_data["name"] == "Alice"
```

## Yield Fixtures (Setup / Teardown)

```python
@pytest.fixture
def db_connection():
    conn = create_connection()       # setup
    yield conn
    conn.close()                     # teardown
```

Code before `yield` runs as setup; code after `yield` runs as teardown, even if the test raises an exception.

## Fixture Requesting Fixtures

Fixtures can depend on other fixtures by declaring them as parameters:

```python
@pytest.fixture
def user(db_connection):
    return create_user(db_connection)

def test_user(user):
    assert user.is_active
```

See also: [fixtures-conftest](./fixtures-conftest.md), [fixtures-scope](./fixtures-scope.md), [fixtures-autouse](./fixtures-autouse.md).
