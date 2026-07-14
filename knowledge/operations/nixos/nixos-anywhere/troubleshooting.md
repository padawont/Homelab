---
title: "Troubleshooting"
status: draft
author: "padawont"
date: 2026-07-14
tags:
  - nixos-anywhere
  - troubleshooting
  - ssh
  - kexec
sources:
  - url: "https://github.com/nix-community/nixos-anywhere/issues"
    title: "nix-community/nixos-anywhere — Issues"
  - url: "https://github.com/nix-community/nixos-anywhere"
    title: "nix-community/nixos-anywhere — README"
last_audit_date: 2026-07-14
---

# Troubleshooting

## SSH connectivity

| Symptom | Likely cause | Solution |
|---|---|---|
| `ssh: connect to host <host> port 22: Connection timed out` | Firewall blocking port 22, or host unreachable | Check network connectivity, firewall rules, and that SSH is running on the target |
| `Permission denied (publickey)` | No SSH key accepted by the target | Add your public key to the target's `~/.ssh/authorized_keys` or use `ssh-copy-id` before running nixos-anywhere |
| `Host key verification failed` | Target host key changed or unknown | Run `ssh-keyscan <host>` to accept the host key first, or use `--ssh-option StrictHostKeyChecking=no` |
| Connection closes immediately after kexec | kexec image doesn't include SSH daemon or network config | Use `--debug` to inspect the kexec boot; try a custom kexec image |
| SSH agent forwarding not working | SSH agent not running or keys not added | Run `ssh-agent -c` then `ssh-add` before nixos-anywhere |

## kexec failures

| Symptom | Likely cause | Solution |
|---|---|---|
| `kexec: Cannot load memory` | Insufficient RAM | Target needs at least 1 GB RAM (excluding swap) |
| System hangs after kexec | Incompatible kernel or hardware | Check if kexec works manually: `sudo kexec -l /path/to/bzImage --initrd=/path/to/initrd --reuse-cmdline && sudo kexec -e` |
| `kexec: Exec format error` | Wrong architecture | Ensure the kexec image matches the target architecture (x86_64 vs aarch64) |
| Network unavailable after kexec | kexec image doesn't have network drivers | Use `--kexec` with a custom image that includes the required kernel modules |
| Black screen / no console output after kexec | Console not configured in kexec image | Add `console=tty0 console=ttyS0,115200` to kernel cmdline in the custom kexec |

## Disk and disko issues

| Symptom | Likely cause | Solution |
|---|---|---|
| `disko: device /dev/sda not found` | Wrong disk device name | Run `lsblk` on the target to find the correct device name |
| `disko: partition table does not match` | Disk already has a different partition layout | Use `--mode destroy,format,mount` to wipe first |
| `disko: mountpoint / already in use` | Filesystem already mounted | Unmount target filesystems: `sudo umount -R /mnt` |
| Installation fails with "not enough space" | Disk too small for the configuration | Increase disk size or reduce the NixOS closure size |
| LUKS passphrase prompt during install | LUKS keyfile not configured | Add `boot.initrd.luks.devices.<name>.keyFile` to your configuration |

> For detailed disk layout examples and configurations, see [disko-integration.md](disko-integration.md).

## Build and evaluation failures

| Symptom | Likely cause | Solution |
|---|---|---|
| `error: undefined variable 'disko'` | disko module not imported in flake | Add `disko.nixosModules.disko` to the modules list |
| `error: flake 'path:/...' does not provide attribute 'nixosConfigurations.<host>'` | Wrong host name in `--flake .#host` | Run `nix eval .#nixosConfigurations --apply builtins.attrNames` to list available hosts |
| `error: cannot connect to cache.nixos.org` | No internet on the build machine | Ensure the source machine has internet access; use `--build-on-remote` if the target has a better connection |
| Build takes very long | Large closure or slow internet | Use a binary cache (`nix.settings.substituters`); pre-build the closure with `nix build .#nixosConfigurations.<host>.config.system.build.toplevel` |
| `error: unfree packages not allowed` | Configuration uses unfree software | Add `nixpkgs.config.allowUnfree = true` to your configuration |

> Full platform context and configurations: [supported-platforms.md](supported-platforms.md)

## Platform-specific

### Hetzner

| Issue | Solution |
|---|---|
| Rescue mode SSH key mismatch | Add your SSH key to Hetzner's Robot SSH key management, then boot into rescue mode |
| Installimage interferes | nixos-anywhere replaces the entire disk; make sure you're not dual-booting with another OS |
| `boot.loader.grub.device` not set | For Hetzner AX series, set `boot.loader.grub.device = "/dev/sda"` |
| Network interface naming | Hetzner uses predictable names (enpXsY); configure in `networking.interfaces` |

### DigitalOcean

| Issue | Solution |
|---|---|
| No console access | DigitalOcean droplets don't have physical console; use `--debug` and check SSH output |
| Cloud-init overwrites config | Ensure your NixOS config disables cloud-init: `services.cloud-init.enable = false` |
| Droplet has no swap | Add a disko swap partition or configure `swapDevices` in your NixOS config |
| Droplet resets after kexec | Some DO droplet types don't support kexec; use a custom installer image |

## Debugging commands

```console
# Run with verbose output
$ nix run github:nix-community/nixos-anywhere -- --debug --flake .#host root@server.ip

# Stop after disko (inspect partitions)
$ nix run github:nix-community/nixos-anywhere -- --stop-after-disko --flake .#host root@server.ip

# Stay in kexec (don't reboot)
$ nix run github:nix-community/nixos-anywhere -- --no-reboot --flake .#host root@server.ip

# Manually check kexec works on the target
$ ssh root@server.ip "command -v kexec && echo 'kexec binary found'"

# List available flake configurations
$ nix eval .#nixosConfigurations --apply builtins.attrNames
```

## Getting help

If the issue persists:

- Check [GitHub Issues](https://github.com/nix-community/nixos-anywhere/issues) for similar reports
- Join the [nixos-anywhere Matrix room](https://matrix.to/#/#nixos-anywhere:nixos.org)
- Include the full output with `--debug` when reporting
