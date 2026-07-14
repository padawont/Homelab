---
title: "Type Check with mypy in GHA"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - python
  - mypy
  - type-checking
  - uv
sources:
  - url: "https://mypy-lang.org/"
    title: "mypy Documentation"
last_audit_date: 2026-06-09
---

# Type Check with mypy in GHA

Run mypy for static type checking using `uv run` in GitHub Actions.

## Basic Workflow

```yaml
steps:
  - uses: actions/checkout@v6
  - uses: astral-sh/setup-uv@v8.2.0
    with:
      python-version: "3.13"
  - run: uv sync
  - run: uv run mypy src
```

## With Strict Mode

```yaml
steps:
  - uses: astral-sh/setup-uv@v8.2.0
  - run: uv run mypy src --strict
```

## With Configuration File

If you have a `pyproject.toml` mypy config:

```toml
[tool.mypy]
strict = true
ignore_missing_imports = true
exclude = ["tests/", "migrations/"]
```

Then simply:

```yaml
steps:
  - run: uv run mypy
```

## Cache mypy Results

```yaml
steps:
  - uses: actions/cache@v5
    with:
      path: .mypy_cache
      key: mypy-${{ runner.os }}-${{ hashFiles('uv.lock') }}
  - run: uv run mypy src --cache-dir .mypy_cache
```

## Best Practices

- Run mypy after ruff (formatting failures can cause false positives)
- Error codes are shown by default; use `--hide-error-codes` to suppress them
- Run on `src/` or specific modules, not the entire repo
- Pin mypy version in dev dependencies for reproducible results

## See Also

- [python-run-ruff.md](./python-run-ruff.md) — Linting with ruff
- [python-run-pytest.md](./python-run-pytest.md) — Running tests
