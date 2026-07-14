---
title: "First App"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - beginner
sources:
  - url: "https://fastapi.tiangolo.com/#first-steps"
    title: "FastAPI Docs — First Steps"
last_audit_date: 2026-06-09
---

# First App

Minimal FastAPI application:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

Save as `main.py`.

## Run it

```bash
uv run uvicorn main:app --reload
```

- `main:app` — Python module `main`, object `app`
- `--reload` — auto-restart on file changes (dev only)

## Check the docs

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/docs` | Swagger UI |
| `http://127.0.0.1:8000/redoc` | ReDoc |

See [installation.md](./installation.md) and [running-uvicorn.md](./running-uvicorn.md) for more details.
