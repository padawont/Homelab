---
title: "Autouse Fixtures"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - fixtures
  - autouse
sources:
  - url: "https://docs.pytest.org/en/stable/how-to/fixtures.html#autouse-fixtures"
    title: "pytest Autouse Fixtures"
last_audit_date: 2026-06-09
---

# Autouse Fixtures

Set `autouse=True` to make a fixture run automatically for all tests in its scope without explicit declaration.

## Basic Pattern

```python
@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    # Every test in this module runs with the patched env
```

## Common Use Cases

- Environment variable setup
- Temporary directory creation
- Database transaction wrapping
- Mocking external services

## Scope Control

Control how often the autouse fixture fires via the `scope` parameter:

```python
@pytest.fixture(autouse=True, scope="session")
def global_config():
    """Runs once for the entire test session."""
    configure_logging()
```

## Visibility

An autouse fixture defined in a `conftest.py` applies to all tests in that directory and subdirectories automatically.

See [fixtures-conftest](./fixtures-conftest.md) for sharing autouse fixtures across modules.
