---
title: "Devbox — Configuration (devbox.json)"
status: exploring
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "configuration", "devbox-json"]
sources:
  - "https://www.jetify.com/docs/devbox/configuration/"
  - "https://www.jetify.com/docs/devbox/guides/pinning-packages/"
  - "https://www.jetify.com/docs/devbox/guides/scripts/"
  - "https://www.jetify.com/docs/devbox/guides/plugins/"
last_audit_date: 2026-05-24
---

# Configuration (devbox.json)

The `devbox.json` file lives in the project root and supports these top-level fields:

```json
{
  "packages": ["go@latest", "golangci-lint@latest"],
  "env": {
    "PROJECT_DIR": "$PWD"
  },
  "env_from": "path/to/.env",
  "shell": {
    "init_hook": [
      "echo 'Welcome!'"
    ],
    "scripts": {
      "test": "go test ./..."
    }
  },
  "include": ["plugin:nginx"]
}
```

## Packages

List or map of Nix packages. Simple form:

```json
{
  "packages": ["go@1.19", "python@3.10"]
}
```

Advanced form with platform constraints and plugin control:

```json
{
  "packages": {
    "go": "latest",
    "glibcLocales": {
      "version": "latest",
      "platforms": ["x86_64-linux", "aarch64-linux"],
      "disable_plugin": true
    }
  }
}
```

Valid platforms: `aarch64-darwin`, `aarch64-linux`, `x86_64-darwin`, `x86_64-linux`. `i686-linux` and `armv7l-linux` are also supported (built from source).

## Version Pinning

```bash
devbox search nodejs             # list available versions
devbox add nodejs@20.1.0         # pin exact version
devbox add nodejs@20             # pin semver range (latest minor/patch >=20)
devbox update                    # refresh to latest within range
```

The `devbox.lock` file records exact Nix commit hashes for reproducibility.

## Env

```json
{
  "env": {
    "DATABASE_URL": "postgres://localhost:5432/myapp"
  }
}
```

Supports string literals, `$PWD`, and `$PATH`. Load from a `.env` file via `"env_from": "path/to/.env"`.

## Init Hook

Runs shell commands before the shell finishes setup, after `~/.rc` scripts:

```json
{
  "shell": {
    "init_hook": [
      "export PS1='devbox> '",
      ". ./scripts/setup-env.sh"
    ]
  }
}
```

## Scripts

Named commands runnable via `devbox run <name>`:

```json
{
  "shell": {
    "scripts": {
      "build": "cargo build",
      "lint": ["cargo clippy", "cargo fmt --check"]
    }
  }
}
```

Run one-off commands without defining a script:

```bash
devbox run echo "Hello World"
devbox run -q lsof -i :80
```

Pass custom env vars:

```bash
devbox run --env MY_VAR=value --env-file .env.devbox echo $MY_VAR
```

## Include (Plugins)

Explicitly load plugin configurations:

```json
{
  "include": [
    "plugin:nginx",
    "path:./path/to/plugin.json",
    "github:org/repo/ref?dir=<path-to-plugin>",
    "github:org/repo/tags/v1.0?dir=<plugin-dir>"
  ]
}
```

Built-in plugins auto-activate when you `devbox add` these packages: Apache, Caddy, Nginx, Node.js, MariaDB, MySQL, PostgreSQL, Redis, Valkey, PHP, Python, Ruby, Elixir.
