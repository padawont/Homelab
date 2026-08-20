---
title: "Home Manager"
status: accepted
author: "padawont"
date: 2026-08-20
tags: [home-manager, nix, nixos, user-environment]
sources:
  - url: "https://nix-community.github.io/home-manager/"
    title: "Home Manager docs"
last_audit_date: 2026-08-20
related_docs:
  - "./02_Knowledge/technologies/tools/nixos/flakes.md"
  - "./02_Knowledge/technologies/tools/nixos/overview.md"
---

# Home Manager

## Overview

Home Manager declaratively manages a user's environment — dotfiles, user packages, git config, and user-level systemd services — as an alternative to hand-managed dotfiles. In the homelab it defines a consistent operator/admin user across all NixOS hosts, so admin tooling is identical on every node.

## Details

### Integration modes

- **Standalone**: `home-manager` command rebuilds only the user environment. Not tied to NixOS; works on other distros.
- **NixOS module** (used in this homelab): home-manager is imported as a NixOS module, and the user environment is built as part of `nixos-rebuild switch`. One build activates both system and user envs.

### home.nix structure

Example — abstract:

```nix
{ config, pkgs, ... }:
{
  home = {
    username = "admin";
    homeDirectory = "/home/admin";
    stateVersion = "26.05";
  };

  programs = {
    git.enable = true;
    bash.enable = true;
    tmux.enable = true;
  };

  services = {
    ssh-agent.enable = true;  # user-level systemd unit
  };
}
```

### Key option areas

- `home.packages` — packages installed for the user
- `programs.<name>` — managed dotfiles/tool config (git, bash, tmux, neovim, …)
- `xdg.*` — XDG base directory settings
- `services.*` — user-level systemd units (started when the user logs in)
- `home.file.*` / `home.sessionVariables` — explicit file management and env vars

Example — abstract:

```nix
{ config, pkgs, ... }:
{
  systemd.user.services.my-tunnel = {
    Service = {
      ExecStart = "${pkgs.openssh}/bin/ssh -R 8080:localhost:80 node-main";
      Restart = "on-failure";
    };
  };
}
```

### Flakes integration

home-manager ships a NixOS module that takes a config function. In the flake:

Example — abstract:

```nix
home-manager.nixosModules.home-manager
```

combined with the module-level settings `home-manager.useGlobalPkgs = true;` and `home-manager.users.admin = import ./home.nix;`. The user env is then rebuilt by `nixos-rebuild switch`, so no separate `home-manager switch` is needed on hosts.

### Rebuild & rollback

`nixos-rebuild switch` activates system + user envs together. Each NixOS generation references the matching home-manager generation, so rolling back the system restores the user environment via the same boot-menu/`nixos-rebuild --rollback` path.

## Sources / Further Reading

- [Home Manager docs](https://nix-community.github.io/home-manager/)
- See `./02_Knowledge/technologies/tools/nixos/flakes.md` for wiring home-manager as a flake input, and `./02_Knowledge/technologies/tools/nixos/overview.md` for the NixOS rebuild model.
