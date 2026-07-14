---
title: "Lockfile Hash Cache Key"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - cache-key
  - lockfile
  - uv
  - hash-files
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
    title: "GitHub Actions Caching Documentation"
last_audit_date: 2026-06-09
---

# Lockfile Hash Cache Key

The most reliable primary key for Python dependency caches is `hashFiles('**/uv.lock')` (for uv) or `hashFiles('**/requirements*.txt', '**/pyproject.toml')` (for pip).

## Why Lockfile Hashing Works

- A lockfile (`uv.lock`, `requirements.txt`) captures the exact resolved dependency tree.
- Any change to dependencies — direct or transitive — changes the lockfile content.
- The hash is deterministic: same lockfile always produces the same hash across runners.

## Example

```yaml
- uses: actions/cache@v4
  id: uv-cache
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
    restore-keys: |
      ${{ runner.os }}-uv-
```

## Globbing Notes

- `**/uv.lock` matches the lockfile at any depth (monorepo support).
- Use `hashFiles('**/uv.lock', '**/pyproject.toml')` to include both lockfile and project metadata.
- GitHub's `hashFiles` is case-sensitive on Linux/macOS runners but **case-insensitive on Windows runners** — the behaviour depends on the runner operating system's file system semantics. Uses forward slashes cross-platform.

## Limitations

- Does not detect changes in the uv tool itself — only dependency changes.
- For uv binary updates, see [uv-caching-install](./uv-caching-install.md).
