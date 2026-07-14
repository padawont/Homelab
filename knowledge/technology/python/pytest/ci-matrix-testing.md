---
title: "Python Version Matrix Testing"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest
  - ci
  - matrix
  - github-actions
sources:
  - url: "https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs"
    title: "GitHub Actions — Matrix Strategy"
last_audit_date: 2026-06-09
---

# Python Version Matrix Testing

Run tests across multiple Python versions using GitHub Actions matrix strategy.

## Matrix Workflow

```yaml
name: Test Matrix
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
      fail-fast: false

    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/setup-uv@v8.2.0
        with:
          python-version: ${{ matrix.python-version }}
          enable-cache: true
      - run: uv sync
      - run: uv run pytest -v --tb=short
```

## Additional Matrix Dimensions

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
    os: [ubuntu-latest, windows-latest, macos-latest]
    include:
      - python-version: "3.13"
        os: ubuntu-latest
```

## Including Experimental Combinations

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
    experimental: [false]
    include:
      - python-version: "3.13-dev"
        experimental: true
  fail-fast: false
```

## Test Result Collection

Use `continue-on-error` for experimental versions:

```yaml
- name: Run tests
  run: uv run pytest -v --tb=short
  continue-on-error: ${{ matrix.experimental || false }}
```

See [ci-github-actions-run](./ci-github-actions-run.md) for the base workflow and [ci-coverage-reporting](./ci-coverage-reporting.md) for coverage collection.
