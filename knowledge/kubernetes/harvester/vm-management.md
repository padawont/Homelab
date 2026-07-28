---
title: "Harvester VM Management"
status: draft
date: 2026-07-28
author: padawont
tags:
  - harvester
  - virtual-machines
  - kubevirt
  - backup
  - snapshots
sources:
  - url: "https://docs.harvesterhci.io/v1.8/vm"
    title: "Harvester VM Management"
  - url: "https://docs.harvesterhci.io/v1.8/vm/backup-restore"
    title: "Harvester Backup and Restore"
  - url: "https://docs.harvesterhci.io/v1.8/vm/live-migration"
    title: "Harvester Live Migration"
last_audit_date: 2026-07-28
related_configs:
  - "configs-and-adr/node-main/vm/"
---

# Harvester VM Management

## VM Lifecycle

Harvester VMs are Kubernetes custom resources managed via the UI, kubectl, or the REST API. The primary resource types are:

- **VirtualMachine** — Desired state of the VM (includes template, runs strategy, and stop behavior)
- **VirtualMachineInstance** — Running instance of a VM (read-only, reflects actual runtime state)

### Creating a VM

VMs can be created from:

1. **Images** — Upload a QCOW2, raw, or ISO image to the Harvester image library, then create a VM from it
2. **Volume** — Boot from an existing PVC-backed volume
3. **VM Template** — Reusable VM configurations with preset resources

**Fields for VM creation:**

| Field | Description | Lab Value |
|---|---|---|
| Name | VM hostname | User-defined |
| CPU | Number of vCPUs | 2-4 (per VM, within 8-core budget) |
| Memory | RAM allocation in GB | 4-8 GB (per VM, within 32 GB budget) |
| Image | Source image for boot disk | QCOW2 from image library |
| Volume Size | Size of the root disk | 20-50 GB |
| Network | Attach to cluster network or NAD | Management VLAN network |
| SSH Keys | Cloud-init public key injection | User's public key |
| Cloud-init | User-data and network-data | Optional |

### Editing a VM

VMs can be edited while stopped. Some resources support hotplug (see below). Editable fields include CPU, memory, volume attachments, network interfaces, and cloud-init.

### Cloning a VM

Clone an existing VM to create an independent copy. The clone creates a new volume from a snapshot of the source VM's root disk. Cloned VMs are fully independent — changes to the source do not propagate.

### Deleting a VM

Deleting a VM removes the VirtualMachine resource and, by default, deletes the associated volumes. To preserve volumes, set the VM's `spec.retainDataOnRemoval` flag to `true` before deletion.

## Live Migration

Live migration moves a running VM from one node to another without downtime. It requires:

- **2+ nodes** in the cluster
- **Shared storage** (Longhorn volumes are shared by default)
- **VM with no host-specific resources** (no PCI passthrough, no vGPU, no nodeSelector)
- **Same CPU model** on source and destination nodes

**Single-node limitation:** Live migration is not available in the homelab. VMs must be stopped and restarted for any node events.

### Migration Status

- **Pending** — Migration requested, not yet started
- **Scheduling** — Target node being selected
- **Preparing Target** — Target node preparing to receive the VM
- **Migrating** — Memory and disk state being transferred
- **Completed** — VM running on target node
- **Failed** — Migration encountered an error

## Backup and Restore

Backups capture the full state of a VM, including volumes, metadata, and configuration. They are stored on an external backup target (NFS or S3).

### Backup Target Configuration

Configure the backup target in **Settings > backup-target**:

```yaml
# NFS example
type: nfs
nfs:
  server: 192.168.111.10
  path: /mnt/backups/harvester

# S3 example
type: s3
s3:
  endpoint: https://s3.us-east-1.amazonaws.com
  bucket: harvester-backups
  region: us-east-1
  accessKeyId: AKIA...
  secretAccessKey: ...
```

### Creating a Backup

1. Navigate to **Virtual Machines > Backups**
2. Click **Create**
3. Select the VM to back up
4. Set the backup target (uses the global setting by default)
5. Optionally set a backup schedule (cron expression)

### Scheduled Backups

