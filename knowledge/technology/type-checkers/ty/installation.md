---
title: "Installation"
status: draft
author: "Khalid Zubair (refactorartist)"
date: 2026-06-28
tags: [python, type-checker, astral, ty]
sources:
  - url: "https://docs.astral.sh/ty/"
    title: "ty Documentation"
  - url: "https://github.com/astral-sh/ty"
    title: "ty GitHub Repository"
last_audit_date: 2026-06-28
---

# Installation

ty supports multiple installation methods. Choose the one that best fits your workflow.

## pip

Install ty from PyPI using pip:

```bash
pip install ty
```

This installs the latest stable release. Use a virtual environment to avoid conflicts with other packages.

## pipx

For an isolated, system-wide installation suitable for CLI usage:

```bash
pipx install ty
```

pipx installs ty in its own environment and makes the `ty` command available globally without polluting your system Python.

## uv

Astral's own package manager, uv, can install ty directly:

```bash
uv tool install ty
```

Or run ty without installing it permanently using uvx:

```bash
uvx ty check
```

To add ty as a project dependency:

```bash
uv add ty --dev
```

## Standalone Installer

A standalone installer script is provided by Astral for CI and automated environments:

```bash
curl -LsSf https://astral.sh/ty/install.sh | sh
```

This installs a self-contained binary that does not require Python.

## GitHub Releases

Standalone binaries are published for each release on the [GitHub releases page](https://github.com/astral-sh/ty/releases). Download the archive for your platform, extract it, and place the binary on your PATH:

```bash
# Linux x86_64 example
curl -L -o ty.tar.gz https://github.com/astral-sh/ty/releases/latest/download/ty-x86_64-unknown-linux-gnu.tar.gz
tar -xzf ty.tar.gz
chmod +x ty
sudo mv ty /usr/local/bin/
```

## Docker

A Docker image is available via GitHub Container Registry:

```bash
docker pull ghcr.io/astral-sh/ty:latest
```

Run ty inside a container:

```bash
docker run --rm -v $(pwd):/workspace ghcr.io/astral-sh/ty:latest check /workspace
```

## mise

If you use mise for tool version management:

```bash
mise install ty
```

## Version Verification

Confirm the installation succeeded:

```bash
ty version
```
