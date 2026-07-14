---
title: "Test Root Directories with testpaths"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - configuration
  - testpaths
sources:
  - url: "https://docs.pytest.org/en/stable/reference/customize.html#confval-testpaths"
    title: "pytest — testpaths Configuration"
last_audit_date: 2026-06-09
---

# Test Root Directories with testpaths

`testpaths` restricts test discovery to specific directories, improving startup speed.

## Basic Configuration

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

In `pytest.ini`:

```ini
[pytest]
testpaths = tests integration_tests
```

## Multiple Directories

```toml
testpaths = [
    "tests/unit",
    "tests/integration",
    "tests/e2e",
]
```

## How It Works

Without `testpaths`, pytest searches from the current directory recursively. With `testpaths`, it only scans those directories, ignoring other project files (docs, src, etc.).

## Best Practices

- Always set `testpaths` to avoid collecting non-test files.
- Use `norecursedirs` to exclude directories like `.git`, `venv`, `__pycache__`.
- `testpaths` is relative to the project root (where `pyproject.toml` or `pytest.ini` lives).

See [test-discovery](./test-discovery.md) for naming conventions and collection rules.
