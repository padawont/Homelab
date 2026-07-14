---
title: "pytest Config in pyproject.toml"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - configuration
  - pyproject-toml
sources:
  - url: "https://docs.pytest.org/en/stable/reference/customize.html#pyproject-toml"
    title: "pytest — pyproject.toml Configuration"
last_audit_date: 2026-06-09
---

# pytest Config in pyproject.toml

Configure pytest under the `[tool.pytest.ini_options]` section of `pyproject.toml`.

## Minimal Example

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
minversion = "8.0"
addopts = "-v --tb=short"
```

## Common Settings

```toml
[tool.pytest.ini_options]
testpaths = ["tests", "integration"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

asyncio_mode = "auto"  # For pytest-asyncio (see pytest-asyncio-installation.md)

markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]

filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
]

log_cli = true
log_cli_level = "INFO"
```

## Comparison with pytest.ini

- `pyproject.toml` is the modern, single-file configuration approach.
- Use `pytest.ini` when you want pytest-specific config separate from project metadata.
- Settings in `pytest.ini` override `pyproject.toml` if both exist.

See [config-pytest-ini](./config-pytest-ini.md), [config-addopts](./config-addopts.md), [config-testpaths](./config-testpaths.md).

## Pytest 9.0+ Config Formats

Starting with pytest 9.0, two new configuration approaches are available:

### `[tool.pytest]` Native TOML Table

In addition to `[tool.pytest.ini_options]`, pytest 9.0 supports a native `[tool.pytest]` table in `pyproject.toml`. This avoids the legacy `ini_options` wrapper and feels more idiomatic for a TOML-based project:

```toml
[tool.pytest]
testpaths = ["tests"]
minversion = "9.0"
addopts = "-v --tb=short"
```

If both `[tool.pytest]` and `[tool.pytest.ini_options]` are present, pytest raises an error — the two tables cannot be used at the same time.

### `pytest.toml` / `.pytest.toml` Files

pytest 9.0 also introduces standalone TOML config files:

- **`pytest.toml`** — version-controlled project config (placed in the project root).
- **`.pytest.toml`** — hidden file variant (useful when you prefer dotfiles).

These files use the same native `[tool.pytest]` table structure and can serve as an alternative to adding pytest configuration inside `pyproject.toml`. This is analogous to using `pytest.ini` when you want pytest-specific config separate from the project's main TOML file.

See [the pytest 9.0 changelog](https://docs.pytest.org/en/stable/changelog.html) for details.
