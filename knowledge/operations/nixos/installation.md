---
title: "Installation"
status: draft
author: "padawont"
date: 2026-07-14
tags:
  - nixos
  - installation
  - disko
  - partitioning
sources:
  - url: "https://nixos.org/manual/nixos/stable/#sec-installation"
    title: "NixOS Manual — Installation"
  - url: "https://github.com/nix-community/disko"
    title: "nix-community/disko — Declarative disk partitioning"
  - url: "https://nixos.org/download.html"
    title: "NixOS Download Page"
last_audit_date: 2026-07-14
---

# Installation

This note covers installing NixOS on a physical or virtual machine using the ISO image and manual partitioning. For remote installations over SSH without physical access, see [nixos-anywhere](../nixos-anywhere/what-is-nixos-anywhere.md).

## ISO installation

### Download

Download the NixOS ISO from [nixos.org/download](https://nixos.org/download.html). Options:

| Image | Use case |
|---|---|
| Minimal ISO (~700MB) | CLI-only installation |
| GNOME ISO (~2GB) | Graphical installer with desktop |
| Plasma ISO (~2GB) | KDE Plasma installer with desktop |

### Write to USB

**Linux:**

```console
# Find the USB device
$ lsblk
# Unmount all partitions
$ sudo umount /dev/sdX*
# Write the ISO
$ sudo dd bs=4M conv=fsync oflag=direct status=progress if=path/to/nixos.iso of=/dev/sdX
```

**macOS:**

```console
$ diskutil unmountDisk diskX
$ sudo dd if=path/to/nixos.iso of=/dev/rdiskX bs=4m
$ diskutil eject /dev/diskX
```

### Boot

1. Plug in the USB drive and restart
2. Enter the boot menu (F12, F9, Esc, or Option on Mac)
3. Select the USB drive (UEFI option preferred)
4. Choose the default installer entry

On the minimal ISO, you'll get a root shell. On graphical ISOs, either use the graphical installer or open a terminal.

## Manual installation

### Networking

Ensure networking is available (the installer needs to download packages):

```console
# Check connectivity
$ ip a
# Configure WiFi with nmtui (if needed)
$ nmtui
```

### Partitioning

The NixOS installer does not partition automatically. Use `parted`, `fdisk`, or `disko`.

**UEFI (GPT) — recommended:**

```console
# Create GPT partition table
$ sudo parted /dev/sda -- mklabel gpt

# Root partition (fill most of the disk)
$ sudo parted /dev/sda -- mkpart root ext4 512MB -8GB

# Swap partition (8GB at the end)
$ sudo parted /dev/sda -- mkpart swap linux-swap -8GB 100%

# EFI system partition (512MB at start)
$ sudo parted /dev/sda -- mkpart ESP fat32 1MB 512MB
$ sudo parted /dev/sda -- set 3 esp on
```

**Legacy Boot (MBR):**

```console
# Create MBR partition table
$ sudo parted /dev/sda -- mklabel msdos

# Root partition
$ sudo parted /dev/sda -- mkpart primary 1MB -8GB
$ sudo parted /dev/sda -- set 1 boot on

# Swap partition
$ sudo parted /dev/sda -- mkpart primary linux-swap -8GB 100%
```

### Formatting

```console
# Format root as ext4
$ sudo mkfs.ext4 -L nixos /dev/sda1

# Format swap
$ sudo mkswap -L swap /dev/sda2

# Format boot (UEFI only)
$ sudo mkfs.fat -F 32 -n boot /dev/sda3
```

### Mount and install

```console
# Mount root
$ sudo mount /dev/disk/by-label/nixos /mnt

# Mount boot (UEFI)
$ sudo mkdir -p /mnt/boot
$ sudo mount -o umask=077 /dev/disk/by-label/boot /mnt/boot

# Enable swap
$ sudo swapon /dev/sda2

# Generate initial configuration
$ sudo nixos-generate-config --root /mnt

# Edit the configuration
$ sudo nano /mnt/etc/nixos/configuration.nix

# Install
$ sudo nixos-install

# Set root password (if not done during install)
# For additional users: nixos-enter --root /mnt -c 'passwd alice'

# Reboot
$ sudo reboot
```

## disko (declarative partitioning)

[disko](https://github.com/nix-community/disko) replaces manual partitioning with a declarative Nix configuration.

### disko-config.nix example

```nix
{
  disko.devices = {
    disk = {
      my-disk = {
        device = "/dev/sda";
        type = "disk";
        content = {
          type = "gpt";
          partitions = {
            ESP = {
              type = "EF00";
              size = "500M";
              content = {
                type = "filesystem";
                format = "vfat";
                mountpoint = "/boot";
                mountOptions = [ "umask=0077" ];
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
    };
  };
}
```

### Run disko

```console
# Partition, format, and mount
$ sudo nix run github:nix-community/disko/latest -- --mode destroy,format,mount /tmp/disk-config.nix

# Then proceed with nixos-generate-config and nixos-install as above
```

### disko modes

| Mode | Action |
|---|---|
| `destroy` | Wipe partition tables and filesystems |
| `format` | Create partitions and filesystems |
| `mount` | Mount partitions to their declared mountpoints |
| `create` | `destroy` + `format` + `mount` |

Combine modes with commas: `--mode destroy,format,mount`.

## Post-installation

After first boot:

```console
# Apply any configuration changes
$ sudo nixos-rebuild switch

# Check disk usage
$ df -h

# Install additional packages
# Edit /etc/nixos/configuration.nix and rebuild
```

## Common pitfalls

| Issue | Solution |
|---|---|
| **No boot menu** | Ensure `boot.loader.systemd-boot.enable = true` (UEFI) or `boot.loader.grub.device = "/dev/sda"` (BIOS) |
| **Can't boot installed system** | Set `boot.initrd.kernelModules` with required storage drivers |
| **No WiFi** | Enable `networking.networkmanager.enable = true` |
| **LUKS encryption** | Use disko with LUKS type, include `boot.initrd.luks.devices` |
| **EFI vs BIOS confusion** | Check with `ls /sys/firmware/efi` — if directory exists, booted in UEFI mode |
