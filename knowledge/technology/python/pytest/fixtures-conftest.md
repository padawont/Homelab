---
title: "Sharing Fixtures with conftest.py"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - fixtures
  - conftest
sources:
  - url: "https://docs.pytest.org/en/stable/how-to/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files"
    title: "pytest conftest.py — Sharing Fixtures"
last_audit_date: 2026-06-09
---

# Sharing Fixtures with conftest.py

Place shared fixtures in `conftest.py` files to make them available across multiple test modules without importing.

## How It Works

pytest automatically discovers `conftest.py` files in each test directory. Fixtures defined there are available to all tests in that directory and its subdirectories.

```python
# tests/conftest.py
import pytest

@pytest.fixture
def api_client():
    from myapp import create_app
    app = create_app()
    return app.test_client()
```

```python
# tests/test_users.py  — no import needed
def test_get_user(api_client):
    resp = api_client.get("/users/1")
    assert resp.status_code == 200
```

## Hierarchy

Conftest fixtures are scoped by directory level — a fixture in `tests/unit/conftest.py` overrides one in `tests/conftest.py`.

## Best Practices

- Use conftest for widely shared fixtures (DB, client, config).
- Keep conftest files focused — split into multiple files if needed.
- See [conftest-intro](./conftest-intro.md) for more on what conftest does.
