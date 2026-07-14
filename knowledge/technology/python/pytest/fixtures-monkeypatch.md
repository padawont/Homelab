---
title: "Monkeypatching with monkeypatch"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - fixtures
  - monkeypatch
  - mocking
sources:
  - url: "https://docs.pytest.org/en/stable/how-to/monkeypatch.html"
    title: "pytest monkeypatch Fixture"
last_audit_date: 2026-06-09
---

# Monkeypatching with monkeypatch

The built-in `monkeypatch` fixture safely modifies objects, environment variables, and dictionaries for the duration of a test.

## Common Operations

```python
def test_monkeypatch(monkeypatch):
    # Patch an attribute
    monkeypatch.setattr("os.getcwd", lambda: "/fake/path")

    # Patch a dictionary
    import os
    monkeypatch.setitem(os.environ, "DATABASE_URL", "sqlite:///test.db")

    # Set an environment variable
    monkeypatch.setenv("DEBUG", "true")

    # Delete an environment variable
    monkeypatch.delenv("SECRET_KEY", raising=False)
```

## Undo Behavior

All changes are automatically reverted after the test function finishes. No manual cleanup needed.

## Using with Context Managers

```python
def test_with_monkeypatch_context(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)
    # time.sleep becomes a no-op for this test
```

## Best Practices

- Prefer `monkeypatch.setattr` over manual mock objects for simple cases.
- Use `monkeypatch.context()` to scope changes to a block within a test.
- For HTTP mocking, use `pytest-vcr` (see [pytest-vcr-fixtures](./pytest-vcr-fixtures.md)).
