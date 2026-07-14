---
title: "actions/cache Overview"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - caching
  - ci
  - github-actions
  - actions-cache
sources:
  - url: "https://github.com/actions/cache"
    title: "actions/cache on GitHub"
  - url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
    title: "GitHub Actions Caching Documentation"
last_audit_date: 2026-06-09
---

# actions/cache Overview

The `actions/cache` action allows GitHub Actions workflows to cache files and directories between job runs, speeding up workflows by reusing previously computed data.

## How It Works

- A **cache key** identifies a unique cache entry.
- On save, the action archives the specified `path` and stores it under the key.
- On restore, if a cache entry matches the key (or a `restore-key`), the files are restored.

## Basic Usage

```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
    restore-keys: |
      ${{ runner.os }}-uv-
```

## Parameters

| Parameter | Required | Description |
|---|---|---|
| `path` | Yes | File/directory to cache (supports globs) |
| `key` | Yes | Unique cache key — cache miss if new |
| `restore-keys` | No | Ordered fallback keys for partial restore |

## Outputs

| Output | Description |
|---|---|
| `cache-hit` | `"true"` if exact key match, `"false"` if partial match via restore-key, empty string on complete cache miss |

See [cache-hit-detection](./cache-hit-detection.md) for how to use this output in conditional steps.
