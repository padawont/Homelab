---
title: "Static Files"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - static-files
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/static-files/"
    title: "FastAPI Docs — Static Files"
last_audit_date: 2026-06-09
---

# Static Files

Mount static file directories:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
```

## How it works

- Files from the `static/` directory are served at `/static/...`
- `GET /static/css/style.css` → reads `static/css/style.css`
- Returns appropriate `Content-Type` based on file extension
- Supports directory index if `index.html` exists

## Multiple directories

```python
app.mount("/media", StaticFiles(directory="media"), name="media")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
```

## HTML responses

```python
from fastapi.responses import HTMLResponse

html_content = """
<!DOCTYPE html>
<html>
<head><title>FastAPI</title></head>
<body><h1>Hello</h1></body>
</html>
"""


@app.get("/page")
async def get_page():
    return HTMLResponse(content=html_content)
```

## StaticFiles vs FileResponse

- `StaticFiles` — serves entire directories
- `FileResponse` — serves a single file with custom headers (see [file-response.md](./file-response.md))

See [html-response.md](./html-response.md) for more HTML response patterns.
