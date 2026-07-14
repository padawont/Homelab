---
title: "Response Status Code"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - response
  - status-code
sources:
  - url: "https://fastapi.tiangolo.com/tutorial/response-status-code/"
    title: "FastAPI Docs — Response Status Code"
last_audit_date: 2026-06-09
---

# Response Status Code

Set the HTTP status code on path operations:

```python
from fastapi import FastAPI, status

app = FastAPI()


@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item():
    return {"message": "created"}


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    return None
```

## Using `status` module

Prefer `fastapi.status` constants over raw integers:

| Constant | Value |
|---|---|
| `status.HTTP_200_OK` | 200 |
| `status.HTTP_201_CREATED` | 201 |
| `status.HTTP_204_NO_CONTENT` | 204 |
| `status.HTTP_400_BAD_REQUEST` | 400 |
| `status.HTTP_401_UNAUTHORIZED` | 401 |
| `status.HTTP_403_FORBIDDEN` | 403 |
| `status.HTTP_404_NOT_FOUND` | 404 |
| `status.HTTP_422_UNPROCESSABLE_ENTITY` | 422 |
| `status.HTTP_500_INTERNAL_SERVER_ERROR` | 500 |

## Dynamic status codes

Use `Response` or `JSONResponse` to set status per-response:

```python
from fastapi import FastAPI, Response, status

@app.post("/items")
async def create_item(response: Response):
    response.status_code = status.HTTP_201_CREATED
    return {"message": "created"}
```

See [response-model.md](./response-model.md) for response_model integration.
