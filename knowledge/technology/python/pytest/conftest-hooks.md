---
title: "conftest.py Hooks"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - conftest
  - hooks
sources:
  - url: "https://docs.pytest.org/en/stable/reference/reference.html#hooks"
    title: "pytest Hooks Reference"
last_audit_date: 2026-06-09
---

# conftest.py Hooks

pytest hooks allow you to run code at various stages of the test lifecycle. Implement them in `conftest.py`.

## Common Hooks

```python
# conftest.py
import pytest

def pytest_runtest_setup(item):
    """Called before each test item is executed."""
    print(f"Setting up: {item.name}")

def pytest_runtest_teardown(item, nextitem):
    """Called after each test item finishes."""
    print(f"Tearing down: {item.name}")

def pytest_runtest_call(item):
    """Called to execute the test itself."""
    pass

def pytest_sessionstart(session):
    """Called before the test session begins."""
    configure_test_database()

def pytest_sessionfinish(session, exitstatus):
    """Called after the test session ends."""
    cleanup_test_resources()
```

## Adding CLI Options

```python
def pytest_addoption(parser):
    parser.addoption(
        "--db-url", action="store", default="sqlite://",
        help="Database URL for tests"
    )

@pytest.fixture
def db_url(request):
    return request.config.getoption("--db-url")
```

## Marker Registration

```python
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
```

## Test Selection Hooks

```python
def pytest_collection_modifyitems(items):
    """Sort or modify collected tests."""
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="Skipping slow tests"))
```

See [conftest-intro](./conftest-intro.md) for an overview of conftest capabilities.
