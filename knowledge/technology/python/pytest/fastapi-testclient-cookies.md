---
title: "Handling Cookies with TestClient"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testclient
  - cookies
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/testing/"
    title: "FastAPI Testing Guide"
last_audit_date: 2026-06-09
---

# Handling Cookies with TestClient

TestClient stores cookies between requests, simulating a browser session.

## Cookie Persistence

```python
def test_cookie_session(client):
    # First request sets a cookie
    resp1 = client.post("/login", json={"user": "alice"})
    assert resp1.cookies.get("session_id")

    # Cookie is automatically sent on subsequent requests
    resp2 = client.get("/profile")
    assert resp2.status_code == 200
```

## Setting Cookies Manually

```python
def test_with_cookie():
    response = client.get("/items", cookies={"session_id": "abc123"})
```

## Checking Response Cookies

```python
def test_check_cookie():
    resp = client.get("/set-cookie")
    assert "session_id" in resp.cookies
    assert resp.cookies["session_id"] == "value"
```

## Clearing Cookies

```python
client.cookies.clear()  # Clears all stored cookies
```

## Per-Test Isolation

When using the fixture pattern with `yield`, each test gets a fresh `TestClient` instance with no shared cookie state (see [fastapi-testclient-context](./fastapi-testclient-context.md)).
