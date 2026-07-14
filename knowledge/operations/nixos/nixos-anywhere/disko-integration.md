---
title: "disko Partitioning"
status: draft
author: "padawont"
date: 2026-07-14
tags:
  - nixos-anywhere
  - disko
  - partitioning
  - disk
sources:
  - url: "https://github.com/nix-community/disko"
    title: "nix-community/disko — Declarative disk partitioning"
  - url: "https://github.com/nix-community/nixos-anywhere"
    title: "nix-community/nixos-anywhere"
last_audit_date: 2026-07-14
---

# disko Integration

nixos-anywhere uses [disko](https://github.com/nix-community/disko) for declarative disk partitioning and formatting. The partition layout is defined in a Nix configuration file that is passed to the disko module.

## How nixos-anywhere invokes disko

When the flake has `disko.devices` defined (or you pass `--disko-mode disko`), nixos-anywhere:

1. Extracts `disko.devices` from your NixOS configuration
2. Runs `disko --mode destroy,format,mount` to wipe, partition, format, and mount
3. Confirms the mount points are correct
4. Proceeds with `nixos-install` into the mounted filesystem

## disko-config.nix structure

A disko configuration defines disks, their partition tables, partitions, filesystems, and mount points:

```nix
{
  disko.devices = {
    disk = {
      main = {
        type = "disk";
        device = "/dev/sda";
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

## Common disk layouts

### Single disk, GPT, ext4

```nix
disko.devices.disk.main = {
  type = "disk";
  device = "/dev/sda";
  content = {
    type = "gpt";
    partitions = {
      ESP = { size = "512M"; type = "EF00"; content = { type = "filesystem"; format = "vfat"; mountpoint = "/boot"; }; };
      root = { size = "100%"; content = { type = "filesystem"; format = "ext4"; mountpoint = "/"; }; };
    };
  };
};
```

### Single disk with swap

```nix
disko.devices.disk.main = {
  type = "disk";
  device = "/dev/sda";
  content = {
    type = "gpt";
    partitions = {
      ESP = { size = "512M"; type = "EF00"; content = { type = "filesystem"; format = "vfat"; mountpoint = "/boot"; }; };
      swap = { size = "8G"; content = { type = "swap"; }; };
      root = { size = "100%"; content = { type = "filesystem"; format = "ext4"; mountpoint = "/"; }; };
    };
  };
};
```

### LUKS encryption

```nix
disko.devices.disk.main = {
  type = "disk";
  device = "/dev/sda";
  content = {
    type = "gpt";
    partitions = {
      ESP = { size = "512M"; type = "EF00"; content = { type = "filesystem"; format = "vfat"; mountpoint = "/boot"; }; };
      luks = {
        size = "100%";
        content = {
          type = "luks";
          name = "crypted";
          settings = { allowDiscards = true; };
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
```

### Btrfs with subvolumes

```nix
disko.devices.disk.main = {
  type = "disk";
  device = "/dev/sda";
  content = {
    type = "gpt";
    partitions = {
      ESP = { size = "512M"; type = "EF00"; content = { type = "filesystem"; format = "vfat"; mountpoint = "/boot"; }; };
      root = {
        size = "100%";
        content = {
          type = "btrfs";
          extraArgs = [ "-f" ];
          subvolumes = {
            "/root" = { mountpoint = "/"; };
            "/home" = { mountpoint = "/home"; };
            "/nix" = { mountpoint = "/nix"; };
            "/swap" = { mountpoint = "/.swapvol"; swap.swapfile.size = "8G"; };
          };
        };
      };
    };
  };
};
```

### ZFS

```nix
disko.devices = {
  disk.main = {
    type = "disk";
    device = "/dev/sda";
    content = {
      type = "gpt";
      partitions = {
        boot = { size = "1G"; type = "EF00"; content = { type = "filesystem"; format = "vfat"; mountpoint = "/boot"; }; };
        zfs = { size = "100%"; content = { type = "zfs"; pool = "zroot"; }; };
      };
    };
  };
  zpool.zroot = {
    type = "zpool";
    mode = "";
    datasets = {
      "root" = { type = "zfs_fs"; mountpoint = "/"; };
      "home" = { type = "zfs_fs"; mountpoint = "/home"; };
      "nix" = { type = "zfs_fs"; mountpoint = "/nix"; };
    };
  };
};
```

### Multi-disk with RAID

```nix
disko.devices = {
  disk = {
    one = { type = "disk"; device = "/dev/sda"; content = { type = "gpt"; partitions = { raid = { size = "100%"; content = { type = "mdadm"; name = "md0"; }; }; }; }; };
    two = { type = "disk"; device = "/dev/sdb"; content = { type = "gpt"; partitions = { raid = { size = "100%"; content = { type = "mdadm"; name = "md0"; }; }; }; }; };
  };
  mdadm.md0 = {
    type = "mdadm";
    level = 1;
    content = {
      type = "gpt";
      partitions = {
        root = { size = "100%"; content = { type = "filesystem"; format = "ext4"; mountpoint = "/"; }; };
      };
    };
  };
};
```

## Partition types reference

| Type code | Meaning |
|---|---|
| `EF00` | EFI System Partition (ESP) |
| `8200` | Linux swap |
| `8300` | Linux filesystem |
| `FD00` | Linux RAID |

> For general disko setup and basic partitioning, see [../installation.md](../installation.md). This note focuses on disko usage within nixos-anywhere.

## disko CLI modes

These are the modes disko uses internally:

| Mode | Action | Destructive? |
|---|---|---|
| `destroy` | Wipe partition tables | Yes |
| `format` | Create partitions and filesystems | Yes |
| `mount` | Mount to declared mountpoints | No |
| `destroy,format,mount` | Full create operation (wipe, partition, format, mount) | Yes |

**Important:** disko is destructive. Running it on a disk will erase all existing data. Always verify the `device` path is correct before running.
