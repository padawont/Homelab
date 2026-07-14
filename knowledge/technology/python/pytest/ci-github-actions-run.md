---
title: "pytest in GitHub Actions with uv"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - ci
  - github-actions
  - uv
sources:
  - url: "https://docs.pytest.org/en/stable/"
    title: "pytest Documentation"
last_audit_date: 2026-06-09
---

# pytest in GitHub Actions with uv

Run pytest in CI using `uv run` for dependency management.

## Basic Workflow

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@v8.2.0
        with:
          enable-cache: true
      - run: uv sync
      - run: uv run pytest -v --tb=short
```

## With Coverage

```yaml
- run: uv run pytest --cov=src --cov-report=xml --cov-report=term-missing
- uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
```

## Selective Test Execution

```yaml
- run: uv run pytest -m "not slow" -v
  if: github.event_name == 'push'

- run: uv run pytest -v
  if: github.event_name == 'pull_request'
```

## Using Services

```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: testdb
    ports:
      - 5432:5432
```

See [ci-matrix-testing](./ci-matrix-testing.md) for multi-version testing and [ci-coverage-reporting](./ci-coverage-reporting.md) for coverage upload patterns.
