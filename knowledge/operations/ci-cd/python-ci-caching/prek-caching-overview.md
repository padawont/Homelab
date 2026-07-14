---
title: "Prek Caching — Introduction"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - prek
  - pre-commit
  - hooks
sources:
  - https://pre-commit.com/
  - https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows
last_audit_date: 2026-06-09
---

# Prek Caching — Introduction

Prek (pre-commit hooks) environments often require cached tool installations to avoid re-downloading linters, formatters, and type checkers on every CI run.

## Why Cache Prek Environments

- Tools like `ruff`, `mypy`, `black`, and `prettier` are downloaded on first pre-commit run.
- Each hook environment can be 10–200 MB.
- Without caching, every CI job re-downloads the same tool binaries.

## How Prek Caching Works

Prek installs hook environments in a cache directory (default: `~/.cache/pre-commit`). Caching this directory preserves installed hook environments between CI runs.

## Basic CI Cache

```yaml
- uses: actions/cache@v5
  with:
    path: ~/.cache/pre-commit
    key: ${{ runner.os }}-precommit-${{ hashFiles('.pre-commit-config.yaml') }}
    restore-keys: |
      ${{ runner.os }}-precommit-
```

## Running Prek with Cache

```yaml
- uses: actions/cache@v5
  id: prek-cache
  with:
    path: ~/.cache/pre-commit
    key: ${{ runner.os }}-precommit-${{ hashFiles('.pre-commit-config.yaml') }}

- name: Run pre-commit hooks
  run: uv tool run pre-commit run --all-files
```

See [prek-cache-key](./prek-cache-key.md) for key design strategies and [prek-cache-restore](./prek-cache-restore.md) for restore patterns.
