---
title: "Docker DLC Invalidation"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - docker
  - docker-layer-caching
  - invalidation
sources:
  - url: "https://docs.docker.com/build/cache/"
    title: "Docker build cache documentation"
last_audit_date: 2026-06-10
---

# Docker DLC Invalidation

Understanding what causes Docker layer cache invalidation helps structure Dockerfiles for maximum cache reuse.

## What Invalidates a Layer

| Change | Effect |
|---|---|
| Modified `requirements*.txt` or `uv.lock` | Invalidates dependency installation layer |
| Modified `pyproject.toml` | Invalidates layers that copy or read it |
| Modified source code | Invalidates the COPY layer and all subsequent layers |
| Changed base image tag | Invalidates FROM layer |
| Changed build argument | Invalidates ARG layer and all subsequent layers |

## Optimizing Dockerfile Layer Order

Structure the Dockerfile so frequently-changing code is **last**:

```dockerfile
# Base — stable
FROM python:3.12-slim AS base

# Dependencies — changes infrequently
COPY uv.lock pyproject.toml /app/
RUN uv sync --frozen

# Source code — changes frequently (cached if deps unchanged)
COPY . /app/
```

## Force Cache Bust

To force a rebuild of all layers:

```yaml
- uses: docker/build-push-action@v7
  with:
    build-args: |
      CACHE_BUST=${{ github.run_id }}
```

Or in Dockerfile:

```dockerfile
ARG CACHE_BUST=1
RUN echo "Build $CACHE_BUST"
```

## Monitoring Cache Effectiveness

```yaml
- name: Build and export
  uses: docker/build-push-action@v7
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

Check build logs for `CACHED` vs `BUILD` annotations on each step to see which layers were reused.

See [docker-multi-stage](./docker-multi-stage.md) for multi-stage build strategies.
