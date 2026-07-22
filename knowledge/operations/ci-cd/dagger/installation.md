---
title: "Dagger — Installation"
status: draft
author: "padawont"
date: 2026-07-22
tags: ["dagger", "installation", "devbox", "cli"]
sources:
  - url: "https://docs.dagger.io/getting-started/installation"
    title: "Dagger Installation Guide"
  - url: "https://github.com/dagger/nix"
    title: "Dagger Nix Flake"
  - url: "https://www.nixhub.io/packages/dagger"
    title: "Dagger on NixHub"
last_audit_date: 2026-07-22
related_configs:
  - devbox.json
  - configs-and-adr/node-main/kubernetes/dagger-engine.yaml
---

# Dagger Installation

## Prerequisites

- **Container runtime** — Docker, Podman, or nerdctl installed and running
- **DevBox** — this repo uses devbox for reproducible tooling

## Install via DevBox (Recommended)

```bash
devbox add dagger@latest
```

**Note:** The Dagger version in nixpkgs may be outdated. If `devbox add dagger` provides an old version, install the CLI directly via the official script (see below) and add the script path to devbox instead.

## Install via Official Script

```bash
curl -fsSL https://dl.dagger.io/dagger/install.sh | BIN_DIR=$HOME/.local/bin sh
```

For a system-wide install:

```bash
curl -fsSL https://dl.dagger.io/dagger/install.sh | BIN_DIR=/usr/local/bin sudo -E sh
```

## Verify Installation

```bash
dagger version
```

Expected output format:
```
dagger v0.21.4 (registry.dagger.io/engine:v0.21.4) linux/amd64
```

## Engine Auto-Provisioning

The Dagger Engine is automatically provisioned on the first `dagger run` or `dagger call` command. It runs as a Docker container (`registry.dagger.io/engine`) and auto-stops after 5 minutes of idle time.

Start the engine:

```bash
dagger run echo "engine started"
```

The engine container is visible via:

```bash
docker ps --filter='name=^dagger-engine-'
```

## Remove Dagger

```bash
# DevBox
devbox remove dagger

# CLI binary
sudo rm /usr/local/bin/dagger

# Engine container + volumes
docker rm --force --volumes "$(docker ps --quiet --filter='name=^dagger-engine-')"
rm -rf ~/.cache/dagger ~/.config/dagger
```

## Persistent Engine (Optional)

For production use, deploy the Dagger Engine as a DaemonSet on node-1. See `configs-and-adr/node-main/kubernetes/dagger-engine.yaml`.
