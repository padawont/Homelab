---
title: "uv cache-dependency-glob Patterns"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - uv
  - cache-dependency-glob
sources:
  - url: "https://github.com/astral-sh/setup-uv"
    title: "astral-sh/setup-uv on GitHub"
last_audit_date: 2026-06-09
---

# uv cache-dependency-glob Patterns

When using `astral-sh/setup-uv` with `enable-cache: true`, the `cache-dependency-glob` parameter controls which files contribute to the cache key hash.

## Minimal Pattern

```yaml
cache-dependency-glob: "**/uv.lock"
```

> **Note:** The action's actual `cache-dependency-glob` default is broader — it tracks `**/*requirements*.txt`, `**/*requirements*.in`, `**/*constraints*.txt`, `**/*constraints*.in`, `**/pyproject.toml`, `**/uv.lock`, and `**/*.py.lock`. The single `**/uv.lock` shown here is a minimal override for projects that only need the lockfile.

This hashes every `uv.lock` in the repository. If any changes, the cache is invalidated.

## Monorepo Patterns

For monorepos with multiple Python projects, restrict the glob to specific directories:

```yaml
cache-dependency-glob: "packages/*/uv.lock"
```

Or for multiple explicit paths:

```yaml
cache-dependency-glob: |
  services/api/uv.lock
  services/worker/uv.lock
```

## Including pyproject.toml

If you want cache invalidation when project metadata changes (even without lockfile changes):

```yaml
cache-dependency-glob: |
  **/uv.lock
  **/pyproject.toml
```

## Multiple Globs

The parameter accepts a multi-line string. Each glob becomes part of the composite hash:

```yaml
cache-dependency-glob: |
  **/uv.lock
  **/requirements*.txt
```

## Best Practices

- Be as specific as possible to avoid unnecessary cache busts.
- In a monorepo, scope globs to the relevant subdirectory.
- When in doubt, use `**/uv.lock` — it is simple and correct for most projects.

See [uv-caching-install](./uv-caching-install.md) for the full setup-uv action reference.
