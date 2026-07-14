---
title: "Supported Platforms"
status: draft
author: "padawont"
date: 2026-07-14
tags:
  - nixos-anywhere
  - hetzner
  - digitalocean
  - platforms
sources:
  - url: "https://github.com/nix-community/nixos-anywhere/blob/main/docs/howtos/INDEX.md"
    title: "nixos-anywhere — How-to guides"
  - url: "https://github.com/nix-community/nixos-anywhere"
    title: "nix-community/nixos-anywhere"
last_audit_date: 2026-07-14
---

# Supported Platforms

nixos-anywhere supports installing NixOS on any x86_64 Linux machine reachable via SSH with kexec support. This covers most cloud providers, VPS hosts, and bare-metal servers.

## Platform comparison

| Platform | Architecture | kexec | Notes |
|---|---|---|---|
| Hetzner | x86_64 | ✅ Works | Best tested platform; rescue mode workflow |
| DigitalOcean | x86_64 | ✅ Works | Standard droplets; disable cloud-init |
| AWS EC2 | x86_64, aarch64 | ✅/⚠ Depends | Nitro instances good; older may need custom kexec |
| Oracle Cloud | aarch64, x86_64 | ⚠ Varies | ARM instances need custom kexec image |
| Generic bare metal | x86_64 | ✅ Most | Debian/Ubuntu pre-installed works best |
| Generic VPS | x86_64 | ✅ Most | Requires SSH root access |
| ARM servers | aarch64 | ⚠ Custom kexec needed | Provide `--kexec` with aarch64 image |

## Hetzner

Hetzner is the most tested platform for nixos-anywhere.

### Workflow

1. Boot into Hetzner Rescue System (available in Robot Console)
2. Hetzner assigns a temporary SSH key — copy yours in:
   ```
   ssh-copy-id root@<hetzner-ip>
   ```
3. Run nixos-anywhere:
   ```
   nix run github:nix-community/nixos-anywhere -- --flake .#host root@<hetzner-ip>
   ```

### Hetzner-specific configuration

```nix
{ config, pkgs, ... }: {
  # For AX series servers, GRUB writes directly to disk
  boot.loader.grub = {
    enable = true;
    device = "/dev/sda";
    efiSupport = false;
  };

  # For CX/NX series (UEFI), use systemd-boot
  # boot.loader.systemd-boot.enable = true;
  # boot.loader.efi.canTouchEfiVariables = true;

  # Hetzner uses predictable network interface names
  networking.useDHCP = true;

  system.stateVersion = "24.11";
}
```

### Server series

| Series | Type | Boot | Notes |
|---|---|---|---|
| AX | Dedicated | BIOS/GRUB | Set `boot.loader.grub.device = "/dev/sda"` |
| CX | Cloud VPS | UEFI | Use systemd-boot |
| NX | Cloud VPS | UEFI | Same as CX |
| CPX | Cloud VPS | UEFI | Same as CX |

## DigitalOcean

### Workflow

1. Create a standard Droplet (Ubuntu or Debian)
2. Add your SSH key when creating the Droplet
3. Run nixos-anywhere:
   ```
   nix run github:nix-community/nixos-anywhere -- --flake .#host root@<droplet-ip>
   ```

### DigitalOcean-specific configuration

```nix
{ config, pkgs, ... }: {
  # DigitalOcean uses UEFI
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  # Disable cloud-init (DigitalOcean injects it)
  services.cloud-init.enable = false;

  # Use DHCP for networking
  networking.useDHCP = true;

  system.stateVersion = "24.11";
}
```

### Known limitations

- Droplets may not provide serial console output
- kexec can fail on some Droplet sizes (try a larger plan)
- Swap is not configured by default — add it to your disko config

## AWS EC2

### Workflow

1. Launch an EC2 instance with Ubuntu or Amazon Linux
2. Configure security group to allow SSH from your IP
3. Connect and run nixos-anywhere:
   ```
   nix run github:nix-community/nixos-anywhere -- --flake .#host ubuntu@<ec2-public-ip>
   ```

### EC2-specific considerations

- Use `ubuntu` or `admin` user initially (root SSH is disabled by default)
- The user must have passwordless sudo
- Nitro instances (most modern types) support kexec well
- Older instance types may need a custom kexec image

## Generic x86_64

Any x86_64 Linux server with:
- SSH access (root or sudo-capable user)
- kexec support (check with `command -v kexec && echo "kexec binary found"`)
- At least 1 GB RAM
- Outbound internet access (to download Nix packages)

Tested base OS distributions:
- Debian 11+ (best compatibility)
- Ubuntu 20.04+
- Fedora 38+
- CentOS 7+ / Rocky Linux 8+
- Arch Linux (with kexec-tools installed)

## ARM / aarch64

nixos-anywhere can install on aarch64 systems but requires a custom kexec image:

```console
$ nix run github:nix-community/nixos-anywhere -- \
  --flake .#host \
  --kexec "$(nix build --print-out-paths github:nix-community/nixos-images#packages.aarch64-linux.kexec-installer-nixos-unstable-noninteractive)/nixos-kexec-installer-noninteractive-aarch64-linux.tar.gz" \
  root@arm-server
```

Platforms where aarch64 has been tested:
- Oracle Cloud ARM instances (Ampere A1)
- AWS EC2 Graviton instances (a1, t4g, m6g, c6g, r6g)

## Platform support matrix

| Provider | x86_64 | aarch64 | kexec | Needs custom image |
|---|---|---|---|---|
| Hetzner | ✅ | ❌ | ✅ | No |
| DigitalOcean | ✅ | ❌ | ✅ | No |
| AWS EC2 | ✅ | ✅ | ⚠ Varies | Sometimes (older instances, ARM) |
| Oracle Cloud | ✅ | ✅ | ⚠ Varies | Yes (ARM) |
| Linode | ✅ | ❌ | ✅ | No |
| Vultr | ✅ | ❌ | ✅ | No |
| Scaleway | ✅ | ✅ | ⚠ Varies | Yes (ARM) |
| Bare metal (DIY) | ✅ | N/A | ✅ Most | No |
| Proxmox VM | ✅ | ✅ | ✅ | No |
| VMware VM | ✅ | ✅ | ✅ | No |

> For platform-specific troubleshooting, see [troubleshooting.md](troubleshooting.md).
