---
title: "Devbox — Plugins"
status: exploring
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "plugins", "nix"]
sources:
  - "https://www.jetify.com/docs/devbox/guides/plugins/"
last_audit_date: 2026-05-24
---

# Plugins

Plugins provide default configuration (env vars, services, helper files) for Nix packages. Built-in plugins auto-activate when you add supported packages.

## Viewing Plugin Details

```bash
devbox info nginx
```

## Built-in Plugins

Auto-activated when you `devbox add` these packages: Apache, Caddy, Nginx, Node.js, MariaDB, MySQL, PostgreSQL, Redis, Valkey, PHP, Python, Ruby, Elixir.

## Local Plugins

```json
{
  "include": [
    "path:./path/to/plugin.json"
  ]
}
```

## GitHub Hosted Plugins

```json
{
  "include": [
    "github:org/repo/ref?dir=<path-to-plugin>",
    "github:org/repo/tags/v1.0?dir=<plugin-dir>"
  ]
}
```

Devbox caches GitHub plugins for 24 hours. Bypass with `export DEVBOX_X_GITHUB_PLUGIN_CACHE_TTL=<time>`.

## Helper Files

Helper files (e.g. `nginx.conf`) are placed in `devbox.d/` and should be checked into source control. Devbox creates them if they don't exist and never overwrites existing ones.

## Plugin Source Code

https://github.com/jetify-com/devbox/tree/main/plugins
