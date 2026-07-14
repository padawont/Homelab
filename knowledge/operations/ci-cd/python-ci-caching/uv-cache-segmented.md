---
title: "UV Cache Segments"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - uv
  - cache-segments
sources:
  - url: "https://docs.astral.sh/uv/concepts/cache/"
    title: "uv caching documentation"
  - url: "https://github.com/astral-sh/uv/blob/main/crates/uv-cache/src/lib.rs"
    title: "uv cache source (CacheBucket enum)"
last_audit_date: 2026-06-10
---

# UV Cache Segments

uv organizes its global cache into 12 buckets, each with a specific purpose. Understanding these segments helps optimize CI caching strategies.

## Cache Directory Layout

```
~/.cache/uv/
├── sdists-v9/           # Source distributions and wheels built from source
├── wheels-v6/           # Downloaded pre-built wheels and their metadata
├── archive-v0/          # Unzipped wheel store (internal, referenced by symlink)
├── git-v0/              # Git dependencies (cloned repositories)
├── simple-v21/          # Simple metadata API responses (PyPI index)
├── flat-index-v2/       # Flat index (`--find-links`) responses
├── interpreter-v4/      # Cached Python interpreter information
├── builds-v0/           # Ephemeral virtual environments for PEP 517 builds
├── environments-v2/     # Reusable virtual environments for Python tools
├── python-v0/           # Downloaded Python installations
├── binaries-v0/         # Downloaded tool binaries (e.g., Ruff)
└── osv-v0/              # Cached vulnerability data from OSV
```

## Segment Characteristics

| Segment | Size | Rebuild Cost | Cached in CI | Notes |
|---|---|---|---|---|
| `wheels-v6` | Large | Low (download only) | Yes | Pre-built wheels; `uv cache prune --ci` removes these |
| `sdists-v9` | Medium | Medium (compile) | Yes | Source dists and their built wheels; the key segment to cache |
| `archive-v0` | Large | High (copy) | Yes (indirect) | Internal unzipped wheel store; managed automatically |
| `git-v0` | Variable | Medium | Yes | Full git clones of VCS dependencies |
| `simple-v21` | Small | Low | Yes | Index metadata; enables fast resolution |
| `flat-index-v2` | Small | Low | Yes | Flat index responses |
| `interpreter-v4` | Small | None | No | Transient; recomputed on demand |
| `builds-v0` | Medium | None | No | Ephemeral; cleaned after each build |
| `environments-v2` | Medium | None | No | Tool venvs; short-lived |
| `python-v0` | Large | High (download) | Yes | Python downloads; valuable but large |
| `binaries-v0` | Medium | High (download) | Yes | Tool binaries like Ruff |
| `osv-v0` | Small | Low | No | Vulnerability data; fetched on demand |

## Cache Granularity

You can cache specific segments if disk space is constrained. The most valuable segments for CI are pre-built wheels and built source distributions:

```yaml
- uses: actions/cache@v5
  with:
    path: |
      ~/.cache/uv/sdists-v9
      ~/.cache/uv/git-v0
    key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
```

To also cache pre-built wheels (trade-off: larger cache, potentially slower restores):

```yaml
- uses: actions/cache@v5
  with:
    path: |
      ~/.cache/uv/wheels-v6
      ~/.cache/uv/sdists-v9
      ~/.cache/uv/git-v0
    key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
```

## Why Segment Separately?

- **Selective eviction** — if the uv tool itself changes, only segments affected by the tool version need rebuilding (e.g., `sdists-v9` → `sdists-v10`, `wheels-v6` → `wheels-v7`).
- **Shared cache** — in self-hosted runners, segments can be shared across projects with compatible requirements.
- **CI pruning** — `uv cache prune --ci` removes `wheels-v6` entries (pre-built wheels) while retaining `sdists-v9` (built-from-source wheels), balancing cache size vs. rebuild cost.

## Cache Versioning

Each bucket is independently versioned. When a uv release changes a bucket's format, the version suffix increments (e.g., `wheels-v6` → `wheels-v7`). uv never reads from or writes to an incompatible bucket, so multiple uv versions can safely share the same cache directory without conflicts.

| Bucket | Current Version | Description |
|---|---|---|
| `sdists-v9` | v9 | Source distributions and built wheels |
| `wheels-v6` | v6 | Pre-built (downloaded) wheels |
| `archive-v0` | v0 | Internal unzipped wheel store |
| `git-v0` | v0 | Git repository clones |
| `simple-v21` | v21 | Simple metadata API (rkyv format) |
| `flat-index-v2` | v2 | Flat index responses |
| `interpreter-v4` | v4 | Python interpreter metadata |
| `builds-v0` | v0 | Ephemeral build environments |
| `environments-v2` | v2 | Reusable tool environments |
| `python-v0` | v0 | Python downloads |
| `binaries-v0` | v0 | Tool binary downloads |
| `osv-v0` | v0 | OSV vulnerability data |

## Recommendation

Cache the entire `~/.cache/uv` directory unless disk space is extremely constrained. uv efficiently manages segment I/O and `uv cache prune --ci` handles size control automatically.

See [cache-path-uv](./cache-path-uv.md) for the standard caching setup, and [uv-caching-install](./uv-caching-install.md) for the recommended CI workflow.
