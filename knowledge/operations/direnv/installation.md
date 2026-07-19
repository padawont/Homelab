---
title: "direnv — Installation"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["direnv", "installation"]
sources:
  - "https://direnv.net/docs/installation.html"
last_audit_date: 2026-05-24
---

# Installation

## Package Managers

```bash
# macOS
brew install direnv

# NixOS / Nixpkgs
nix-env -iA nixos.direnv     # NixOS
nix-env -iA nixpkgs.direnv   # non-NixOS

# Arch
pacman -S direnv

# Debian / Ubuntu
apt install direnv

# Fedora
dnf install direnv
```

## Binary Install

```bash
curl -sfL https://direnv.net/install.sh | bash
```

Binary builds are also available for each [release](https://github.com/direnv/direnv/releases).

## Verify

```bash
direnv version
```
