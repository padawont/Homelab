---
title: "Devbox — Troubleshooting & Uninstall"
status: exploring
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "troubleshooting", "faq", "uninstall"]
sources:
  - "https://www.jetify.com/docs/devbox/faq/"
last_audit_date: 2026-05-24
---

# Troubleshooting & Uninstall

| Issue | Solution |
|---|---|
| Package install is slow | Missing prebuilt binary — use Jetify Cache or Jetify Prebuilt Cache |
| `GLIBC_X.XX not found` | Update packages or use `devbox add <pkg>@<ver> --patch always` |
| Missing `libstdc++` | `devbox add stdenv.cc.cc.lib` |
| Prompt is modified inside shell | `DEVBOX_NO_PROMPT=true` |
| Clean up Nix store | `devbox run -- nix store gc --extra-experimental-features nix-command` |
| Package missing headers | `devbox add prometheus --outputs=out,cli` |
| Use custom Nix packages | Use flake references in `devbox.json` |
| Fish shell support | Works out of the box |

## CI/CD Issues

For CI/CD-specific issues (caching, Nix build timeouts, permission errors), see the dedicated [devbox-ci](/knowledge/operations/ci-cd/devbox-ci/) knowledge note.

## Uninstall

```bash
rm /usr/local/bin/devbox
rm -rf ~/.cache/devbox ~/.local/share/devbox
```

To uninstall Nix itself, follow the [Nix manual](https://nixos.org/manual/nix/stable/installation/uninstall).
