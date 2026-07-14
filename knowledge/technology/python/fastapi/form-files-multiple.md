---
title: "Multiple File Uploads"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - forms
  - files
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/request-files/#multiple-file-uploads"
    title: "FastAPI Docs — Multiple File Uploads"
last_audit_date: 2026-06-09
---

# Multiple File Uploads

Upload multiple files simultaneously:

```python
from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/upload-multiple")
async def upload_multiple(files: list[UploadFile] = File()):
    results = []
    for file in files:
        content = await file.read()
        results.append({
            "filename": file.filename,
            "size": len(content),
        })
    return results
```

## Using `bytes` for small files

```python
@app.post("/upload-small")
async def upload_small(files: list[bytes] = File()):
    return [{"size": len(f)} for f in files]
```

## Client request format

Multiple files are sent as `multipart/form-data` with the same field name repeated:

```
POST /upload-multiple
Content-Type: multipart/form-data

files: <file1>
files: <file2>
```

## Required dependency

Ensure `python-multipart` is installed:

```bash
uv add python-multipart
```

See [form-data.md](./form-data.md) for single file uploads and form fields.
