---
title: "Mounting Sub-Applications"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - asgi
  - sub-applications
sources:
  - url: "https://fastapi.tiangolo.com/advanced/sub-applications/"
    title: "FastAPI Docs — Sub Applications"
last_audit_date: 2026-06-09
---

# Mounting Sub-Applications

Mount other ASGI applications under a URL prefix:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()


# Mount a sub-application
sub_app = FastAPI()


@sub_app.get("/info")
async def info():
    return {"app": "sub", "version": "2.0"}


app.mount("/sub", sub_app)
```

- `GET /sub/info` → handled by `sub_app`
- The `sub_app` sees `/info` (prefix is stripped before routing)

## Mounting WSGI apps

```python
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask

flask_app = Flask(__name__)


@flask_app.route("/hello")
def hello():
    return "Hello from Flask"


app.mount("/legacy", WSGIMiddleware(flask_app))
```

## Mounting StaticFiles

```python
app.mount("/static", StaticFiles(directory="static"), name="static")
```

## Important notes

- Sub-apps have their own OpenAPI docs at `/sub/docs`
- Middleware on the parent app wraps the sub-app
- `app.state` is not shared — use dependency injection for shared resources
- Mount order matters — first match wins

See [integration-fastmcp-events.md](./integration-fastmcp-events.md) for mounting FastMCP servers.
