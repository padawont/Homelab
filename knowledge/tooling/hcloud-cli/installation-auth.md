---
title: "Installation & Authentication"
status: draft
author: "refactorartist"
date: 2026-07-11
tags:
  - hetzner
  - hcloud
  - installation
  - authentication
  - context
sources:
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md"
    title: "Setup hcloud CLI — Tutorial"
    paragraph: "§1.1–1.7, §2.1–2.4, §3"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_context_create.md"
    title: "hcloud context create — Reference"
    paragraph: "§hcloud context create"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_context_list.md"
    title: "hcloud context list — Reference"
    paragraph: "§hcloud context list"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_context_use.md"
    title: "hcloud context use — Reference"
    paragraph: "§hcloud context use"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_context_delete.md"
    title: "hcloud context delete — Reference"
    paragraph: "§hcloud context delete"
  - url: "https://docs.hetzner.com/cloud/api/getting-started/generating-api-token/"
    title: "Generating an API Token — Hetzner Docs"
    paragraph: "Steps 1–6"
  - url: "https://docs.hetzner.com/cloud/api/getting-started/using-api/"
    title: "Using the API — Hetzner Docs"
    paragraph: "Project scoping"
last_audit_date: 2026-07-11
---

# Installation & Authentication

## Installation Methods

### Homebrew (macOS and Linux)

```bash
brew install hcloud
```

Source: [setup-hcloud-cli.md §1.5](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md)

### Direct Download (Linux amd64)

```bash
curl -sSLO https://github.com/hetznercloud/cli/releases/latest/download/hcloud-linux-amd64.tar.gz
sudo tar -C /usr/local/bin --no-same-owner -xzf hcloud-linux-amd64.tar.gz hcloud
rm hcloud-linux-amd64.tar.gz
```

Source: [setup-hcloud-cli.md §1.1](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md)

### .deb Package (Debian/Ubuntu)

```bash
curl -sSLO https://github.com/hetznercloud/cli/releases/latest/download/hcloud-cli_<version>_linux_amd64.deb
sudo dpkg -i hcloud-cli_<version>_linux_amd64.deb
```

Includes man pages and shell completions for bash, zsh, and fish.

Source: [setup-hcloud-cli.md §1.3](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md)

### .rpm Package (Fedora/RHEL/CentOS)

```bash
curl -sSLO https://github.com/hetznercloud/cli/releases/latest/download/hcloud-cli-<version>-1.x86_64.rpm
sudo dnf install hcloud-cli-<version>-1.x86_64.rpm
```

Includes man pages and shell completions.

Source: [setup-hcloud-cli.md §1.4](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md)

### Windows (WinGet or Scoop)

```powershell
winget install HetznerCloud.CLI
scoop install hcloud
```

Note: These package entries are not maintained by Hetzner.

Source: [setup-hcloud-cli.md §1.6](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md)

### Go Install

```bash
go install github.com/hetznercloud/cli/cmd/hcloud@latest
```

Note: Binaries built with Go will not have the correct version embedded.

Source: [setup-hcloud-cli.md §1.2](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md)

### Docker

```bash
# Run one-off commands with token via environment variable
docker run --rm -e HCLOUD_TOKEN="<token>" hetznercloud/cli:latest <command>

# Persist config via volume mount
docker run --rm -v ~/.config/hcloud/cli.toml:/config.toml hetznercloud/cli:latest <command>

# Interactive shell
docker run -it --rm --entrypoint /bin/sh hetznercloud/cli:latest
```

Source: [setup-hcloud-cli.md §1.7](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md)

## Shell Completion

### Bash

```bash
source <(hcloud completion bash)
# Make permanent:
echo 'source <(hcloud completion bash)' >> ~/.bashrc
```

Source: [setup-hcloud-cli.md §2.1](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md)

### Zsh

```bash
mkdir -p ~/.config/hcloud/completion/zsh
hcloud completion zsh > ~/.config/hcloud/completion/zsh/_hcloud
# Add to ~/.zshrc before compinit:
echo 'fpath+=(~/.config/hcloud/completion/zsh)' >> ~/.zshrc
```

Source: [setup-hcloud-cli.md §2.2](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md)

### Fish

```bash
hcloud completion fish | source
# Make permanent:
hcloud completion fish > ~/.config/fish/completions/hcloud.fish
```

Source: [setup-hcloud-cli.md §2.3](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md)

### PowerShell

```powershell
hcloud completion powershell | Out-String | Invoke-Expression
# Generate script for permanent loading:
hcloud completion powershell > hcloud.ps1
```

Source: [setup-hcloud-cli.md §2.4](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md)

## Authentication

### API Token Creation

1. Open [Hetzner Console](https://console.hetzner.com/)
2. Navigate to your Project → **Security** → **API Tokens**
3. Click **Generate API Token**
4. Enter a description (e.g., "hcloud CLI - production")
5. Choose permission level:
   - **Read** — GET requests only
   - **Read & Write** — Full CRUD access (required for provisioning)
6. Copy the token immediately — it is shown **only once**

Source: [Generating an API Token](https://docs.hetzner.com/cloud/api/getting-started/generating-api-token/)

**Important:** Each API token is bound to a single project. Create separate tokens for separate projects. Source: [Using the API](https://docs.hetzner.com/cloud/api/getting-started/using-api/)

### Context Management

The hcloud CLI uses **contexts** to manage multiple Hetzner Cloud tokens and configuration preferences. Context configuration is stored in `~/.config/hcloud/cli.toml`.

```bash
# Create a new context (interactively prompted for token)
hcloud context create <context-name>

# Create a context using HCLOUD_TOKEN environment variable (non-interactive)
export HCLOUD_TOKEN="<token>"
hcloud context create --token-from-env <context-name>

# Switch to a context
hcloud context use <context-name>

# List all contexts (active context marked with *)
hcloud context list

# Show currently active context
hcloud context active

# Rename a context
hcloud context rename <old-name> <new-name>

# Delete a context
hcloud context delete <context-name>

# Unset/clear the current context
hcloud context unset
```

Source: [setup-hcloud-cli.md §3](https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md), [context reference](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_context_create.md)

### Multi-Project Setup

For teams managing multiple Hetzner Cloud projects, create one context per project:

```bash
hcloud context create production
hcloud context create staging
hcloud context create development

# Switch context depending on the task
hcloud context use production
hcloud server list  # Lists servers in the production project

hcloud context use staging
hcloud server list  # Lists servers in the staging project
```

### Environment Variable Authentication

Set `HCLOUD_TOKEN` to bypass context configuration — useful for CI/CD and Docker:

```bash
export HCLOUD_TOKEN="<token>"
hcloud server list
```

### Global Configuration Flags

These flags apply to any `hcloud` command:

| Flag | Purpose |
|---|---|
| `--config string` | Config file path (default: `~/.config/hcloud/cli.toml`) |
| `--context string` | Override the active context for a single command |
| `--endpoint string` | API endpoint override (default: `https://api.hetzner.cloud/v1`) |
| `--poll-interval duration` | Polling interval for async operations (default 500ms) |
| `--quiet` | Only print error messages |
| `--debug` | Enable debug output |

Source: [hcloud CLI manual](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud.md)
