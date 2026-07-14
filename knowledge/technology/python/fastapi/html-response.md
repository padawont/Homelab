---
title: "HTML Response"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - response
  - html
sources:
  - url: "https://fastapi.tiangolo.com/advanced/custom-response/#htmlresponse"
    title: "FastAPI Docs — HTMLResponse"
last_audit_date: 2026-06-09
---

# HTML Response

Return HTML content using `HTMLResponse`:

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/hello", response_class=HTMLResponse)
async def hello_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hello</title>
        <style>
            body { font-family: sans-serif; padding: 2rem; }
        </style>
    </head>
    <body>
        <h1>Hello from FastAPI!</h1>
        <p>This is an HTML response.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
```

## Using Jinja2 templates

```bash
uv add jinja2
```

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/profile/{username}", response_class=HTMLResponse)
async def profile(request: Request, username: str):
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "username": username},
    )
```

## `response_class=HTMLResponse`

Using `response_class=HTMLResponse` in the decorator:
- Sets `Content-Type: text/html`
- Tells OpenAPI the response is HTML

See [static-files.md](./static-files.md) for serving static assets alongside HTML.
