---
title: "Matrix Builds"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - matrix
  - strategy
sources:
  - url: "https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs"
    title: "GitHub Actions: Matrix Strategy"
last_audit_date: 2026-06-09
---

# Matrix Builds

Use a matrix strategy to run a job across multiple configurations.

## Basic Matrix

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.12", "3.13"]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: astral-sh/setup-uv@v8.2.0
        with:
          python-version: ${{ matrix.python-version }}
      - run: uv run pytest
```

## include / exclude

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    python-version: ["3.12", "3.13"]
    include:
      - os: ubuntu-latest
        python-version: "3.14"
        experimental: true
    exclude:
      - os: macos-latest
        python-version: "3.13"
```

## Naming Matrix Jobs

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
    name: "Test on ${{ matrix.os }}"
```

## Key Points

- Maximum number of jobs defaults to 256 per workflow
- Use `include` for ad-hoc additions, `exclude` to prune combos
- Access matrix values via `${{ matrix.<key> }}`
- Combine with `fail-fast: false` to let all variants complete
