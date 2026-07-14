---
title: "Fixture Scopes"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - fixtures
  - scope
sources:
  - url: "https://docs.pytest.org/en/stable/how-to/fixtures.html#fixture-scopes"
    title: "pytest Fixture Scopes"
last_audit_date: 2026-06-09
---

# Fixture Scopes

Control how often a fixture is set up and torn down using the `scope` parameter.

## Available Scopes

| Scope | Lifecycle |
|---|---|
| `function` (default) | Once per test function |
| `class` | Once per test class |
| `module` | Once per module (file) |
| `package` | Once per package directory |
| `session` | Once per entire test run |

## Examples

```python
@pytest.fixture(scope="module")
def db_pool():
    pool = create_pool()
    yield pool
    pool.close()

@pytest.fixture(scope="session")
def settings():
    return load_settings()  # loaded once for the whole run

@pytest.fixture(scope="class")
def shared_data():
    return expensive_computation()
```

## Scope Ordering

A fixture with a broader scope cannot depend on a fixture with a narrower scope. pytest raises `ScopeMismatch` in that case.

For async fixture scoping, see [pytest-asyncio-scope](./pytest-asyncio-scope.md).
