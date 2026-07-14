---
title: "CI Caching for Python"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - python
  - uv
  - github-actions
  - docker
  - vcr
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
    title: "GitHub Actions Caching Documentation"
  - url: "https://github.com/actions/cache"
    title: "actions/cache on GitHub"
last_audit_date: 2026-06-09
---

# CI Caching for Python

Comprehensive reference for CI caching strategies in Python projects using GitHub Actions. Covers three major caching domains: uv dependency caching, VCR cassette caching, and Docker layer caching.

## Domains

| Domain | Focus | Notes |
|---|---|---|
| **uv Dependency Caching** | `~/.cache/uv`, `.venv`, lockfile-based keys | [details](./uv-caching-install.md) |
| **pip (legacy)** | `~/.cache/pip`, setup-python cache | [details](./pip-caching-setup.md) |
| **VCR Cassette Caching** | Recorded HTTP interactions, selective replay | [details](./vcr-cassette-caching-intro.md) |
| **Docker Layer Caching** | Docker image layers, multi-stage builds | [details](./docker-layer-caching-intro.md) |

## Design Principles

- Use `hashFiles('**/uv.lock')` for primary cache keys — lockfile changes are the best invalidation signal.
- Factor OS and Python version into keys to prevent cross-platform cache corruption.
- Use `restore-keys` for partial fallback when an exact match is not found.
- Keep cache segments separate (e.g. dependency cache vs. cassette cache) to avoid unnecessary churn.
- Benchmark cache effectiveness with real CI timing data.

## Scenarios

- **New project setup**: [uv-caching-install](./uv-caching-install.md) + [cache-key-lockfile-hash](./cache-key-lockfile-hash.md)
- **Adding VCR tests**: [vcr-cassette-caching-intro](./vcr-cassette-caching-intro.md) + [vcr-cache-key](./vcr-cache-key.md)
- **Dockerized CI**: [docker-layer-caching-intro](./docker-layer-caching-intro.md) + [docker-multi-stage](./docker-multi-stage.md)
- **Migrating from pip to uv**: [pip-vs-uv-tradeoffs](./pip-vs-uv-tradeoffs.md)
