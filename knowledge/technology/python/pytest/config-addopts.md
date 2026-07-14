---
title: "Default CLI Options with addopts"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - configuration
  - addopts
sources:
  - url: "https://docs.pytest.org/en/stable/reference/customize.html#confval-addopts"
    title: "pytest — addopts Configuration"
last_audit_date: 2026-06-09
---

# Default CLI Options with addopts

`addopts` specifies default command-line options that are always prepended when running pytest.

## Basic Usage

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "-v --tb=short --strict-markers"
```

In `pytest.ini`:

```ini
[pytest]
addopts = -v --tb=short
```

## Common Patterns

```toml
[tool.pytest.ini_options]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=xml",
    "-p no:cacheprovider",
]
```

## Overriding addopts

Pass `-o "addopts="` on the CLI to clear addopts for a single run:

```bash
uv run pytest -o "addopts="
```

## Best Practices

- Use `-v` for verbose output by default.
- Add `--strict-markers` to catch unknown markers early.
- Include coverage flags if you always want coverage.
- Keep addopts short in shared configs; let CI override with explicit flags.

See [config-pyproject-toml](./config-pyproject-toml.md) and [config-pytest-ini](./config-pytest-ini.md).