Backups can be scheduled using a cron expression:

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: ScheduleVMBackup
metadata:
  name: daily-backup
  namespace: default
spec:
  vmBackupSpec:
    source:
      apiGroup: kubevirt.io
      kind: VirtualMachine
      name: my-vm
  cron: "0 2 * * *"   # Daily at 2 AM
  retentionCount: 7   # Keep 7 backups, delete oldest
```

### Restoring a Backup

1. Navigate to **Virtual Machines > Backups**
2. Find the backup and click **Restore**
3. Specify a new VM name (restores as a new VM)
4. The restored VM is created with the same configuration as the original

### VM Snapshots

Snapshots capture the current state of a VM's volumes at a point in time. They differ from backups:

| Feature | Backup | Snapshot |
|---|---|---|
| Storage | External (NFS/S3) | Local (Longhorn) |
| Portability | Yes — can restore on different cluster | No — tied to the cluster |
| Retention | Configurable | Manual deletion |
| Performance Impact | Read from disk during creation | Instant (copy-on-write) |
| Use Case | Disaster recovery | Pre-upgrade checkpoint |

Snapshots are created via the UI under **Virtual Machines > Snapshots** or via kubectl:

```bash
kubectl create -f - <<EOF
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-vm-snapshot
  namespace: default
spec:
  source:
    persistentVolumeClaimName: my-vm-root
EOF
```

## Hotplug

Harvester supports hotplugging certain resources while a VM is running:

| Resource | Hotplug Support | Notes |
|---|---|---|
| Volumes | Yes | Additional data disks only (not root disk) |
| CPU | Yes | Requires KubeVirt CPU hotplug support (v1.8+) |
| Memory | Yes | Requires KubeVirt memory hotplug support (v1.8+) |
| NIC | Yes | Hot-plug network interfaces |

CPU and memory hotplug require the VM to use a CPU topology with the `hotpluggable` flag. Not all guest operating systems support CPU/memory hotplug.

## CPU Pinning and Resource Overcommit

### CPU Pinning

Dedicated CPU cores for VMs that require consistent performance:

```yaml
spec:
  template:
    spec:
      domain:
        cpu:
          dedicatedCpuPlacement: true
          cores: 2
```

When enabled, the VM gets exclusive access to the specified vCPUs. The hypervisor will not schedule other workloads on those cores.

### Resource Overcommit

Harvester allows overcommitting CPU and memory to increase VM density. Overcommit is configured globally:

| Setting | Default | Description |
|---|---|---|
| `overcommit-config` | CPU: 1.0, Memory: 1.0 | Ratio of allocated to physical resources |

A CPU overcommit of 2.0 means you can allocate 16 vCPUs on an 8-core host. Memory overcommit of 1.5 means you can allocate 48 GB on a 32 GB host. Overcommitting beyond physical capacity risks performance degradation under load.

In the homelab (8 cores, 32 GB RAM), modest overcommit (CPU 1.5, Memory 1.2) allows running 3-4 small VMs alongside the Harvester system services.

## Validated OS List

Harvester v1.8 validates the following guest operating systems:

| OS | Version |
|---|---|
| Ubuntu | 20.04, 22.04, 24.04 |
| CentOS | 7, 8 (stream), 9 (stream) |
| Rocky Linux | 8, 9 |
| SLE / openSUSE | SLE 15 SP5+, openSUSE Leap 15.5+ |
| Debian | 11, 12 |
| Fedora | 38+ |
| Windows | Server 2019, Server 2022, 10, 11 |
| RHEL | 8, 9 |

Unlisted OS images may still work but lack official validation and may have missing virtio drivers or cloud-init compatibility issues. Always install `qemu-guest-agent` inside guests for proper VM metrics and graceful shutdown.

## References

- [Harvester VM Management](https://docs.harvesterhci.io/v1.8/vm)
- [Harvester Backup and Restore](https://docs.harvesterhci.io/v1.8/vm/backup-restore)
- [Harvester Live Migration](https://docs.harvesterhci.io/v1.8/vm/live-migration)
- [KubeVirt VM Lifecycle](https://kubevirt.io/user-guide/virtual_machines/virtual_machine/)
