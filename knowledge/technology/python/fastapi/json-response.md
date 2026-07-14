---
title: "JSON Response"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - response
  - json
sources:
  - url: "https://fastapi.tiangolo.com/advanced/custom-response/#jsonresponse"
    title: "FastAPI Docs — JSONResponse"
last_audit_date: 2026-06-09
---

# JSON Response

Create custom JSON responses with full control:

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import status

app = FastAPI()


@app.get("/health")
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "2.0.0",
            "uptime_seconds": 12345,
        },
        status_code=status.HTTP_200_OK,
        headers={
            "X-API-Version": "2.0.0",
            "X-Health-Check": "pass",
        },
    )
```

## When to use `JSONResponse` directly

- Custom status codes per response
- Custom headers
- Returning non-model data
- Error responses with custom format
- Wrapping responses in an envelope

## Custom JSON encoder

```python
from datetime import datetime
from fastapi.encoders import jsonable_encoder


@app.get("/timestamp")
async def timestamp():
    data = {
        "now": datetime.utcnow(),
        "message": "Current time",
    }
    return JSONResponse(content=jsonable_encoder(data))
```

## JSON response vs returning a dict

| Returning a dict | `JSONResponse` |
|---|---|
| Returns `200` by default | Full control |
| Headers via `Response` param | Headers inline |
| Uses `response_model` filtering | No filtering |

See [response-model.md](./response-model.md) for response filtering and [response-headers.md](./response-headers.md) for header customization.
