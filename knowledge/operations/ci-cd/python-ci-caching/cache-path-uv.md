---
title: "UV Cache Directory (~/.cache/uv)"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - uv
  - cache-path
sources:
  - url: "https://docs.astral.sh/uv/concepts/cache/"
    title: "uv caching documentation"
last_audit_date: 2026-06-10
---

# UV Cache Directory (~/.cache/uv)

uv maintains a global cache at `~/.cache/uv` (Linux/macOS) or `%LOCALAPPDATA%\uv\cache` (Windows). This cache is the primary target for CI caching.

## Cache Structure

```
~/.cache/uv/
├── sdists-v9/          # Source distributions and built wheels
├── wheels-v6/          # Downloaded pre-built wheels
├── archive-v0/         # Unzipped wheel store (internal)
├── simple-v21/         # Package index metadata
├── git-v0/             # Git dependencies
└── ...                 # 7 more buckets (see uv-cache-segmented.md)
```

> **Note:** The specific subdirectory names shown above (`sdists-v9`, `wheels-v6`, etc.) are uv internal implementation details and may change between releases. Always reference the top-level cache directory — not individual subdirectories — in CI cache configuration.

uv automatically manages cache segments internally. See [uv-cache-segmented](./uv-cache-segmented.md) for detail.

## CI Cache Step

```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    env:
      UV_CACHE_DIR: /tmp/.uv-cache
    steps:
      - uses: actions/cache@v5
        with:
          path: /tmp/.uv-cache
          key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
          restore-keys: |
            ${{ runner.os }}-uv-

      - name: Install dependencies
        run: uv sync --frozen

      - name: Prune uv cache
        run: uv cache prune --ci
```

## Performance Notes

- uv's cache is **concurrent-safe** — multiple uv processes can read/write simultaneously.
- Cache population is fast because uv downloads and builds in parallel.
- Typical cache size: 100–500 MB for a medium-sized project.
- See [benchmark-uv-timing](./benchmark-uv-timing.md) for real timing data.

## Eviction

GitHub Actions caches are automatically evicted after 7 days of inactivity. The uv cache can be rebuilt on cache miss with minimal overhead due to uv's parallelism.
