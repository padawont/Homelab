---
title: "Form Data and File Uploads"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - forms
  - files
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/request-forms/"
    title: "FastAPI Docs — Form Data"
  - url: "https://fastapi.tiangolo.com/tutorial/request-files/"
    title: "FastAPI Docs — File Uploads"
last_audit_date: 2026-06-09
---

# Form Data and File Uploads

## Form fields

Requires `python-multipart`:

```bash
uv add python-multipart
```

```python
from fastapi import FastAPI, Form

app = FastAPI()


@app.post("/login")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}
```

## Single file upload

```python
from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/upload")
async def upload_file(file: UploadFile = File()):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}
```

## `UploadFile` vs `bytes`

| `UploadFile` | `bytes` |
|---|---|
| Spooled to disk if > threshold | Loaded entirely into memory |
| Has `.filename`, `.content_type` | Just raw bytes |
| `await file.read()` / `file.file` | Used directly |
| Preferred for large files | Fine for tiny payloads |

## Mixed form + file

```python
@app.post("/create")
async def create(
    name: str = Form(),
    file: UploadFile = File(),
):
    ...
```

See [form-files-multiple.md](./form-files-multiple.md) for multiple file uploads.
