---
title: "Installation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - installation
  - uv
sources:
  - url: "https://fastapi.tiangolo.com/"
    title: "FastAPI Documentation"
last_audit_date: 2026-06-09
---

# Installation

Add FastAPI with all recommended extras using `uv`:

```bash
uv add "fastapi[standard]"
```

The `[standard]` extra bundles everything needed for production FastAPI development: `uvicorn[standard]` (with `uvloop`, `httptools`, `websockets`, `watchfiles`, `python-dotenv`, `PyYAML`, `colorama`), `httpx`, `jinja2`, `python-multipart`, `email-validator`, and `fastapi-cli[standard]`.

## Minimal requirements

```
fastapi[standard]>=0.115.0
```

> If you installed bare `fastapi` (without `[standard]`), you would need to add `uvicorn[standard]` separately. The `[standard]` extra includes it automatically.

## Verification

```bash
uv run python -c "import fastapi; print(fastapi.__version__)"
```

## Optional extras

The extras below are **not** included in `fastapi[standard]`. They provide additional functionality on demand:

| Extra | Install | Purpose |
|---|---|---|
| `orjson` | `uv add orjson` | Faster JSON serialization (`ORJSONResponse`) |
| `ujson` | `uv add ujson` | Faster JSON serialization (`UJSONResponse`) |
| `pydantic-settings` | `uv add pydantic-settings` | Settings / environment variable management |
| `pydantic-extra-types` | `uv add pydantic-extra-types` | Additional Pydantic types (phone numbers, colors, etc.) |

> Notes: `httpx`, `python-multipart`, and `jinja2` are already included in `fastapi[standard]`. If you installed bare `fastapi` instead, add them separately as needed.

See [first-app.md](./first-app.md) for the minimal application setup.
