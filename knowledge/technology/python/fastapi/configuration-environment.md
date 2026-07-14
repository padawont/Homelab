---
title: "Configuration — Environment Files"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - configuration
  - environment
sources:
  - url: "https://fastapi.tiangolo.com/advanced/settings/#dotenv-env-file"
    title: "FastAPI Docs — .env File"
last_audit_date: 2026-06-09
---

# Configuration — Environment Files

Load configuration from `.env` files:

```dotenv
# .env
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=super-secret-key
DEBUG=true
MAX_CONNECTIONS=50
```

## With Pydantic Settings

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    max_connections: int = 10

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
```

## Multiple env files

```python
class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",  # Default
        "extra": "ignore",
    }


# Load different file per environment
if os.getenv("ENV") == "production":
    settings = Settings(_env_file=".env.production")
else:
    settings = Settings()
```

## Priority order

Environment variables override `.env` file values, which override field defaults.

## Security

- Never commit `.env` files to version control
- Use `.env.example` as a template
- Keep secrets in a vault/secret manager in production

See [configuration-pydantic-settings.md](./configuration-pydantic-settings.md) for the Settings base class pattern.
