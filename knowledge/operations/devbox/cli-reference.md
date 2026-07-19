---
title: "Devbox — CLI Reference"
status: exploring
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "cli", "reference"]
sources:
  - "https://www.jetify.com/docs/devbox/cli-reference/devbox/"
last_audit_date: 2026-05-24
---

# CLI Reference

| Command | Description |
|---|---|
| `devbox init [<dir>]` | Create a new `devbox.json` in the current or specified directory |
| `devbox add <pkg>[@<ver>]...` | Add one or more packages to the project |
| `devbox rm <pkg>...` | Remove one or more packages |
| `devbox shell` | Enter an isolated shell with the project's packages |
| `devbox run <script \| command>` | Run a script or arbitrary command in the Devbox environment |
| `devbox install` | Start a shell, install all packages, and exit |
| `devbox services up [service]...` | Start services with process-compose (use -b for background) |
| `devbox services start [service]...` | Start one or more services (starts all if omitted) |
| `devbox services stop [service]...` | Stop one or more services (stops all and shuts down process-compose if omitted) |
| `devbox services ls` | List available services |
| `devbox services restart [service]...` | Restart one or more services (restarts all and process-compose if omitted) |
| `devbox services attach` | Attach process-compose TUI to background services |
| `devbox generate direnv` | Generate `.envrc` for direnv integration |
| `devbox search <pkg>` | Search for available package versions |
| `devbox update` | Refresh packages to latest within version constraints |
| `devbox info <pkg>` | Display package information including plugins |
| `devbox global add <pkg>` | Install a package globally (available across all projects) |
| `devbox global list` | List globally installed packages |
| `devbox global rm <pkg>` | Remove a global package |
| `devbox global pull` | Pull global config from a file or URL |
| `devbox global shellenv` | Source global packages in your host shell |
| `devbox version update` | Update Devbox itself |
| `devbox generate dockerfile` | Generate a Dockerfile from your devbox.json |
| `devbox generate devcontainer` | Generate Dockerfile and devcontainer.json for VS Code Dev Containers |
| `devbox generate readme` | Generate a markdown README for the project |
