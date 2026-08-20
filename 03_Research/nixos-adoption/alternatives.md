---
title: "NixOS adoption research — alternatives index"
status: draft
author: "padawont"
date: 2026-08-20
tags: [nixos, deployment, alternatives, k8s]
sources:
  - knowledge: "./02_Knowledge/technologies/tools/nixos/flakes.md"
references:
  - url: "https://github.com/serokell/deploy-rs"
    title: "deploy-rs"
  - url: "https://colmena.cli.rs/"
    title: "colmena manual"
  - url: "https://nixops.dev/"
    title: "NixOps"
  - url: "https://nixos.org/manual/nixos/stable/"
    title: "NixOS manual"
last_audit_date: 2026-08-20
---

# Alternatives index — NixOS adoption

| Technology | File | Verdict |
|---|---|---|
| deploy-rs | ./alternative-deploy-rs.md | Selected |
| colmena | ./alternative-colmena.md | Rejected — no automatic rollback, slow release cadence |
| NixOps | ./alternative-nixops.md | Rejected — 2.x abandoned & not flake-native; NixOps4 unreleased |
| nixos-rebuild | ./alternative-nixos-rebuild.md | Rejected — manual multi-node only (baseline fallback) |

This index covers the deployment-tool alternatives only. The secrets-manager sub-decision (sops-nix selected) is covered in ./overview.md.
