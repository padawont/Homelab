---
title: "Harvester Installation"
status: draft
date: 2026-07-28
author: padawont
tags:
  - harvester
  - installation
  - hardware
  - bare-metal
sources:
  - url: "https://docs.harvesterhci.io/v1.8/install/requirements"
    title: "Harvester Hardware Requirements"
  - url: "https://docs.harvesterhci.io/v1.8/install/harvester-config"
    title: "Harvester Configuration Reference"
  - url: "https://docs.harvesterhci.io/v1.8/install/iso-install"
    title: "ISO Installation Guide"
last_audit_date: 2026-07-28
related_configs:
  - "configs-and-adr/node-main/vm/"
---

# Harvester Installation

## Hardware Requirements

Harvester v1.8 requires the following minimum hardware per node:

| Component | Minimum | Recommended |
|---|---|---|
| CPU | 8 cores (x86-64 with hardware virtualization) | 16+ cores |
| RAM | 32 GB | 64+ GB |
| Disk | 250 GB SSD | 500+ GB NVMe SSD |
| Boot | UEFI (Legacy/BIOS boot is not supported) | UEFI |

Additional requirements:
- **Hardware virtualization** must be enabled in BIOS (Intel VT-x / AMD-V)
- **TPM 2.0** recommended but not required
- **Network** — at least one physical NIC for the management network

The homelab node meets the minimum specs with 8 cores, 32 GB RAM, and SSD storage, which is sufficient for a single-node deployment running a handful of VMs.

## Install Methods

### ISO Installation

The standard installation method boots from the Harvester ISO image, available from the [GitHub releases page](https://github.com/harvester/harvester/releases). The ISO boots into an interactive installer that:

1. Detects hardware and configures UEFI boot
2. Prompts for hostname, network config, and disk selection
3. Installs the Elemental SLE Micro base OS to disk
4. Deploys the embedded Kubernetes cluster and Harvester services
5. Applies the harvester-config YAML (if provided via a USB drive or remote URL)

### USB Installation

Write the ISO to a USB drive using `dd` or `balenaEtcher`. Boot from the USB drive and follow the interactive installer.

```bash
# Write ISO to USB (replace /dev/sdX with the correct device)
sudo dd if=harvester-v1.8.1.iso of=/dev/sdX bs=4M status=progress
```

### PXE Installation

Harvester supports PXE boot for automated provisioning at scale. The boot artifacts (kernel, initrd, squashfs image) are extracted from the ISO and served via HTTP/TFTP. A harvester-config YAML file is passed as a kernel parameter to automate the install.

## harvester-config YAML

For unattended installation, provide a `harvester-config.yaml` file via USB drive (at `iso://harvester-config.yaml`) or a remote URL passed as the `harvester.install.config_url` kernel parameter. This file contains all installation parameters:

```yaml
# Example harvester-config.yaml for single-node homelab deployment
scheme_version: 1
server_url: ""                          # Empty for first node
token: "my-shared-cluster-token"        # Cluster join token
os:
  hostname: harvester
  ssh_authorized_keys:
    - "ssh-rsa AAAA..."                # Public key for SSH access
  ntp_servers:
    - 0.pool.ntp.org
    - 1.pool.ntp.org
install:
  mode: create                          # "create" for first node, "join" for additional
  management_interface:
    method: static
    ip: 192.168.111.51/24              # Harvester VIP
    gateway: 192.168.111.1
    dns_nameservers:
      - 192.168.111.1
    interfaces:
      - name: ens192                   # Physical NIC
  data_disk: /dev/sda                   # Disk for Longhorn storage
  force_efi: true                       # UEFI required
  device: /dev/sda                      # Install target disk
  iso_url: ""
  vip: 192.168.111.51                   # Virtual IP for cluster access
  vip_hw_addr: "xx:xx:xx:xx:xx:xx"     # MAC for VIP (optional)
```

### Key Fields

| Field | Description |
|---|---|
| `scheme_version` | Config format version (1 for Harvester v1.0+) |
| `server_url` | URL of the first node for joining nodes; empty when creating the cluster |
| `token` | Shared secret for node-to-node authentication |
| `os.hostname` | Node hostname (set to `harvester` for the homelab) |
| `os.ntp_servers` | NTP servers for time synchronization |
| `install.mode` | `create` for the first node, `join` for additional nodes |
| `install.management_interface` | Static IP or DHCP config for the management NIC |
| `install.data_disk` | Disk to use for Longhorn storage (supports disk tags) |
| `install.vip` | Virtual IP for cluster endpoint (used for UI and API access) |

## Single-Node Considerations

A single-node Harvester deployment requires several configuration adjustments:

### Longhorn Replica Count

By default, Longhorn creates 3 replicas for every volume. On a single node, this causes volume provisioning to fail because replicas cannot be scheduled on different nodes. Set the default replica count to 1 either:

- During installation via harvester-config (setting `replicaCount: 1` in `longhorn.defaultSettings.replicaCount`)
- After installation in the Harvester UI under **Settings > longhorn > Default Setting > Replica Count**
- By editing the `settings.harvesterhci.io` resource directly

### No High Availability

- **Live migration** is not available — VMs cannot move to another node
- **Node failure** means all VMs go down until the node is restored
- **etcd** is not replicated — single point of failure for cluster state
- **Storage** is not replicated — data loss risk if the disk fails
- Backups to NFS/S3 are critical for disaster recovery

### Dedicated Setup Steps

1. Boot from ISO
2. Provide harvester-config.yaml on USB
3. After install completes, access the UI at `https://192.168.111.51`
4. Navigate to **Settings > longhorn > Default Setting** and set Replica Count to 1
5. Configure backup target (NFS or S3) for disaster recovery
6. Configure monitoring and alerting

## Post-Install Configuration

After the initial install, configure:

- **Backup target** — NFS or S3 endpoint for VM backups
- **Storage tags** — tag disks for Longhorn scheduling (not critical on single-node)
- **NTP** — verify time sync (pre-configured in harvester-config)
- **Certificate** — replace the self-signed certificate with a trusted one (optional)
- **Rancher import** — generate the import YAML from Rancher Virtualization Management

## References

- [Harvester Hardware Requirements](https://docs.harvesterhci.io/v1.8/install/requirements)
- [Harvester Configuration Reference](https://docs.harvesterhci.io/v1.8/install/harvester-config)
- [ISO Installation Guide](https://docs.harvesterhci.io/v1.8/install/iso-install)
