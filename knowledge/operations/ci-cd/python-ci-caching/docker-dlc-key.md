---
title: "Docker Layer Cache Key Design"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - docker
  - docker-layer-caching
  - cache-key
sources:
  - url: "https://docs.docker.com/build/cache/"
    title: "Docker build cache documentation"
  - url: "https://github.com/docker/build-push-action"
    title: "docker/build-push-action on GitHub"
last_audit_date: 2026-06-09
---

# Docker Layer Cache Key Design

When using `type=gha` (GitHub Actions cache) for DLC, the **GHA cache key** is the `scope` parameter value (default: `buildkit`). The `scope` acts as the named identifier under which BuildKit stores and retrieves cached layers in GHA's blob store. BuildKit handles the layer-level cache matching internally.

## Default GHA Scope

The `docker/build-push-action` with `type=gha` defaults the `scope` to `buildkit`. This means all builds across the repository share a single GHA cache entry, regardless of branch, OS, or event.

## How BuildKit Cache Matching Works (Internally)

Once a GHA cache entry is loaded by scope, BuildKit performs its own internal cache matching against that entry using:

- **Source files** in the build context (hash of directory).
- **Build arguments** passed to `docker build`.
- **Dockerfile instructions** and their order.

This is **not** part of the GHA cache key — it is a separate, internal mechanism within BuildKit that determines which layers from the retrieved cache blob are reusable.

## Explicit Scope Control

For finer control, use `cache-to` with an explicit scope:

```yaml
- uses: docker/build-push-action@v7
  with:
    cache-from: type=gha,scope=${{ runner.os }}-docker
    cache-to: type=gha,mode=max,scope=${{ runner.os }}-docker
```

## Scoping Strategies

| Scope | Trade-off |
|---|---|
| Per-branch (`scope=${{ github.ref }}`) | Fast branch-local builds, no cross-branch reuse |
| Per-event (`scope=${{ github.event_name }}`) | Separates PR vs main branch caches |
| Global (`scope=global-docker`) | Maximum reuse, risk of stale layers on branches |

## Cache Mode

| Mode | Description |
|---|---|
| `min` | Cache only exported layers (smaller cache, may rebuild intermediate layers) |
| `max` | Cache all layers (larger cache, fastest rebuilds) |

Use `mode=max` for CI to maximize speed. The total GitHub Actions cache limit (10 GB per repo) is usually sufficient.

## Layer Invalidation

A Docker layer is invalidated when:
1. The preceding layer changes.
2. The instruction producing it changes.
3. Files copied into the layer change.

See [docker-dlc-invalidation](./docker-dlc-invalidation.md) for detailed invalidation scenarios.
