---
title: "Python Version in Cache Key"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - cache-key
  - python-version
  - uv
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
    title: "GitHub Actions Caching Documentation"
last_audit_date: 2026-06-09
---

# Python Version in Cache Key

Include Python version in the cache key when caching `.venv` or any directory containing compiled artifacts.

## When Python Version Matters

- `.venv` directories contain Python-version-specific binaries (`.so`, `.pyd`).
- If your matrix tests multiple Python versions against the same lockfile, the `.venv` for Python 3.11 is invalid for Python 3.12.

## Example

```yaml
- uses: actions/cache@v5
  id: venv-cache
  with:
    path: .venv
    key: ${{ runner.os }}-venv-${{ matrix.python-version }}-${{ hashFiles('**/uv.lock') }}
    restore-keys: |
      ${{ runner.os }}-venv-${{ matrix.python-version }}-
```

## Not Always Needed

- The `~/.cache/uv` directory stores **source distributions** and **pre-built wheels** indexed by Python version internally. uv manages version separation automatically.
- For `~/.cache/pip`, pip also handles version separation internally, so Python version in the key is less critical for the pip cache itself.

## Recommendation

| Cache Target | Include Python Version? |
|---|---|
| `~/.cache/uv` | No (uv handles it internally) |
| `.venv` | Yes |
| `~/.cache/pip` | No (pip handles it internally) |
