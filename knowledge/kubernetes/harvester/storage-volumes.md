---
title: "Harvester Storage Volumes"
status: draft
date: 2026-07-28
author: padawont
tags:
  - harvester
  - storage
  - longhorn
  - volumes
  - persistent-volumes
sources:
  - url: "https://docs.harvesterhci.io/v1.8/volume/index"
    title: "Harvester Volume Management"
  - url: "https://longhorn.io/docs/"
    title: "Longhorn Documentation"
last_audit_date: 2026-07-28
related_configs:
  - "configs-and-adr/node-main/vm/"
---

# Harvester Storage Volumes

## Architecture

Harvester uses Longhorn as its default and only storage backend. Longhorn is a cloud-native distributed block storage system that provisions volumes as Kubernetes PersistentVolumeClaims (PVCs). Each volume is composed of replicas stored on the node's local disks, managed by Longhorn's engine and instance manager processes.

The storage stack:
- **Longhorn CSI Driver** — Implements the Container Storage Interface (CSI) for dynamic volume provisioning
- **Longhorn Manager** — Kubernetes controller that manages volumes, replicas, engines, and backups
- **Longhorn Engine** — Runs on the node where the volume is attached, handles I/O requests
- **Longhorn Instance Manager** — Manages engine and replica instances on each node

## StorageClasses

Harvester installs with one default StorageClass:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: harvester-longhorn
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "3"
  staleReplicaTimeout: "30"
  fromBackup: ""
  fsType: ext4
  dataLocality: disabled
allowVolumeExpansion: true
```

### Key Parameters

| Parameter | Description | Lab Value |
|---|---|---|
| `numberOfReplicas` | Number of volume replicas across nodes | `1` (single-node) |
| `dataLocality` | Whether data stays local to the consuming node | `disabled` |
| `staleReplicaTimeout` | Time in minutes before a stale replica is evicted | `30` |
| `fromBackup` | Restore a volume from a backup on creation | `""` |
| `fsType` | Filesystem type for the volume | `ext4` |
| `diskSelector` | Comma-separated disk tags for replica placement | `""` |
| `nodeSelector` | Comma-separated node names for replica placement | `""` |

### Custom StorageClasses

Create additional StorageClasses for specific use cases:

```yaml
# Single-replica StorageClass for single-node
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: harvester-longhorn-single
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "1"
  dataLocality: local
  fsType: ext4
allowVolumeExpansion: true
```

```yaml
# SSD-tagged StorageClass for fast storage
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "1"
  diskSelector: "ssd,fast"
  dataLocality: local
allowVolumeExpansion: true
```

## Volume Operations

### Creating a Volume

Through the Harvester UI:
1. Navigate to **Volumes**
2. Click **Create**
3. Set the name, size, and StorageClass
4. Optionally specify access mode (RWO or RWX) and source (empty, backup, or image)

Through kubectl:
```bash
kubectl create -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-data-volume
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Block
  resources:
    requests:
      storage: 50Gi
  storageClassName: harvester-longhorn
EOF
```

### Attaching a Volume to a VM

Volumes are attached to VMs as disks. Through the UI, edit the VM and add a new volume. Through the VM spec, reference the PVC:

```yaml
spec:
  template:
    spec:
      domain:
        devices:
          disks:
            - name: data
              disk:
                bus: virtio
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: my-data-volume
```

### Cloning a Volume

Clone an existing volume to create an independent copy. Cloning uses Longhorn's snapshot-and-restore mechanism:

```bash
# Via Longhorn API
kubectl apply -f - <<EOF
apiVersion: harvesterhci.io/v1beta1
kind: Volume
metadata:
  name: cloned-volume
  namespace: default
spec:
  source:
    pvc: original-pvc
  size: "50Gi"
EOF
```

### Exporting a Volume

Export a volume as a QCOW2 image file for portability:

1. Navigate to **Volumes**
2. Select the volume and click **Export**
3. The volume is exported as a QCOW2 image, downloadable from the UI

### Resizing a Volume

Volumes can be expanded online (while attached to a running VM) if:
- The StorageClass has `allowVolumeExpansion: true` (default for `harvester-longhorn`)
- The VM's guest OS supports online disk resizing
- The filesystem inside the guest supports online resize (ext4, xfs)

Resize through the UI by editing the volume's size, or:

```bash
kubectl patch pvc my-data-volume -n default -p '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}'
```

### Deleting a Volume

Deleting a volume removes the PVC and all associated replicas. Data is permanently lost unless a backup exists. Use `kubectl delete pvc` or the UI.

## Snapshots

Volume snapshots are point-in-time, copy-on-write images managed by the Kubernetes VolumeSnapshot API:

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-volume-snapshot
  namespace: default
spec:
  source:
    persistentVolumeClaimName: my-data-volume
```

Snapshots are used for:
- Pre-upgrade rollback points
- Volume cloning (via snapshot restore)
- Creating new volumes from an existing state

## Storage Network

Harvester supports a dedicated storage network for Longhorn replica traffic. This keeps storage replication (e.g., between nodes) off the management network. Configuring a storage network requires:

1. A dedicated VLAN or physical NIC for storage traffic
2. A custom cluster network (see [networking.md](networking.md))
3. Enabling the storage network in Longhorn settings

**Single-node consideration:** A dedicated storage network is unnecessary since all replicas are on the same node. Replica traffic does not cross the network.

## Backup

Volume-level backups (distinct from VM-level backups) are managed through Longhorn's backup mechanism:

| Backup Type | Scope | Target |
|---|---|---|
| VM Backup | Full VM (all volumes) | NFS/S3 |
| Volume Backup | Single volume | NFS/S3 |
| Volume Snapshot | Single volume | Local (Longhorn) |

Configure a backup target in **Settings > backup-target** (see [vm-management.md](vm-management.md) for details).

## References

- [Harvester Volume Management](https://docs.harvesterhci.io/v1.8/volume/index)
- [Longhorn Documentation](https://longhorn.io/docs/)
- [Longhorn StorageClass Parameters](https://longhorn.io/docs/1.11.2/references/examples/)
