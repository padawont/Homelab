---
title: "Cache Key Design Strategies"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - cache-key
  - github-actions
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
    title: "GitHub Actions Caching Documentation"
  - url: "https://github.com/actions/cache"
    title: "actions/cache on GitHub"
last_audit_date: 2026-06-09
---

# Cache Key Design Strategies

A well-designed cache key maximizes cache hits while ensuring correctness. The key should encode every factor that affects the cached content.

## Principles

1. **Precise invalidation** — the key must change when the cached content becomes stale.
2. **Broad reuse** — the key should be stable across runs where the cached content is still valid.
3. **Segmented scope** — use separate keys for distinct cache domains (deps, cassettes, Docker).

## Common Factors

| Factor | When to Include | Example |
|---|---|---|
| OS runner | Always (binaries differ) | `${{ runner.os }}` |
| Python version | When caching `.venv` or compiled deps | `${{ matrix.python-version }}` |
| Lockfile hash | For dependency caches | `hashFiles('**/uv.lock')` |
| Content hash | For arbitrary file caches | `hashFiles('tests/cassettes/**')` |

## Strategies

- **Exact key** — Use for deterministic builds (e.g., `runner.os` + lockfile hash).
- **Prefix + hash** — Use for broader fallback via `restore-keys` (e.g., `runner.os-` prefix).
- **Version prefix** — Bump a static prefix (`cache-v1-`) to force a clean cache.

See [cache-key-lockfile-hash](./cache-key-lockfile-hash.md), [cache-key-os-factor](./cache-key-os-factor.md), and [cache-key-python-version](./cache-key-python-version.md) for each factor in detail.
