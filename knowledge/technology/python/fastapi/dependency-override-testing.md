---
title: "Dependency Override Testing"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - dependency-injection
  - testing
sources:
  - url: "https://fastapi.tiangolo.com/advanced/testing-dependencies/"
    title: "FastAPI Docs — Testing Dependencies"
last_audit_date: 2026-06-09
---

# Dependency Override Testing

Replace real dependencies with test doubles using `app.dependency_overrides`:

```python
from fastapi import FastAPI, Depends

app = FastAPI()


def get_db():
    return {"connection": "real_db"}


@app.get("/items")
async def read_items(db: dict = Depends(get_db)):
    return db


# In tests
def test_override():
    def fake_db():
        return {"connection": "test_db"}

    app.dependency_overrides[get_db] = fake_db

    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/items")
    assert response.json() == {"connection": "test_db"}

    app.dependency_overrides.clear()  # cleanup
```

## Context manager pattern

```python
def test_with_override():
    app.dependency_overrides[get_db] = fake_db
    with TestClient(app) as client:
        response = client.get("/items")
        assert response.status_code == 200
    app.dependency_overrides.clear()
```

## Multiple overrides

```python
app.dependency_overrides = {
    get_db: fake_db,
    verify_token: fake_token,
}
```

## Reset between tests

Always call `app.dependency_overrides.clear()` or use `pytest` fixtures with `yield` + cleanup.

See [testing-testclient-intro.md](./testing-testclient-intro.md) for TestClient setup and [testing-dependency-overrides.md](./testing-dependency-overrides.md) for more patterns.
