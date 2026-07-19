---
title: "Devbox — IDE Integration"
status: exploring
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "ide", "vscode", "direnv", "wsl"]
sources:
  - "https://www.jetify.com/docs/devbox/ide-configuration/vscode/"
  - "https://www.jetify.com/docs/devbox/ide-configuration/direnv/"
last_audit_date: 2026-05-24
---

# IDE Integration

## VS Code (Devbox Extension)

1. Install the Devbox extension from the marketplace
2. Open Command Palette → `Devbox: Reopen in Devbox shell environment`
3. VS Code reloads with the Devbox environment in its terminal

The extension auto-runs `devbox shell` in new terminals by default (disable via `"devbox.autoShellOnTerminal": false`).

## VS Code (Direnv Alternative)

1. Install direnv + run `devbox generate direnv`
2. Install the direnv VS Code extension
3. Open the project — direnv prompts to reload the environment

## Manual Shell Setup

Open VS Code terminal and run `devbox shell` manually. For debugger integration, find the binary path via `devbox shell -- 'which java'` and set it in `launch.json`.

## Direnv Integration

```bash
devbox generate direnv
```

This creates an `.envrc` file and runs `direnv allow`. After this, entering the project directory automatically loads the Devbox environment. After changes to `devbox.json`, you must re-run `direnv allow` (or whitelist the directory) for the environment to update.

The generated `.envrc` evaluates `devbox generate direnv --print-envrc`. Add custom env vars:

```bash
devbox generate direnv --env MY_VAR=value --env-file .env.prod
```

Limitations:
- Shell aliases and functions from `init_hook` are not available
- `$PS1` modifications do not work

These work normally with `devbox shell`, `devbox run`, and `devbox services`.

Whitelist a project directory for auto-reload in `~/.config/direnv/direnv.toml`:

```toml
[whitelist]
prefix = [ "/absolute/path/to/project" ]
```

## Windows / WSL

Devbox CLI is not supported on Windows directly. Use WSL:
1. Install Devbox in WSL
2. Navigate to the project and run `devbox shell`
3. Run `code .` to connect VS Code remotely to the WSL environment
