---
title: "Testing — Form Data and File Uploads"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - testing
  - forms
  - files
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/testing/"
    title: "FastAPI Docs — Testing"
last_audit_date: 2026-06-09
---

# Testing — Form Data and File Uploads

## Testing form fields

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_login_form():
    response = client.post("/login", data={"username": "alice", "password": "secret"})
    assert response.status_code == 200
    assert response.json() == {"username": "alice"}
```

## Testing file uploads

```python
def test_upload_file():
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"Hello, World!", "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["size"] == 13
```

## Multiple files

```python
def test_upload_multiple():
    response = client.post(
        "/upload-multiple",
        files=[
            ("files", ("a.txt", b"Content A", "text/plain")),
            ("files", ("b.txt", b"Content B", "text/plain")),
        ],
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
```

## Mixed form + file

```python
def test_mixed():
    response = client.post(
        "/create",
        data={"name": "test"},
        files={"file": ("doc.txt", b"content", "text/plain")},
    )
    assert response.status_code == 200
```

See [form-data.md](./form-data.md) for form/file handler definitions and [form-files-multiple.md](./form-files-multiple.md) for multiple files.
