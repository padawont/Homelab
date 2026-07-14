---
title: "Run pytest with uv in GHA"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - python
  - pytest
  - testing
  - uv
sources:
  - url: "https://docs.pytest.org/en/stable/"
    title: "pytest Documentation"
last_audit_date: 2026-06-09
---

# Run pytest with uv in GHA

Run pytest using `uv run` in GitHub Actions.

## Minimal Workflow Step

```yaml
steps:
  - uses: actions/checkout@v6
  - uses: astral-sh/setup-uv@v8.2.0
    with:
      python-version: "3.13"
  - run: uv run pytest
```

## With Coverage

```yaml
steps:
  - uses: astral-sh/setup-uv@v8.2.0
  - run: uv run pytest --cov=src --cov-report=xml --cov-report=term
  - uses: codecov/codecov-action@v5
    with:
      files: ./coverage.xml
```

## With JUnit XML Output

```yaml
steps:
  - uses: astral-sh/setup-uv@v8.2.0
  - run: uv run pytest --junitxml=test-results.xml
  - uses: actions/upload-artifact@v7
    if: always()
    with:
      name: test-results
      path: test-results.xml
```

## Matrix Strategy

```yaml
strategy:
  matrix:
    python-version: ["3.12", "3.13"]
steps:
  - uses: astral-sh/setup-uv@v8.2.0
    with:
      python-version: ${{ matrix.python-version }}
  - run: uv run pytest -v
```

## Best Practices

- Use `-v` flag for verbose output
- Use `--tb=short` to keep logs manageable
- Combined coverage reports across matrix runs with Codecov
- Use `uv sync --dev` to install dev dependencies before running tests

## See Also

- [python-setup-uv.md](./python-setup-uv.md) — uv setup
- [python-cache-uv.md](./python-cache-uv.md) — uv caching
- [jobs-strategy-matrix.md](./jobs-strategy-matrix.md) — Matrix strategy
