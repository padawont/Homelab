---
title: "pytest.ini Configuration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - configuration
  - pytest-ini
sources:
  - url: "https://docs.pytest.org/en/stable/reference/customize.html#configuration-file-formats"
    title: "pytest — Configuration File Formats"
last_audit_date: 2026-06-09
---

# pytest.ini Configuration

`pytest.ini` is the traditional pytest configuration file. It lives in the project root or test root directory.

## Basic Structure

```ini
[pytest]
testpaths = tests
minversion = 8.0
addopts = -v --tb=short -p no:cacheprovider
```

## Common Options

```ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
norecursedirs = .git venv __pycache__

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: integration tests requiring external services

filterwarnings =
    error
    ignore::DeprecationWarning

log_cli = true
log_cli_level = DEBUG
```

## Precedence

1. `pytest.ini` in the project root
2. `pyproject.toml` `[tool.pytest.ini_options]`
3. `tox.ini` `[pytest]` section
4. `setup.cfg` `[tool:pytest]` section

If both `pytest.ini` and `pyproject.toml` exist, `pytest.ini` takes precedence.

See [config-pyproject-toml](./config-pyproject-toml.md) for the modern alternative.
