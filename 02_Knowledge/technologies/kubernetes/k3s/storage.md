---
title: "k3s storage"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, k3s, storage, local-path]
sources:
  - url: "https://docs.k3s.io/add-ons/storage"
    title: "k3s storage"
  - url: "https://github.com/rancher/local-path-provisioner"
    title: "local-path-provisioner"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/longhorn/overview.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/storage.md"
---

# k3s storage

## Overview

k3s ships the local-path provisioner (`rancher.io/local-path`) as the default StorageClass. It dynamically provisions `PersistentVolume`s as directories on the node's local disk — simple, zero-dependency storage for a single-node homelab where the host disk is the only disk anyway.

## Details

### Local-path provisioner

- Creates one directory per PVC under `/var/lib/rancher/k3s/storage/` (default path).
- `StorageClass` name: `local-path`, provisioner `rancher.io/local-path`.
- Works per node; a PVC is bound to whichever node the pod schedules on.
- Disable with `--disable=local-storage`.

Example — abstract (PVC using the default class):

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 10Gi
  storageClassName: local-path   # optional — this is the default
```

Example — real config (checking the homelab default class):

```bash
sudo k3s kubectl get storageclass
# NAME         PROVISIONER             RECLAIMPOLICY
# local-path   rancher.io/local-path   Delete
```

### Trade-offs

- **Single-node only for real**: data lives on one node's disk; no replication across nodes.
- **`ReadWriteOnce`** semantics per volume.
- **Backup is host-level**: PVs live under `/var/lib/rancher/k3s/storage/`, so the k3s backup already covers them (see `./02_Knowledge/technologies/kubernetes/k3s/operations.md`).
- For replicated, multi-node storage, Longhorn is the usual next step — see `./02_Knowledge/technologies/kubernetes/longhorn/overview.md`. General PV/PVC concepts: `./02_Knowledge/technologies/kubernetes/concepts/storage.md`.

## Sources / Further Reading

- [k3s storage](https://docs.k3s.io/add-ons/storage)
- [local-path-provisioner](https://github.com/rancher/local-path-provisioner)
