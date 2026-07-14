---
title: "Lint with ruff in GHA"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - python
  - ruff
  - linting
  - uv
sources:
  - url: "https://docs.astral.sh/ruff/"
    title: "ruff Documentation"
last_audit_date: 2026-06-09
---

# Lint with ruff in GHA

Run ruff linter and formatter using `uvx` in GitHub Actions.

## Basic Lint Check

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: astral-sh/setup-uv@v8.2.0
  - run: uvx ruff check
```

## Lint with Auto-Fix

```yaml
steps:
  - uses: astral-sh/setup-uv@v8.2.0
  - run: uvx ruff check --fix
```

## Format Check

```yaml
steps:
  - uses: astral-sh/setup-uv@v8.2.0
  - run: uvx ruff format --check
```

## Using pip-based venv (via uv)

If ruff is a dev dependency in pyproject.toml:

```yaml
steps:
  - uses: astral-sh/setup-uv@v8.2.0
  - run: uv sync
  - run: uv run ruff check
```

## Combined Lint + Format + Type Check

```yaml
steps:
  - uses: astral-sh/setup-uv@v8.2.0
  - run: |
      uvx ruff check
      uvx ruff format --check
      uv run mypy src
```

## Best Practices

- Pin ruff version in `pyproject.toml` for reproducible CI
- Use `uvx ruff check` for one-off runs (no install needed)
- Use `uv run ruff` when ruff is a project dependency
- Run lint before tests to fail fast on style issues
- Use `--output-format=github` for annotations in PRs

## See Also

- [python-run-mypy.md](./python-run-mypy.md) — Type checking
- [python-run-pytest.md](./python-run-pytest.md) — Running tests
- [GitHub Actions Integration (Ruff)](../../../technology/python/ruff/integration-github-actions.md) — Comprehensive GHA integration guide (official action, pip/uvx, version pinning, caching, PR annotations)
