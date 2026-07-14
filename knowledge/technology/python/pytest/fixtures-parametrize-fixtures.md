---
title: "Parametrized Fixtures"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - fixtures
  - parametrize
sources:
  - url: "https://docs.pytest.org/en/stable/how-to/fixtures.html#parametrizing-fixtures"
    title: "pytest Parametrized Fixtures"
last_audit_date: 2026-06-09
---

# Parametrized Fixtures

A fixture can be declared with `params` to run all dependent tests once for each parameter value.

## Basic Syntax

```python
@pytest.fixture(params=["sqlite", "postgresql"])
def db(request):
    engine = create_engine(request.param)
    yield engine
    engine.dispose()
```

The fixture function receives each value via `request.param` (see [fixtures-request](./fixtures-request.md)).

## Test Execution

A test requesting `db` runs twice — once for `"sqlite"` and once for `"postgresql"`:

```python
def test_connection(db):
    assert db.connect()
```

## Combining with Regular Parametrize

You can also combine a parametrized fixture with `@pytest.mark.parametrize` on the test — the total test count is the Cartesian product of all parameter sets.

See [parametrize-fixture-combine](./parametrize-fixture-combine.md).
