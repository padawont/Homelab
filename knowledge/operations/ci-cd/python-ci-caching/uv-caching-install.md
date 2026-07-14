---
title: "uv Caching via astral-sh/setup-uv"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - uv
  - setup-uv
  - astral-sh
sources:
  - url: "https://github.com/astral-sh/setup-uv"
    title: "astral-sh/setup-uv on GitHub"
  - url: "https://docs.astral.sh/uv/"
    title: "uv documentation"
last_audit_date: 2026-06-10
---

# uv Caching via astral-sh/setup-uv

The `astral-sh/setup-uv` action handles both installing uv and optionally caching the uv dependency cache. It is the recommended approach for Python CI caching.

## Basic Setup

```yaml
- uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
  with:
    enable-cache: true
    cache-dependency-glob: "**/uv.lock"
```

This automatically:
1. Installs the specified `uv` version.
2. Restores the uv cache (at the configured `cache-local-path`, defaulting to a temp directory) based on the lockfile hash.
3. Saves the cache after the job completes.

## Full Workflow Example

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0
        with:
          version: "0.6.x"
          enable-cache: true
          cache-dependency-glob: "**/uv.lock"
      - run: uv sync --frozen
      - run: uv run pytest
```

## Manual Cache (Alternate)

If you need more control over `restore-keys` or cache paths, use `actions/cache` directly:

```yaml
- uses: actions/cache@v4
  id: uv-cache
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
    restore-keys: |
      ${{ runner.os }}-uv-
```

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `enable-cache` | `"auto"` | Enable uv cache |
| `cache-dependency-glob` | `` `**/*requirements*.txt`, `**/*requirements*.in`, `**/*constraints*.txt`, `**/*constraints*.in`, `**/pyproject.toml`, `**/uv.lock`, `**/*.py.lock` `` | Glob for lockfile hash |
| `cache-local-path` | temp dir (`/tmp/setup-uv-cache` on Linux) | Cache directory path |
| `version` | latest (after checking config files) | uv version to install |

See [uv-cache-dependency-glob](./uv-cache-dependency-glob.md) for advanced glob patterns.
