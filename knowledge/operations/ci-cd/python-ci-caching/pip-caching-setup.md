---
title: "pip Caching via actions/setup-python"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - pip
  - setup-python
  - legacy
sources:
  - url: "https://github.com/actions/setup-python"
    title: "actions/setup-python on GitHub"
last_audit_date: 2026-06-10
---

# pip Caching via actions/setup-python

`actions/setup-python` has a built-in `cache: pip` option that automatically caches the pip directory. This note documents the approach for legacy projects still using pip.

## Built-in Cache

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
    cache: pip
```

This is equivalent to:

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
- uses: actions/cache@v5
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt', '**/pyproject.toml') }}
```

> **Cross-platform note:** The `path: ~/.cache/pip` shown above is the Linux cache directory. On macOS the path is `~/Library/Caches/pip`, and on Windows it is `%LocalAppData%\pip\Cache`. When using `actions/setup-python`'s built-in `cache: pip`, it handles the correct path for each runner OS automatically. If migrating to a manual `actions/cache` step, use `${{ runner.os }}`-conditional path logic or reference the runner's OS-specific cache directory.

## Limitations

- **No restore-keys control** — the built-in cache does not expose `restore-keys` for fallback.
- **pip only** — only caches `~/.cache/pip`, not `.venv`.
- **Slow population** — pip is single-threaded for downloads.

## When to Use

- Legacy projects that still use `pip install` and `requirements.txt`.
- Migrating away from this in favor of uv is recommended.

## Migration Path

1. Replace `actions/setup-python` cache with manual `actions/cache` for `~/.cache/pip`.
2. Add uv installation via `astral-sh/setup-uv`.
3. Replace `pip install` with `uv sync`.
4. See [uv-caching-install](./uv-caching-install.md) for the target setup.

See [pip-vs-uv-tradeoffs](./pip-vs-uv-tradeoffs.md) for a full comparison.
