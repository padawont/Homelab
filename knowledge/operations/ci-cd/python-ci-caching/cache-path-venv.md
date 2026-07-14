---
title: ".venv Directory Cache"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - uv
  - venv
  - cache-path
sources:
  - url: "https://docs.astral.sh/uv/"
    title: "uv documentation"
last_audit_date: 2026-06-09
---

# .venv Directory Cache

Caching the `.venv` directory directly saves time by avoiding re-creation of the virtual environment and re-linking of dependencies on every CI run.

## When to Cache .venv

- **Recommended** for most projects — `uv sync` on a restored `.venv` is near-instant.
- The alternative is caching `~/.cache/uv` only and rebuilding `.venv` from scratch each time.

## CI Cache Step

```yaml
- uses: actions/cache@v5
  id: venv-cache
  with:
    path: .venv
    key: ${{ runner.os }}-venv-${{ matrix.python-version }}-${{ hashFiles('**/uv.lock') }}
    restore-keys: |
      ${{ runner.os }}-venv-${{ matrix.python-version }}-
```

## uv sync with Cached .venv

```yaml
- name: Install dependencies
  run: uv sync --frozen
```

If `.venv` is restored from cache, `uv sync --frozen` only performs a quick validation pass in most cases. If the hash changed (cache miss), uv populates `.venv` from `~/.cache/uv`.

## Path Considerations

| Aspect | Detail |
|---|---|
| Default venv path | `.venv` in project root |
| uv respects | `$VIRTUAL_ENV` if set |
| Cache size | 50–300 MB depending on dependency count |

The `.venv` size is smaller than the underlying `~/.cache/uv` (100–500 MB, see [cache-path-uv](./cache-path-uv.md)) because uv uses hardlink deduplication — `.venv` links to cached wheels rather than duplicating them.

## Dual Caching Strategy

For maximum speed, cache **both** `~/.cache/uv` and `.venv`:

```yaml
- uses: actions/cache@v5
  with:
    path: |
      ~/.cache/uv
      .venv
    key: ${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/uv.lock') }}
```

See [uv-caching-install](./uv-caching-install.md) for the complete setup.
