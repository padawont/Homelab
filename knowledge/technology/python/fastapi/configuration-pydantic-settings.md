---
title: "Configuration — Pydantic Settings"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - configuration
  - pydantic
sources:
  - url: "https://fastapi.tiangolo.com/advanced/settings/"
    title: "FastAPI Docs — Settings"
last_audit_date: 2026-06-09
---

# Configuration — Pydantic Settings

Manage application configuration with `BaseSettings`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "My API"
    debug: bool = False
    database_url: str
    secret_key: str
    max_connections: int = 10
    allowed_hosts: list[str] = ["*"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

## Usage in FastAPI

```python
from fastapi import FastAPI
from functools import lru_cache


@lru_cache
def get_settings():
    return Settings()


app = FastAPI()


@app.get("/info")
async def info():
    s = get_settings()
    return {"app_name": s.app_name, "debug": s.debug}
```

## Environment variable mapping

Settings read from environment variables by field name (case-insensitive):

```bash
export DATABASE_URL="postgresql://localhost/mydb"
export SECRET_KEY="super-secret"
export DEBUG="true"
```

## Field aliases

```python
class Settings(BaseSettings):
    database_url: str = Field(alias="db_url")
```

## Nested settings

```python
class APIConfig(BaseSettings):
    timeout: int = 30
    retries: int = 3

class Settings(BaseSettings):
    api: APIConfig = APIConfig()
```

See [configuration-environment.md](./configuration-environment.md) for `.env` file loading.
