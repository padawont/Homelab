---
status: draft
service: harvester
target: node-main
related_knowledge:
  - knowledge/kubernetes/harvester/installation.md
  - knowledge/kubernetes/harvester/networking.md
related_configs:
  - configs-and-adr/node-main/vm/harvester-config.yaml
  - configs-and-adr/adr/0003-harvester-vm-platform.md
---

# Deploy Harvester HCI v1.8

Procedure to install and configure Harvester HCI v1.8 on node-main as the VM infrastructure platform. Harvester replaces the NixOS+K3s setup with an Elemental SLE Micro bare-metal OS.

## Prerequisites

- Host meets minimum hardware requirements (8 cores, 32GB RAM, 250GB SSD, UEFI boot)
- USB drive (8GB+) or PXE server for ISO installation
- Network: single flat VLAN `192.168.111.0/24`
- VIP: `192.168.111.51` (static, must be unused)
- DNS server: `192.168.111.1`
- NTP server: `0.pool.ntp.org`
- Cluster token (generate: `openssl rand -hex 16`)
- SSH key pair for the `rancher` user
- Rancher server (external, on existing K3s cluster) for Virtualization Management integration
- Internet access to pull container images during install

## Steps

### 1. Preparation

Download the Harvester v1.8 ISO:

```bash
wget https://releases.rancher.com/harvester/v1.8.1/harvester-v1.8.1-amd64.iso
```

Write ISO to USB drive:

```bash
sudo dd if=harvester-v1.8.1-amd64.iso of=/dev/sdX bs=4M status=progress
sync
```

Verify UEFI boot is enabled in the BIOS. Disable Legacy Boot if both are supported. Enable virtualization (VT-x/AMD-V) and IOMMU.

### 2. Configuration

Prepare `harvester-config.yaml` at `configs-and-adr/node-main/vm/harvester-config.yaml` with lab-specific values:

```yaml
scheme_version: 1
token: "CHANGE-ME-CLUSTER-TOKEN"
os:
  hostname: harvester
  ssh_authorized_keys:
    - "ssh-ed25519 AAA... user@host"
  ntp_servers:
    - "0.pool.ntp.org"
  dns_nameservers:
    - "192.168.111.1"
install:
  mode: create
  management_interface:
    interfaces:
      - name: ens192
    method: static
    ip: 192.168.111.51/24
    gateway: 192.168.111.1
  device: /dev/sda
  vip: 192.168.111.51
  vip_mode: static
  cluster_pod_cidr: 10.52.0.0/16
  cluster_service_cidr: 10.53.0.0/16
  cluster_dns: 10.53.0.10
  role: management
  skipchecks: false
  harvester:
    storage_class:
      replica_count: 1
  wipe_all_disks: true
```

Host the config file on an HTTP server reachable from the installation environment, or input values manually via the interactive TUI.

### 3. Deployment

Boot the target machine from the USB drive and select `Harvester Installer`.

At the `Customize the host` step, provide the URL to the `harvester-config.yaml`:

```
http://192.168.111.X/harvester-config.yaml
```

Or input the values manually through the interactive dialogs:
- Installation mode: `Create a new Harvester cluster`
- Hostname: `harvester`
- Network: static IP `192.168.111.51/24`, gateway `192.168.111.1`
- VIP: `192.168.111.51` (static)
- DNS: `192.168.111.1`
- NTP: `0.pool.ntp.org`
- Cluster token: `<generated token>`
- SSH authorized keys: paste your public key

The installation takes 10–20 minutes. The node reboots automatically when complete.

### 4. Verification

Access the Harvester UI:

```bash
https://192.168.111.51
```

Set the admin password on first login.

Check cluster status from the UI dashboard or via CLI:

```bash
kubectl get nodes
```

Expected output: `harvester` in `Ready` state.

Verify the default StorageClass has replica count 1:

```bash
kubectl get storageclass harvester-longhorn -o yaml | grep numberOfReplicas
```

Expected output: `numberOfReplicas: "1"`.

### 5. Post-Install Configuration

Import Harvester into Rancher Virtualization Management:

1. In Rancher UI, navigate to Virtualization Management → Import Existing
2. Set the Cluster Name and click Create
3. Rancher displays a registration guide with a manifest URL
4. Apply the manifest URL to the Harvester cluster:

```bash
# From the Harvester CLI, set the cluster-registration-url:
kubectl patch settings.harvesterhci.io cluster-registration-url \
  --type=merge \
  --patch='{"value": "https://rancher.example.com/v3/import/...yaml"}'
```

5. A `cattle-cluster-agent` pod appears in the Harvester cluster. Once ready, the cluster appears in Rancher's Virtualization Management view.

Configure a backup target:

```bash
# Via Harvester UI: Settings > backup-target
# NFS example: nfs://192.168.111.X:/path/to/backups
```

For single-node operation, ensure the following settings are in effect:
- Longhorn replica count: 1 (done during install)
- `restoreVM` in upgrade-config: true (auto-restart VMs after upgrade)
- `guaranteedInstanceManagerCPU`: set lower than default (12) for limited resources

### Verification Checklist

- [ ] Harvester UI accessible at `https://192.168.111.51`
- [ ] `kubectl get nodes` shows `Ready`
- [ ] StorageClass `harvester-longhorn` has `numberOfReplicas: 1`
- [ ] Harvester appears in Rancher Virtualization Management
- [ ] Backup target is configured and reachable
- [ ] VM network (VLAN) is created for workload VMs
- [ ] VM images are uploaded for provisioning

## Rollback

Harvester uses an immutable OS (Elemental SLE Micro). Rollback requires a full reinstall:

```bash
# 1. Backup any VMs from the Harvester UI (Backup → To Backup Target)
# 2. Reinstall from scratch using the same ISO
# 3. Restore cluster from backup token (same token = same cluster identity)
# 4. Restore VMs from backup target
```

If you need to abandon Harvester entirely, reinstall NixOS from your NixOS ISO and restore the K3s cluster from your NixOS configuration backup.
