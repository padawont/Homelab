---
title: "OS Factor in Cache Key"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - cache-key
  - runner-os
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
    title: "GitHub Actions Caching Documentation"
last_audit_date: 2026-06-09
---

# OS Factor in Cache Key

The runner operating system must be part of any dependency cache key because compiled Python extensions are platform-specific.

## Why OS Matters

- Binary wheels differ per OS (manylinux, macOS, Windows).
- The uv cache stores pre-built binaries that cannot be shared across platforms.
- The `.venv` directory includes shebangs and compiled `.so`/`.dylib`/`.pyd` files.

## Standard Pattern

```yaml
key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
```

`${{ runner.os }}` evaluates to `Linux`, `macOS`, or `Windows`.

## Matrix Example

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]

steps:
  - uses: actions/cache@v4
    with:
      path: ~/.cache/uv
      key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
```

Each OS gets its own cache namespace. Cross-platform cache poisoning is impossible because the keys never collide.

See [cache-key-python-version](./cache-key-python-version.md) for when Python version should also be included.
