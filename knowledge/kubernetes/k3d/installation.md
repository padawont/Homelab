---
title: "k3d Installation"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k3d
  - installation
  - kubernetes
  - docker
sources:
  - url: "https://k3d.io/v5.6.0/#installation"
    title: "k3d — Installation"
  - url: "https://github.com/k3d-io/k3d#readme"
    title: "k3d GitHub README"
  - url: "https://formulae.brew.sh/formula/k3d"
    title: "Homebrew formula for k3d"
  - url: "https://chocolatey.org/packages/k3d"
    title: "Chocolatey package for k3d"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_version/"
    title: "k3d version command"
last_audit_date: 2026-07-10
---

# k3d Installation

Install [k3d](https://k3d.io/) — a tool for running k3s Kubernetes clusters in Docker containers. k3d is a community-driven project (not an official Rancher/SUSE product).

## Prerequisites

- **Docker** >= v20.10.5 (runc >= v1.0.0-rc93 is required for k3d v5.x)
- **kubectl** — for interacting with the cluster after creation

## macOS / Linux

### Homebrew

```bash
brew install k3d
```

Formula is maintained in [homebrew/homebrew-core](https://github.com/Homebrew/homebrew-core/blob/master/Formula/k3d.rb) and mirrored to [homebrew/linuxbrew-core](https://github.com/Homebrew/linuxbrew-core/blob/master/Formula/k3d.rb).

### Install Script (curl / wget)

Install the latest release:

```bash
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
```

```bash
wget -q -O - https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
```

Install a specific version using the `TAG` environment variable:

```bash
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | TAG=v5.6.0 bash
```

### MacPorts

```bash
sudo port selfupdate && sudo port install k3d
```

### AUR (Arch Linux)

```bash
yay -S rancher-k3d-bin
```

### asdf

```bash
asdf plugin-add k3d
asdf install k3d latest
```

Managed by [spencergilbert/asdf-k3d](https://github.com/spencergilbert/asdf-k3d).

## Windows

### Chocolatey

```bash
choco install k3d
```

Package maintained at [erwinkersten/chocolatey-packages](https://github.com/erwinkersten/chocolatey-packages/tree/master/automatic/k3d).

### Scoop

```bash
scoop install k3d
```

Package maintained at [ScoopInstaller/Main](https://github.com/ScoopInstaller/Main/blob/master/bucket/k3d.json).

## Other Methods

### GitHub Release Binary

Download a pre-built binary from the [GitHub Releases page](https://github.com/k3d-io/k3d/releases) and place it in your `PATH`.

### Go Install

```bash
go install github.com/k3d-io/k3d/v5@latest
```

This gives you unreleased/bleeding-edge changes.

### Docker Image

```bash
docker run --rm k3d-io/k3d --help
```

## Verify Installation

```bash
k3d version
```

Verify that Docker and kubectl are available with `docker --version` and `kubectl version --client`.
