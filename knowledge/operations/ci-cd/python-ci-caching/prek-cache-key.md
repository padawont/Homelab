---
title: "Prek Cache Key Strategies"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - prek
  - pre-commit
  - cache-key
sources:
  - "https://pre-commit.com/#configuration"
  - "https://pre-commit.com/#creating-new-hooks"
  - "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
  - "https://github.com/pre-commit/action"
last_audit_date: 2026-06-09
---

# Prek Cache Key Strategies

Prek cache keys should encode the factors that determine which hook environments are installed.

## Primary Key: Config Hash

The `.pre-commit-config.yaml` determines which hooks and versions are used:

> **Note:** `.pre-commit-hooks.yaml` is a **hook-author manifest** — it declares the hooks a repository *provides*, not what a user *installs*. It is owned by upstream hook authors (e.g., `pre-commit/pre-commit-hooks`). Do not hash it in cache keys; it changes independently of your config and would invalidate prek needlessly.

```yaml
key: ${{ runner.os }}-precommit-${{ hashFiles('.pre-commit-config.yaml') }}
```

## Including Additional Files

If hooks reference local config (e.g., `.ruff.toml`, `pyproject.toml`), include those:

```yaml
key: ${{ runner.os }}-precommit-${{ hashFiles('.pre-commit-config.yaml', '.ruff.toml', 'pyproject.toml') }}
```

## OS Factor

Always include `${{ runner.os }}` — hook environments contain platform-specific binaries:

```yaml
key: ${{ runner.os }}-precommit-${{ hashFiles('.pre-commit-config.yaml') }}
```

## Python Version Factor

If your `.pre-commit-config.yaml` uses `python` as the language for hooks, include Python version:

```yaml
key: ${{ runner.os }}-py${{ matrix.python-version }}-precommit-${{ hashFiles('.pre-commit-config.yaml') }}
```

## Minimal Fallback

```yaml
restore-keys: |
  ${{ runner.os }}-precommit-
```

## Best Practices

- Keep keys as narrow as possible — config-only changes rarely happen.
- Use `restore-keys` to salvage prek caches when config changes slightly.
- If hooks use `node` or `docker` language, include additional relevant hashes.

See [prek-caching-overview](./prek-caching-overview.md) for the introduction and [prek-cache-restore](./prek-cache-restore.md) for restore patterns.
