---
title: "Troubleshooting"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - troubleshooting
sources:
  - url: "https://fastapi.tiangolo.com/"
    title: "FastAPI Documentation"
last_audit_date: 2026-06-09
---

# Troubleshooting

Common errors and solutions:

## Validation errors (422)

```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Fix**: Check the request body matches the Pydantic model. Missing required fields.

## ImportError: cannot import name 'TestClient'

**Fix**: Add `httpx`:

```bash
uv add httpx
```

## ModuleNotFoundError: No module named 'multipart'

**Fix**: Add `python-multipart`:

```bash
uv add python-multipart
```

## CORS errors in browser

**Fix**: Configure `CORSMiddleware` correctly (see [middleware-cors.md](./middleware-cors.md)). Ensure `allow_origins` matches the requesting origin.

## 405 Method Not Allowed

**Fix**: Check the HTTP method in the decorator matches the client request:

```python
@app.get("/items")  # Client must use GET, not POST
```

## Slow responses under load

| Cause | Solution |
|---|---|
| Blocking I/O in async handler | Use thread pool or async driver |
| No connection pool | Add database pool ([performance-database-pool.md](./performance-database-pool.md)) |
| No response compression | Add GZip middleware |
| Single worker | Increase `--workers` |

## WebSocket disconnects

**Fix**: Wrap receive loop in try/except. Use connection manager pattern ([websockets-managing-connections.md](./websockets-managing-connections.md)).

## Lifespan not running

**Fix**: Use context manager `with TestClient(app):` or run with ASGI server that supports lifespan.

## uv command not found

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Port already in use

```bash
# Find process
sudo lsof -i :8000
# Kill or use a different port
uv run uvicorn main:app --port 8001
```

See individual atomic notes for specific topic troubleshooting.
