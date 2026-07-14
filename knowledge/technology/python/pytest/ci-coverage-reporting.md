---
title: "Coverage Reporting in CI"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - pytest-cov
  - coverage
  - ci
  - github-actions
sources:
  - url: "https://docs.codecov.com/docs"
    title: "Codecov Documentation"
last_audit_date: 2026-06-09
---

# Coverage Reporting in CI

Upload coverage results to services like Codecov, Coveralls, or enforce thresholds directly.

## Codecov Upload

```yaml
- name: Run tests with coverage
  run: uv run pytest --cov=src --cov-report=xml --cov-report=term-missing

- name: Upload to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    token: ${{ secrets.CODECOV_TOKEN }}
```

## Fail-Under in CI

```yaml
- name: Run tests with coverage threshold
  run: uv run pytest --cov=src --cov-report=xml --cov-fail-under=80
```

## Combined Matrix Coverage

Upload from each matrix job with a unique flag:

```yaml
- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    flags: unittests
    name: codecov-umbrella
```

## Without External Service

Use built-in threshold enforcement:

```toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"
```

## Coverage Badge

After upload, add a Codecov badge to the project README:

```markdown
[![codecov](https://codecov.io/gh/org/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/org/repo)
```

See [pytest-cov-thresholds](./pytest-cov-thresholds.md) for threshold configuration and [pytest-cov-omit](./pytest-cov-omit.md) for file exclusions.
