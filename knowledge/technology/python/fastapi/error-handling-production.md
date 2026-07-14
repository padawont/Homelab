---
title: "Production Error Handling"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - error-handling
  - production
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/handling-errors/"
    title: "FastAPI Docs — Handling Errors"
last_audit_date: 2026-06-09
---

# Production Error Handling

Safe error responses for production:

```python
import logging
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)
app = FastAPI()


@app.exception_handler(HTTPException)
async def production_http_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def production_validation_handler(request: Request, exc: RequestValidationError):
    # Log full details, return safe message
    logger.error("Validation error: %s", exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "Request validation failed",
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    # Catch-all for unhandled exceptions
    logger.exception("Unhandled error handling %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
            }
        },
    )
```

## Don't leak internals

- Never expose tracebacks in production
- Log full error details server-side
- Return consistent, safe error bodies

## 500 catch-all

Always register a catch-all `Exception` handler to prevent unhandled crashes from leaking stack traces.

See [exception-handlers.md](./exception-handlers.md) for handler setup and [custom-exception-responses.md](./custom-exception-responses.md) for custom error bodies.
