---
title: "Deployment — Docker"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastapi
  - deployment
  - docker
sources:
  - url: "https://fastapi.tiangolo.com/deployment/docker/"
    title: "FastAPI Docs — Docker"
last_audit_date: 2026-06-09
---

# Deployment — Docker

Containerize FastAPI with Docker:

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application
COPY . .

# Run with uvicorn
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Dockerfile with Gunicorn

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

CMD [
    "uv", "run", "gunicorn", "main:app",
    "--worker-class", "uvicorn.workers.UvicornWorker",
    "--workers", "4",
    "--bind", "0.0.0.0:8000"
]
```

## Multi-stage build

```dockerfile
# Builder stage
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.12-slim
COPY --from=builder /app/.venv /app/.venv
COPY . /app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## docker-compose.yml

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://db:5432/app
    depends_on:
      - db
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: app
```

See [deployment-uvicorn.md](./deployment-uvicorn.md) for Uvicorn options and [deployment-nginx.md](./deployment-nginx.md) for reverse proxy setup.
