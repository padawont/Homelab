---
title: "uv Caching in GHA"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - python
  - uv
  - caching
  - performance
sources:
  - url: "https://github.com/astral-sh/setup-uv/blob/main/docs/caching.md"
    title: "astral-sh/setup-uv: Caching Documentation"
last_audit_date: 2026-06-09
---

# uv Caching in GHA

Use the uv package cache in GitHub Actions to speed up dependency installation.

## Using setup-uv Built-in Cache

```yaml
steps:
  - uses: astral-sh/setup-uv@fac544c07dec837d0ccb6301d7b5580bf5edae39 # v8.2.0
    with:
      enable-cache: true
      cache-dependency-glob: "uv.lock"
```

## Manual Cache with actions/cache

```yaml
steps:
  - uses: actions/cache@v5
    id: uv-cache
    with:
      path: ~/.cache/uv
      key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
      restore-keys: |
        uv-${{ runner.os }}-

  - uses: astral-sh/setup-uv@fac544c07dec837d0ccb6301d7b5580bf5edae39 # v8.2.0
    with:
      enable-cache: false
  - if: steps.uv-cache.outputs.cache-hit != 'true'
    run: uv sync
  - run: uv run pytest
```

> **Note:** The `path: ~/.cache/uv` in this example is Linux-specific. See the [Cache Paths](#cache-paths) table below for macOS and Windows paths.

## Cache Key Strategy

| Key Strategy | Hit Rate | Notes |
|---|---|---|
| `hashFiles('uv.lock')` | High | Best for stable deps |
| `hashFiles('pyproject.toml')` | Medium | May invalidate too often |
| `runner.os` prefix | Fallback | Broad restore key |

## Cache Paths

| OS | Default Cache Path |
|---|---|
| Linux | `~/.cache/uv` |
| macOS | `~/.cache/uv` |
| Windows | `~\AppData\Local\uv\cache` |

> **Note on built-in vs. manual caching:** `setup-uv` enables caching by default (`auto`) on GitHub-hosted runners; you only need `enable-cache: true` if you want to force it on self-hosted runners. When setup-uv's caching is active, it overrides `UV_CACHE_DIR` to a temporary path (`/tmp/setup-uv-cache` on Linux/macOS, `D:\a\_temp\setup-uv-cache` on Windows) and manages the cache automatically — you do not need to specify a path. The paths in the table above are uv's *default* cache locations and should be used **only** when configuring manual caching with `actions/cache` (paired with `enable-cache: false` on `setup-uv`).

## See Also

- [python-setup-uv.md](./python-setup-uv.md) — uv setup
- [python-run-pytest.md](./python-run-pytest.md) — Running tests
