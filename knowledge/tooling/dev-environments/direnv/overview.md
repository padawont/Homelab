---
title: "direnv"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["direnv", "environment-management", "developer-experience", "shell"]
sources:
  - "https://direnv.net/"
  - "https://direnv.net/man/direnv.1.html"
last_audit_date: 2026-05-24
---

# direnv

direnv is an environment variable manager for your shell. Before each prompt, it checks for a `.envrc` file in the current or parent directories. If found and authorized, it loads the exported variables into the current shell — and unloads them when you `cd` out.

## How It Works

direnv does not source `.envrc` into the current shell. Instead, it creates a bash sub-process to load the file, captures the environment diff, and applies only the changes (exports and unset variables) to the current shell. This means aliases and shell functions defined in `.envrc` are **not** available.

## Detailed Guides

| File | Description |
|---|---|
| [installation.md](./installation.md) | Package manager and binary install methods |
| [shell-hooks.md](./shell-hooks.md) | Hook setup for Bash, Zsh, Fish, and other shells |
| [envrc-reference.md](./envrc-reference.md) | `.envrc` format, quick demo, security model |
| [stdlib.md](./stdlib.md) | Stdlib functions — PATH, loading, layouts, utilities |
| [cli-reference.md](./cli-reference.md) | Full CLI commands reference |
| [configuration.md](./configuration.md) | Whitelisting and `direnv.toml` |
| [devbox-integration.md](./devbox-integration.md) | Using direnv with Devbox |
| [troubleshooting.md](./troubleshooting.md) | FAQ and common issues |
