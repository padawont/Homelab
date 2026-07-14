---
title: "Marker Registration"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - marks
  - configuration
sources:
  - url: "https://docs.pytest.org/en/stable/how-to/mark.html#registering-markers"
    title: "pytest — Registering Markers"
last_audit_date: 2026-06-09
---

# Marker Registration

Register custom markers to prevent `PytestUnknownMarkWarning` and enable IDE support.

## In pyproject.toml

```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "smoke: marks tests for smoke test suite",
    "issue(id): link to a GitHub issue",
]
```

## In pytest.ini

```ini
[pytest]
markers =
    slow: marks tests as slow
    integration: marks tests that need external services
    smoke: quick checks for the build pipeline
```

## In conftest.py (runtime registration)

```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line(
        "markers", "issue(id): link test to a specific issue"
    )
```

## Using --strict-markers

Enable `--strict-markers` in [addopts](./config-addopts.md) so that any unregistered marker raises an error:

```toml
[tool.pytest.ini_options]
addopts = "--strict-markers"
```

This catches typos in marker names at collection time.

See [marks-custom](./marks-custom.md) for using custom markers in tests.
