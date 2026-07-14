---
title: "Docker Layer Caching — Introduction"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - docker
  - docker-layer-caching
  - dlc
sources:
  - url: "https://docs.docker.com/build/cache/"
    title: "Docker build cache documentation"
last_audit_date: 2026-06-09
---

# Docker Layer Caching — Introduction

Docker Layer Caching (DLC) reuses previously built image layers to accelerate Docker builds in CI. For Python projects, this speeds up image creation when dependencies change infrequently.

## Why DLC Matters

- Python dependency layers (uv sync, pip install) are the most expensive part of a Docker build.
- Without caching, every CI build rebuilds the entire image from scratch (2–5 minutes).
- With caching, unchanged layers are reused (10–30 seconds).

## How DLC Works in GitHub Actions

GitHub Actions supports DLC via the `docker/build-push-action` with cache-to/cache-from pointing to a GitHub Actions cache backend:

```yaml
- uses: docker/build-push-action@v7
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Cache Scope

| Backend | Scope | Persistence |
|---|---|---|
| `type=gha` | GitHub Actions cache | Per branch/repo |
| `type=registry` | Container registry | Per image tag |
| `type=local` | Local filesystem | Per runner |

## Basic Workflow

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v4

- name: Build and push
  uses: docker/build-push-action@v7
  with:
    context: .
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

See [docker-dlc-key](./docker-dlc-key.md) for cache key design and [docker-dlc-invalidation](./docker-dlc-invalidation.md) for invalidation strategies.
