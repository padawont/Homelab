---
title: "Cache Hit Detection"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - cache-hit
  - github-actions
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
    title: "GitHub Actions Caching Documentation"
last_audit_date: 2026-06-09
---

# Cache Hit Detection

The `actions/cache` action outputs `cache-hit` (`"true"`, `"false"`, or an empty string on a complete cache miss). Use this to conditionally skip or execute steps.

## Basic Conditional

```yaml
- uses: actions/cache@v4
  id: uv-cache
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}

- name: Install dependencies (if cache miss)
  if: steps.uv-cache.outputs.cache-hit != 'true'
  run: uv sync --frozen
```

## Important: Cache Hit Means Exact Key Match

`cache-hit = 'true'` only when the **exact** primary key matches. If a `restore-key` fallback was used, `cache-hit` is `'false'`.

```yaml
- name: Run uv sync (partial or full miss)
  if: steps.uv-cache.outputs.cache-hit != 'true'
  run: uv sync --frozen
```

## Multi-Cache Detection

When using multiple cache actions (e.g., uv cache + VCR cache), give each step a unique `id`:

```yaml
- uses: actions/cache@v4
  id: uv-cache
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}

- uses: actions/cache@v4
  id: vcr-cache
  with:
    path: tests/cassettes
    key: ${{ hashFiles('tests/cassettes/**') }}
```

## Common Mistake

Using `cache-hit` to skip `uv sync` entirely is unsafe — even on cache hit, you may need to validate the environment. Instead, skip only the download phase and run `uv sync --frozen` regardless (it will be near-instant on cache hit).

See [cache-restore-keys](./cache-restore-keys.md) for details on fallback behavior.
