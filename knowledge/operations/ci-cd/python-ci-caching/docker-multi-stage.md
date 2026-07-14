---
title: "Multi-stage Docker Builds for Cache"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - docker
  - multi-stage
  - dockerfile
sources:
  - url: "https://docs.docker.com/build/building/multi-stage/"
    title: "Multi-stage builds documentation"
last_audit_date: 2026-06-09
---

# Multi-stage Docker Builds for Cache

Multi-stage builds improve cache reuse by separating build-time dependencies from the runtime image.

## Why Multi-stage Helps

- **Build stage**: installs all dependencies (including dev/test tools).
- **Runtime stage**: copies only the built artifacts and runtime dependencies.
- Smaller final images reduce pull times and cache storage.

## Example: Python with uv

```dockerfile
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY uv.lock pyproject.toml /app/
RUN uv sync --locked --no-dev

# Stage 2: Test dependencies
FROM builder AS test
RUN uv sync --locked
COPY . /app/

# Stage 3: Runtime
FROM python:3.12-slim AS runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uv", "run", "app"]
```

## CI Build with DLC

```yaml
- uses: docker/build-push-action@v7
  with:
    target: runtime
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Stage-Specific Caching

Build specific stages for different CI jobs:

```yaml
# Test job — build up to test stage
- uses: docker/build-push-action@v7
  with:
    target: test
    cache-from: type=gha
    cache-to: type=gha,mode=max

# Deploy job — build runtime stage only
- uses: docker/build-push-action@v7
  with:
    target: runtime
    cache-from: type=gha
```

The test stage benefits from the builder layer being cached from previous runs.

See [docker-layer-caching-intro](./docker-layer-caching-intro.md) for the introduction to DLC.
