---
title: "restore-keys Fallback Patterns"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - cache-key
  - restore-keys
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
    title: "GitHub Actions Caching Documentation"
last_audit_date: 2026-06-09
---

# restore-keys Fallback Patterns

`restore-keys` provides a fallback when the primary cache key does not match any existing entry. GitHub Actions tries each fallback key in order and restores the most recent match.

## How restore-keys Work

1. Exact match on `key` → full hit (`cache-hit = true`).
2. No exact match → iterate `restore-keys` in order.
3. Each `restore-key` matches as a **prefix** — the most recent cache with that prefix is restored.
4. No matches at all → cache miss, steps continue without restored files.

## Common Patterns

### Global prefix fallback

```yaml
key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
restore-keys: |
  ${{ runner.os }}-uv-
```

When the lockfile hash changes, the runner still gets the previous uv cache (partially stale, but better than nothing).

### Tiered specificity

```yaml
key: ${{ runner.os }}-venv-${{ matrix.python-version }}-${{ hashFiles('**/uv.lock') }}
restore-keys: |
  ${{ runner.os }}-venv-${{ matrix.python-version }}-
  ${{ runner.os }}-venv-
```

### No fallback (strict mode)

Leave `restore-keys` empty. Cache is only used on exact match — safe but slower on lockfile changes.

## Trade-offs

- **Broad fallback** — faster partial restores, risk of stale dependencies being used.
- **Strict** — slower builds after dependency changes, guarantees correctness.

See [cache-hit-detection](./cache-hit-detection.md) for how to detect whether a cache was restored via fallback.
