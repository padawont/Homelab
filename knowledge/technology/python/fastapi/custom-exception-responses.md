---
title: "Custom Exception Response Bodies"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - exceptions
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/handling-errors/#override-the-default-exception-handlers"
    title: "FastAPI Docs — Override Default Handlers"
last_audit_date: 2026-06-09
---

# Custom Exception Response Bodies

Override FastAPI's default exception handlers for consistent JSON error bodies:

```python
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError

app = FastAPI()


@app.exception_handler(HTTPException)
async def custom_http_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error",
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "Validation failed",
                "type": "validation_error",
                "fields": exc.errors(),
            }
        },
    )
```

## Standard error schema

```json
{
  "error": {
    "code": 422,
    "message": "Validation failed",
    "type": "validation_error",
    "fields": [
      {"loc": ["body", "price"], "msg": "field required", "type": "value_error.missing"}
    ]
  }
}
```

## Override vs add

- Override: replace the default handler entirely
- Add: handle custom exception types not covered by defaults

See [exception-handlers.md](./exception-handlers.md) for adding custom handlers and [http-exception.md](./http-exception.md) for HTTPException usage.
