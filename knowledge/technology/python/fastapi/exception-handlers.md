---
title: "Exception Handlers"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - exceptions
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/handling-errors/"
    title: "FastAPI Docs — Handling Errors"
last_audit_date: 2026-06-09
---

# Exception Handlers

Override or add custom exception handlers:

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


app = FastAPI()


@app.exception_handler(UnicornException)
async def unicorn_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=status.HTTP_418_IM_A_TEAPOT,
        content={"detail": f"Oops! {exc.name} did something weird."},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.status_code},
    )


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}
```

## Built-in exception types

| Exception | Default status | Purpose |
|---|---|---|
| `HTTPException` | Required (user-specified) | Standard HTTP errors |
| `RequestValidationError` | 422 | Request validation failures |
| `StarletteHTTPException` | Various | Starlette-level errors |

## Custom exception responses

See [custom-exception-responses.md](./custom-exception-responses.md) for custom JSON error bodies.

See also [http-exception.md](./http-exception.md) for `HTTPException` usage patterns.
