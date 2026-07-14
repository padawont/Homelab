---
title: "Python Setup with uv in GHA"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - python
  - uv
  - setup
  - actions
  - astral-sh
sources:
  - url: "https://github.com/astral-sh/setup-uv"
    title: "astral-sh/setup-uv"
last_audit_date: 2026-06-10
---

# Python Setup with uv in GHA

Use `astral-sh/setup-uv` to install Python and uv in GitHub Actions.

## Basic Setup

```yaml
steps:
  - uses: actions/checkout@v6
  - uses: astral-sh/setup-uv@v8.2.0
    with:
      python-version: "3.13"
  - run: uv run pytest
```

## Without Specifying Python Version

If `pyproject.toml` specifies a `requires-python`, uv resolves the version natively — no `python-version` input needed:

```yaml
steps:
  - uses: astral-sh/setup-uv@v8.2.0
  - run: uv run pytest   # uv reads requires-python from pyproject.toml
```

## Installing uv Version

```yaml
steps:
  - uses: astral-sh/setup-uv@v8.2.0
    with:
      version: "0.11.20"
      python-version: "3.13"
```

## Enable Caching

```yaml
steps:
  - uses: astral-sh/setup-uv@v8.2.0
    with:
      enable-cache: true
      cache-dependency-glob: "uv.lock"
```

## Multi-Version Matrix

```yaml
strategy:
  matrix:
    python-version: ["3.12", "3.13"]
steps:
  - uses: astral-sh/setup-uv@v8.2.0
    with:
      python-version: ${{ matrix.python-version }}
```

## See Also

- [python-cache-uv.md](./python-cache-uv.md) — uv caching
- [python-run-pytest.md](./python-run-pytest.md) — Run tests with uv
- [python-run-ruff.md](./python-run-ruff.md) — Lint with uv
