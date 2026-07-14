---
title: "Devbox CI/CD — GitHub Actions"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "github-actions", "ci-cd"]
sources:
  - "https://www.jetify.com/docs/devbox/continuous-integration/github-action/"
  - "https://github.com/jetify-com/devbox-install-action"
last_audit_date: 2026-05-24
---

# GitHub Actions

The official [devbox-install-action](https://github.com/marketplace/actions/devbox-installer) installs the Devbox CLI, provisions Nix packages defined in `devbox.json`, and supports caching.

## Minimal Workflow

```yaml
name: CI with Devbox

on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install devbox
        uses: jetify-com/devbox-install-action@v0.15.0

      - name: Run tests
        run: devbox run test
```

## With Caching Enabled

```yaml
- name: Install devbox
  uses: jetify-com/devbox-install-action@v0.15.0
  with:
    enable-cache: 'true'
```

The cache key is derived from `devbox.lock`, runner OS/architecture, and the Nix version. A cache hit restores the full Nix store; a miss builds from scratch and saves the result.

## Full Configuration

```yaml
- name: Install devbox
  uses: jetify-com/devbox-install-action@v0.15.0
  with:
    project-path: 'path/to/project'   # default: repo root
    enable-cache: 'true'               # default: false
    refresh-cli: 'false'               # default: false
    devbox-version: '0.13.4'           # default: '' (resolves to latest)
    sha256-checksum: '<checksum>'      # optional
    skip-nix-installation: 'false'     # default: false
    disable-nix-access-token: 'false'  # default: false
    extra-nix-config: |                # appended to nix.conf
      access-tokens = github.com=${{ secrets.GITHUB_TOKEN }}
```

## Action Inputs Reference

| Input | Description | Default |
|---|---|---|
| `project-path` | Path to folder containing `devbox.json` | repo root |
| `enable-cache` | Cache entire Nix store based on `devbox.lock` | `false` |
| `refresh-cli` | Force re-download of Devbox CLI | `false` |
| `devbox-version` | Pin Devbox CLI version (>0.2.2) | `''` (resolves to latest) |
| `sha256-checksum` | Explicit checksum for the devbox binary | |
| `disable-nix-access-token` | Skip configuring Nix access tokens | `false` |
| `skip-nix-installation` | Skip Nix installation entirely | `false` |
| `extra-nix-config` | Extra lines appended to `nix.conf` | |
| `installer-init-system` | Init system to use for the devbox installer | `systemd` |
