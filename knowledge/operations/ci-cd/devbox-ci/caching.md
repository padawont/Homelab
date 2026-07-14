---
title: "Devbox CI/CD — Caching"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "ci-cd", "caching", "cachix"]
sources:
  - url: "https://github.com/actions/cache"
    title: "actions/cache — GitHub Action for caching dependencies"
  - url: "https://github.com/cachix/cachix-action"
    title: "cachix/cachix-action — Cachix binary cache GitHub Action"
  - url: "https://github.com/jetify-com/devbox-install-action"
    title: "jetify-com/devbox-install-action — Devbox install GitHub Action"
  - url: "https://github.com/jetify-com/devbox-install-action/blob/main/action.yml"
    title: "devbox-install-action/action.yml — Action definition reference"
last_audit_date: 2026-05-24
---

# Caching Strategies

## Devbox Built-in Cache (recommended)

The `devbox-install-action` has built-in cache support via `enable-cache: 'true'`. This is the simplest approach — it caches the full Nix store based on your `devbox.lock` hash.

Cache key = hash of `devbox.lock` + runner OS/architecture + Nix version. On exact hit, the Nix store is fully restored. On miss, packages build from source and are cached for future runs.

## Cachix Binary Cache

For teams that want a shared persistent cache across developers and CI, use [Cachix](https://cachix.org/):

```yaml
- uses: cachix/cachix-action@v17
  with:
    name: my-team-cache
    authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
    signingKey: '${{ secrets.CACHIX_SIGNING_KEY }}'
```

Cachix pushes newly built packages after each job and pulls them before subsequent runs. This is useful when multiple repositories share common dependencies.

## Manual Cache (actions/cache)

If you need custom cache key logic:

```yaml
- name: Cache Nix store
  uses: actions/cache@v5
  with:
    path: /nix/store
    key: ${{ runner.os }}-nix-${{ hashFiles('devbox.lock') }}
```

**Note:** The Nix store is read-only. This approach can have permission issues — prefer the Devbox built-in cache or Cachix.
