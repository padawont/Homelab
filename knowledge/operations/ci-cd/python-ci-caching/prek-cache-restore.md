---
title: "Prek Cache Restore Patterns"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - prek
  - pre-commit
  - restore-keys
sources: []
last_audit_date: 2026-06-09
---

# Prek Cache Restore Patterns

Restoring prek caches requires handling the pre-commit environment directory structure correctly.

## Cache Path

Pre-commit stores hook environments under:

```
~/.cache/pre-commit/
├── <hash1>/  # Python hook environments
├── <hash2>/
└── ...
```

Each hash corresponds to a unique hook + Python version combination.

## Restore and Validate

```yaml
- uses: actions/cache@v4
  id: prek-cache
  with:
    path: ~/.cache/pre-commit
    key: ${{ runner.os }}-precommit-${{ hashFiles('.pre-commit-config.yaml') }}
    restore-keys: |
      ${{ runner.os }}-precommit-

- name: Install pre-commit
  run: uv tool install pre-commit

- name: Run pre-commit (restore hooks if needed)
  run: pre-commit run --all-files
```

On cache hit, `pre-commit run` skips installation and runs immediately. On miss, pre-commit installs hooks (takes 30–90s).

## Forcing Re-installation

```yaml
- name: Clean pre-commit cache
  if: steps.prek-cache.outputs.cache-hit != 'true'
  run: rm -rf ~/.cache/pre-commit

- name: Install and run hooks
  run: |
    pre-commit install --install-hooks
    pre-commit run --all-files
```

## Combined Dependency + Prek Cache

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/uv
      ~/.cache/pre-commit
    key: ${{ runner.os }}-${{ hashFiles('**/uv.lock', '.pre-commit-config.yaml') }}
```

## Manual Purge

If the prek cache grows too large, purge it in a scheduled workflow:

```yaml
- name: Purge pre-commit cache
  run: pre-commit clean
```

See [prek-caching-overview](./prek-caching-overview.md) for the introduction.
