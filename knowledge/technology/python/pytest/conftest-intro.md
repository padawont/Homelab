---
title: "What conftest.py Does"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - conftest
  - plugins
sources:
  - url: "https://docs.pytest.org/en/stable/how-to/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files"
    title: "pytest conftest.py Documentation"
last_audit_date: 2026-06-09
---

# What conftest.py Does

`conftest.py` is a special file pytest discovers automatically in each test directory. It serves as a plugin and fixture container.

## Key Roles

1. **Shared Fixtures** — Define fixtures available to all tests in the directory tree (see [fixtures-conftest](./fixtures-conftest.md)).
2. **Hooks** — Implement pytest hooks for setup/teardown (see [conftest-hooks](./conftest-hooks.md)).
3. **Plugin Configuration** — Register markers, configure options, add CLI arguments.
4. **Override** — A conftest closer to a test module overrides one in a parent directory.

## Example conftest.py

```python
# tests/conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
```

## Directory Scoping

```
tests/
├── conftest.py          # Applies to all tests
├── unit/
│   ├── conftest.py      # Adds unit-specific fixtures
│   └── test_foo.py
└── integration/
    ├── conftest.py      # Adds integration-specific fixtures
    └── test_bar.py
```

## No Import Needed

Tests in the same directory tree automatically see conftest fixtures — no explicit import required.
