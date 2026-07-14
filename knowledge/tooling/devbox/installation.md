---
title: "Devbox — Installation"
status: exploring
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "installation", "nix"]
sources:
  - "https://www.jetify.com/docs/devbox/installing-devbox/"
last_audit_date: 2026-05-24
---

# Installation

## Linux / macOS / WSL2 (recommended)

```bash
curl -fsSL https://get.jetify.com/devbox | bash
```

If Nix is not detected, Devbox installs it automatically (single-user on Linux/WSL2, multi-user on macOS).

## NixOS / Nixpkgs

```bash
nix-env -iA nixos.devbox      # NixOS
nix-env -iA nixpkgs.devbox    # non-NixOS
```

## Nix Flake

```bash
nix profile install github:jetify-com/devbox/latest
nix profile install github:jetify-com/devbox/0.13.2  # specific version
```

## Updating

```bash
devbox version update        # script install
nix-env -u devbox            # Nixpkgs install
```

Pin a specific Devbox version with the environment variable:

```bash
export DEVBOX_USE_VERSION=0.8.0
```
