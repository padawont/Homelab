---
title: "Rollback Mechanisms"
status: draft
author: "padawont"
date: 2026-07-14
tags:
  - nixos
  - rollback
  - generations
  - garbage-collection
sources:
  - url: "https://nixos.org/manual/nixos/stable/#sec-changing-config"
    title: "NixOS Manual — Changing the Configuration"
  - url: "https://nixos.org/manual/nix/stable/"
    title: "Nix Reference Manual — Garbage Collection"
  - url: "https://nixos.org/manual/nixos/stable/#sec-nix-gc"
    title: "NixOS Manual — Cleaning the Nix Store"
last_audit_date: 2026-07-14
---

# Rollback Mechanisms

NixOS's generation-based model makes rollbacks a first-class feature. Every configuration change creates a new generation, and old generations remain bootable until explicitly removed.

## Boot generations

Each successful `nixos-rebuild switch` produces a new generation — a complete system closure stored in the Nix profile at `/nix/var/nix/profiles/system`:

```
/nix/var/nix/profiles/system-1-link  →  /nix/store/abc...1-system
/nix/var/nix/profiles/system-2-link  →  /nix/store/abc...2-system
/nix/var/nix/profiles/system-3-link  →  /nix/store/abc...3-system
```

Generations appear as boot menu entries in systemd-boot or GRUB.

```console
# List all generations
$ nix-env --list-generations -p /nix/var/nix/profiles/system
   1   2024-01-15 10:00:23
   2   2024-03-20 14:30:45
   3   2024-06-10 09:15:12   (current)
```

To boot an older generation, select it from the boot menu at startup. The system will run exactly as it did when that generation was created.

## nixos-rebuild switch --rollback

The `--rollback` flag reverts to the previous generation without rebooting:

```console
# Revert to the previous generation
$ sudo nixos-rebuild switch --rollback

# Revert to a specific generation
$ sudo nixos-rebuild switch --rollback 2

# Test the rollback without adding to boot menu
$ sudo nixos-rebuild test --rollback
```

This is useful when a configuration change breaks a running service and you need to restore functionality immediately. The rollback:
1. Activates the previous generation's system closure
2. Restarts/reloads services to match the previous configuration
3. Adds the rolled-back state as a new generation in the boot menu

## Specialisations

Specialisations allow boot menu entries with different configuration variants sharing the same base:

```nix
{ config, pkgs, ... }: {
  specialisation = {
    no-gui.configuration = {
      systemd.services.display-manager.enable = lib.mkForce false;
      services.xserver.enable = lib.mkForce false;
    };
    debug.configuration = {
      services.openssh.logLevel = "DEBUG";
    };
  };
}
```

Each specialisation appears as a separate boot menu entry under the same generation.

## Garbage collection

Unused packages and old generations must be explicitly removed. Nix never automatically deletes store paths that might be needed.

### nix-collect-garbage

The primary garbage collection command:

```console
# Delete all paths not reachable from any profile or GC root
$ sudo nix-collect-garbage

# Delete old generations and then garbage collect
$ sudo nix-collect-garbage --delete-old

# Keep only the last N generations
$ sudo nix-collect-garbage --delete-older-than 30d

# Dry run: show what would be deleted
$ sudo nix-collect-garbage --dry-run
```

### nix-env --delete-generations

Remove specific generations from the system profile:

```console
# Delete generations older than 7 days
$ sudo nix-env --delete-generations -p /nix/var/nix/profiles/system 7d

# Delete all but the N most recent
$ sudo nix-env --delete-generations -p /nix/var/nix/profiles/system +5

# Delete specific generation numbers
$ sudo nix-env --delete-generations -p /nix/var/nix/profiles/system 1 2 3
```

### Automatic GC

Configure periodic garbage collection in `configuration.nix`:

```nix
{ config, pkgs, ... }: {
  nix.gc = {
    automatic = true;
    dates = "weekly";
    options = "--delete-older-than 30d";
  };
}
```

### Bootloader generation limits

Control how many generations appear in the boot menu:

```nix
{ config, pkgs, ... }: {
  boot.loader.systemd-boot.configurationLimit = 10;
  # or for GRUB:
  boot.loader.grub.configurationLimit = 10;
}
```

This only limits boot menu entries — the full generations remain in the store until garbage collected.

## Rollback safety

Nix's garbage collector never deletes store paths referenced by:
- Any generation in the system profile
- Any currently running process (via `/proc` scanning)
- Explicit GC roots (e.g., `nix-store --add-root`)

This means:
- A generation selected in the boot menu is always safe from GC
- Running services pin their dependencies
- Rollback is always possible as long as the target generation exists

To check what's protecting a path from GC:

```console
$ nix-store --query --roots /nix/store/abc...-some-package
```

## Comparing generations

See what changed between generations:

```console
# Show the difference between current and previous generation
$ nix store diff-closures /nix/var/nix/profiles/system-2-link /nix/var/nix/profiles/system-3-link

# Human-readable comparison
$ nix-env --compare-versions -p /nix/var/nix/profiles/system
```

## Key commands reference

```console
# Boot into previous generation (interactive)
# Restart, select previous generation in boot menu

# Rollback without reboot
sudo nixos-rebuild switch --rollback

# List all generations
nix-env --list-generations -p /nix/var/nix/profiles/system

# Delete old generations and free space
sudo nix-collect-garbage --delete-old

# Auto-GC config in configuration.nix
nix.gc.automatic = true;
nix.gc.dates = "weekly";
nix.gc.options = "--delete-older-than 30d";

# Limit boot menu entries
boot.loader.systemd-boot.configurationLimit = 10;

# Compare generations
nix store diff-closures /nix/var/nix/profiles/system-*-link
```
