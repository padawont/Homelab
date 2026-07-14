---
title: "Basic Usage"
status: draft
author: "padawont"
date: 2026-07-14
tags:
  - nixos-anywhere
  - nixos
  - cli
  - installation
sources:
  - url: "https://github.com/nix-community/nixos-anywhere"
    title: "nix-community/nixos-anywhere — README"
  - url: "https://nixos.org/manual/nixos/stable/#sec-installation"
    title: "NixOS Manual — Installation"
last_audit_date: 2026-07-14
---

# Basic Usage

## Minimal command

```console
$ nix run github:nix-community/nixos-anywhere -- --flake .#host root@server.ip
```

This runs nixos-anywhere with:
- `--flake .#host` — use the `nixosConfigurations.host` output from your flake
- `root@server.ip` — SSH target (must have root or sudo access)

## Common flags

| Flag | Description |
|---|---|
| `--flake <flake-uri>` | NixOS configuration to install (e.g. `.#host`) |
| `--disko-mode <mode>` | disko mode: `disko`, `mount`, or `format` (default: `disko`) |
| `--no-reboot` | Stay in the kexec environment after install (useful for debugging) |
| `--extra-files <dir>` | Copy additional files to the target before installation |
| `--target-host <host>` | SSH connection string override for the target |
| `--build-on-remote` | Build the NixOS closure on the target instead of locally |
| `--kexec <url-or-path>` | Use a custom kexec image instead of the default |
| `--stop-after-disko` | Run disko then stop (useful for inspecting partitions) |
| `--debug` | Enable verbose debug output |

### --flake

The flake must contain a `nixosConfigurations.<name>` output with `disko.devices` defined and a bootloader configured:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    disko.url = "github:nix-community/disko";
    disko.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, disko, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      modules = [
        disko.nixosModules.disko
        ./configuration.nix
        ./disko-config.nix
      ];
    };
  };
}
```

### --extra-files

Copy supplementary files to the target before installation:

```console
$ nix run github:nix-community/nixos-anywhere -- \
  --flake .#host \
  --extra-files ./extra-files \
  root@server.ip
```

The `extra-files` directory structure mirrors the target filesystem:

```
extra-files/
├── etc/
│   └── ssh/
│       └── ssh_host_ed25519_key   # pre-generated host key
└── root/
    └── .ssh/
        └── authorized_keys
```

### --kexec

Override the default kexec image for unsupported architectures or custom needs:

```console
# Build and use a custom kexec image
$ nix build --print-out-paths github:nix-community/nixos-images#packages.x86_64-linux.kexec-installer-nixos-unstable-noninteractive
$ nix run github:nix-community/nixos-anywhere -- \
  --flake .#host \
  --kexec ./result/nixos-kexec-installer-noninteractive-x86_64-linux.tar.gz \
  root@server.ip
```

## End-to-end example

**1. Create a flake:**

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    disko.url = "github:nix-community/disko";
    disko.inputs.nixpkgs.follows = "nixpkgs";
    nixos-anywhere.url = "github:nix-community/nixos-anywhere";
  };

  outputs = { self, nixpkgs, disko, ... }: {
    nixosConfigurations.webserver = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        disko.nixosModules.disko
        ({ ... }: {
          disko.devices.disk.main = {
            device = "/dev/sda";
            type = "disk";
            content = {
              type = "gpt";
              partitions = {
                boot = {
                  size = "1G";
                  type = "EF00";
                  content = {
                    type = "filesystem";
                    format = "vfat";
                    mountpoint = "/boot";
                  };
                };
                root = {
                  size = "100%";
                  content = {
                    type = "filesystem";
                    format = "ext4";
                    mountpoint = "/";
                  };
                };
              };
            };
          };
        })
        ({ pkgs, ... }: {
          boot.loader.systemd-boot.enable = true;
          services.openssh.enable = true;
          users.users.root.openssh.authorizedKeys.keys = [
            "ssh-ed25519 AAAAC3... your-public-key"
          ];
          networking.hostName = "webserver";
          system.stateVersion = "24.11";
        })
      ];
    };
  };
}
```

**2. Run nixos-anywhere:**

```console
$ nix run github:nix-community/nixos-anywhere -- \
  --flake .#webserver \
  root@192.168.1.100
```

**3. Wait for completion** (typically 5-15 minutes depending on connection speed). The machine will reboot into a running NixOS system.

## See also

- [disko-integration.md](disko-integration.md) — Additional disk layouts and partitioning options
- [supported-platforms.md](supported-platforms.md) — Platform-specific configuration notes

## SSH key forwarding

If your flake references private repositories, forward your SSH agent:

```console
$ ssh-agent -c
$ ssh-add ~/.ssh/id_ed25519
$ nix run github:nix-community/nixos-anywhere -- \
  --flake .#webserver \
  --extra-files ./extra-files \
  root@server.ip
```
