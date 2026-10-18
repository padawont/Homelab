---
title: "Longhorn storage"
status: active
author: "padawont"
date: 2026-10-02
tags: [kubernetes, storage, longhorn, deployment]
technologies: [longhorn, helm, iscsi, kubernetes, k3s]
related_docs:
  - "./04_ADRs/26-adopt-nixos-on-node-main.md"
  - "./02_Knowledge/technologies/kubernetes/longhorn/overview.md"
  - "./02_Knowledge/technologies/kubernetes/longhorn/installation.md"
  - "./05_Implementations/node-main/k3s/overview.md"
references:
  online:
    - url: "https://longhorn.io/docs/"
      title: "Longhorn documentation"
    - url: "https://longhorn.io/docs/latest/deploy/install/install-with-helm/"
      title: "Install Longhorn with Helm"
  repo:
    - "./04_ADRs/26-adopt-nixos-on-node-main.md"
    - "./05_Implementations/node-main/k3s/overview.md"
    - "./rollback.md"
node: node-main
---

# Longhorn storage

Distributed block storage for the single-node k3s cluster on `node-main`. Longhorn
is the cluster's **default StorageClass**, providing dynamic PVCs backed by a
dedicated data disk plus a root-LVM SSD directory.

## Prerequisites

- Working k3s cluster — see `./05_Implementations/node-main/k3s/overview.md`.
- Host packages: **open-iscsi** (`iscsid` enabled + active) and **nfs-common**.
- Kernel module **`iscsi_tcp`** loaded.
- Backing paths: `/var/lib/longhorn` (dedicated `/dev/sda1`, ext4, ~938 GB) and
  `/var/lib/longhorn-ssd` (directory on the root LVM).

## Deployment

### Pre-deploy checks

```bash
systemctl status iscsid
modprobe iscsi_tcp && lsmod | grep iscsi_tcp
dpkg -l | grep -E 'open-iscsi|nfs-common'
findmnt /var/lib/longhorn
```

### Deploy

```bash
helm repo add longhorn https://charts.longhorn.io
helm repo update
helm install longhorn longhorn/longhorn \
  --namespace longhorn-system \
  --create-namespace \
  --version 1.13.0 \
  --set defaultSettings.defaultReplicaCount=1
```

### Post-deploy verification

```bash
kubectl -n longhorn-system get pods
kubectl get storageclass
kubectl -n longhorn-system get nodes.longhorn.io
kubectl -n longhorn-system get disks.longhorn.io
```

Longhorn pods are Running, both disks report **Ready + Schedulable**, and
`longhorn` is the default StorageClass. A 1 GiB PVC bound successfully to the
`longhorn` class during deployment.

## Configuration

| Item | Value |
|---|---|
| Chart | `longhorn/longhorn` **1.13.0** |
| Namespace | `longhorn-system` |
| Replicas | `defaultSettings.defaultReplicaCount=1` (single node) |
| Default StorageClass | `longhorn` (k3s `local-path` default annotation removed) |
| Additional class | `longhorn-static` |

### Disks

| Disk | Name | Path | Basis | Reserved | Tags |
|---|---|---|---|---|---|
| 1 (default) | `default-disk-d5814dcb3a640738` | `/var/lib/longhorn/` | `/dev/sda1` ext4, label `longhorn`, UUID `6d6a0b8c-0c6f-44ce-a627-8a59346820f4`, 938 GB | ~100 GB (`100000000000`) | — |
| 2 | `root-ssd` | `/var/lib/longhorn-ssd` | directory on root LVM | 20 GB (`21474836480`) | `ssd`, `root` |

`/etc/fstab` entry for disk 1:

```
UUID=6d6a0b8c-0c6f-44ce-a627-8a59346820f4 /var/lib/longhorn ext4 defaults,noatime 0 2
```

## Operations

```bash
# Health
kubectl -n longhorn-system get pods
kubectl -n longhorn-system get nodes.longhorn.io,disks.longhorn.io
kubectl get pvc -A

# Volume / replica state
kubectl -n longhorn-system get volumes.longhorn.io

# Upgrade (pin the chart version)
helm repo update
helm -n longhorn-system upgrade longhorn longhorn/longhorn --version <new>
```

Back up PVC data before upgrades. Teardown and data-loss risk are documented in
`./rollback.md`.
