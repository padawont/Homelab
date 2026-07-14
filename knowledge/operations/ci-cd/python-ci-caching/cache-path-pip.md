---
title: "pip Cache Directory (~/.cache/pip)"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - pip
  - cache-path
sources:
  - url: "https://pip.pypa.io/en/stable/topics/caching/"
    title: "pip caching documentation"
last_audit_date: 2026-06-09
---

# pip Cache Directory (~/.cache/pip)

This note describes the pip cache path for reference when comparing against uv caching strategies. New projects should use [uv](./cache-path-uv.md).

## Path

| OS | Default Cache Path |
|---|---|
| Linux | `~/.cache/pip` |
| macOS | `~/Library/Caches/pip` |
| Windows | `%LocalAppData%\pip\Cache` |

## Cache Contents

- Downloaded wheel archives (`.whl` files)
- Source distributions (`.tar.gz` files)
- HTTP response metadata

## Usage in CI

```yaml
- uses: actions/cache@v5
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt', '**/pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

## Limitations

- pip does not cache compiled extensions across Python version upgrades as efficiently as uv.
- The pip cache is single-threaded by default, making it slower to populate.
- See [pip-vs-uv-tradeoffs](./pip-vs-uv-tradeoffs.md) for a full comparison.
