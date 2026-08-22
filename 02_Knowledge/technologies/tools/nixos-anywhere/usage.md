---
title: "NixOS Anywhere usage"
status: accepted
author: "padawont"
date: 2026-08-22
tags: [nixos, nixos-anywhere, provisioning, disko, cli]
sources:
  - url: "https://nix-community.github.io/nixos-anywhere/quickstart.html"
    title: "nixos-anywhere quickstart guide"
  - url: "https://github.com/nix-community/disko"
    title: "disko"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/tools/nixos-anywhere/overview.md"
  - "./02_Knowledge/technologies/tools/nixos-anywhere/install-methods.md"
  - "./02_Knowledge/technologies/tools/nixos/flakes.md"
---

# NixOS Anywhere usage

## Overview

nixos-anywhere does not need to be installed. Run it with `nix run github:nix-community/nixos-anywhere -- <flags>`. It takes a flake reference to a NixOS configuration plus a disko disk layout, and installs that configuration on a target host over SSH.

## Details

### Setup

1. **Enable flakes** — verify with `nix flake` (see `./02_Knowledge/technologies/tools/nixos/flakes.md`)
2. **Prepare the flake** — a flake exposing `nixosConfigurations.<name>` and importing the disko NixOS module. Copy the upstream [nixos-anywhere-examples flake](https://github.com/nix-community/nixos-anywhere-examples/blob/main/flake.nix) or adapt an existing flake:

Example — abstract:

```nix
{
  inputs.disko.url = "github:nix-community/disko";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs, disko, ... }: {
    nixosConfigurations.generic = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        disko.nixosModules.disko
        ./configuration.nix
        ./hardware-configuration.nix
      ];
    };
  };
}
```

3. **Add a disko disk layout** — a `disk-config.nix` declaring partitioning/formatting. Identify the target disk with `lsblk` (e.g. `/dev/nvme0n1`) and adjust the device in the config. See the [disko examples](https://github.com/nix-community/disko/tree/master/example) for layouts.
4. **Lock the flake** — `nix flake lock` pins inputs and writes `flake.lock`
5. **Inject an SSH key** — replace the placeholder in `configuration.nix` (e.g. in `users.users.root.openssh.authorizedKeys.keys`) with your public key, or it will be impossible to log in after install. Generate from a `.pem` with `ssh-keygen -y -f /path/to/key.pem`

### Running the install

Example — real command:

```bash
nix run github:nix-community/nixos-anywhere -- \
  --flake /home/mydir/test#hetzner-cloud \
  --target-host root@37.27.18.135
```

With hardware-config generation:

```bash
nix run github:nix-community/nixos-anywhere -- \
  --generate-hardware-config nixos-generate-config ./hardware-configuration.nix \
  --flake /path/to/config#name \
  --target-host root@<ip>
```

### Key flags

| Flag | Purpose |
|---|---|
| `--flake <path>#<name>` | Flake reference to the target `nixosConfigurations.<name>` |
| `--target-host <user>@<host>` | SSH destination for the install |
| `--generate-hardware-config <tool> <out>` | Generate hardware config during install: `nixos-generate-config` writes `hardware-configuration.nix`, `nixos-facter` writes `facter.json` — see `./02_Knowledge/technologies/tools/nixos-anywhere/install-methods.md` |
| `--vm-test` | Test the flake + disko config in a VM before touching real hardware |
| `--env-password` | Take the SSH password from the `SSHPASS` environment variable (avoids prompts) |
| `-i <identity_file>` | Use this SSH key for the install instead of creating a temporary one |
| `--kexec <path-or-url>` | Custom kexec image (VPN-capable installer, non-standard architectures) |
| `--kexec-extra-flags <flags>` | Extra flags passed into the kexec call (e.g. `--no-sync`) |

### Gotchas

- **Host key changes** — the target is a new machine after install, so SSH will warn about a changed host key. Remove the old entry with `ssh-keygen -R <ip>`.
- **Temporary SSH key** — unless `-i` is given, nixos-anywhere creates a temporary key for the install session.
- **Passwords** — for a non-root user you need password-less sudo; set `SSHPASS` + `--env-password` to avoid prompts.

### After the install

nixos-anywhere's job ends when NixOS is installed. Ongoing changes go through the flake:

- Locally: `nixos-rebuild switch --flake <url>` (e.g. `.#` for the current dir)
- Remotely: `nixos-rebuild switch --flake <url> --target-host "root@<ip>"` (needs `services.openssh.enable` and the root authorized key)
- Or a deployment tool: deploy-rs (selected in `./03_Research/nixos-adoption/overview.md`), colmena, nixinate

## Sources / Further Reading

- [nixos-anywhere quickstart](https://nix-community.github.io/nixos-anywhere/quickstart.html)
- [disko](https://github.com/nix-community/disko)
- See `./02_Knowledge/technologies/tools/nixos-anywhere/overview.md` for the concept and `./02_Knowledge/technologies/tools/nixos-anywhere/install-methods.md` for boot modes and hardware-config generation.
