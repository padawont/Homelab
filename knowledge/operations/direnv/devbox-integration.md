---
title: "direnv — Devbox Integration"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["direnv", "devbox", "integration"]
sources:
  - "https://www.jetify.com/docs/devbox/ide-configuration/direnv/"
last_audit_date: 2026-05-24
---

# Devbox Integration

direnv is the recommended way to automatically activate Devbox environments on directory entry.

## Setup

```bash
# Prerequisite: direnv installed and hooked to your shell
devbox generate direnv
```

This creates an `.envrc` file and runs `direnv allow`. After this, every time you `cd` into the project directory, direnv automatically loads the Devbox environment defined in `devbox.json`.

## Custom Env Variables

```bash
devbox generate direnv --env MY_VAR=value --env-file .env.devbox
```

The generated `.envrc` contains:

```bash
eval "$(devbox generate direnv --print-envrc --env MY_VAR=value --env-file .env.devbox)"
```

## Auto-Reload

After changes to `devbox.json`, run `direnv allow` to reload. Alternatively, whitelist the project directory in `direnv.toml` for automatic updates.

## Limitations with Devbox

- Shell aliases and functions defined in `init_hook` are **not** loaded by direnv. Use Devbox Scripts instead.
- `$PS1` modifications in `init_hook` do **not** work with direnv.
- These limitations do **not** apply when using `devbox shell`, `devbox run`, or `devbox services`.

## VS Code with Direnv

1. Run `direnv allow` in the terminal
2. Launch VS Code from the same terminal: `code .`
3. VS Code inherits the direnv environment

Or install the [direnv VS Code extension](https://marketplace.visualstudio.com/items?itemName=mkhl.direnv).
