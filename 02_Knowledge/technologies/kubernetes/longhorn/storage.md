---
title: "Longhorn storage classes and volumes"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, storage, longhorn, block-storage, storageclass]
sources:
  - url: "https://longhorn.io/docs/1.12.1/nodes-and-volumes/volumes/"
    title: "Longhorn volumes and snapshots"
  - url: "https://longhorn.io/docs/1.12.1/references/storage-class-parameters/"
    title: "Longhorn Storage Class Parameters"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/storage.md"
---

# Longhorn storage classes and volumes

## Overview

Longhorn exposes storage to workloads as Kubernetes StorageClasses backed by its CSI driver. A PVC using a Longhorn StorageClass is provisioned as a replicated block volume. The default `longhorn` StorageClass is created during install and can be tuned per volume or per class.

## Details

### Default StorageClass

Installing Longhorn creates a StorageClass named `longhorn` with `provisioner: driver.longhorn.io`. Workloads that request a PVC without a `storageClassName` get Longhorn only if it is marked default; otherwise reference the class explicitly.

```yaml
Example — abstract
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn
provisioner: driver.longhorn.io
allowVolumeExpansion: true
parameters:
  numberOfReplicas: "3"
  staleReplicaTimeout: "30"
  fromBackup: ""
```

### PVC integration

```yaml
Example — abstract
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: longhorn
  resources:
    requests:
      storage: 10Gi
```

Volumes are block devices — mount as filesystem in the pod; one writer per volume (ReadWriteOnce) is the common homelab pattern.

### Key settings and concepts

- **Replica count** — default 3; each replica consumes real disk space. With 3 replicas, a volume survives the loss of any single replica (disk or node failure); lowering the count reduces durability.
- **Data locality** — `disabled` (replicas spread across nodes) or `best-effort`/`strict-local` to prefer or require a replica on the same node as the workload (lower latency, but loses node-failure protection).
- **Default settings** — replica count, data locality, and backup targets are configured in Longhorn settings; individual volumes can override.

### Longhorn vs local-path tradeoff

| Aspect | Longhorn | local-path |
|---|---|---|
| Durability | Replicated across disks/nodes | Single copy on one node |
| Snapshots/backups | Built-in | None |
| Expansion | Online volume expansion | Manual, painful |
| Overhead | Extra engine/replica processes, disk usage | Near zero |
| Failure domain | Survives node/disk loss | Data lost with node |

## Sources / Further Reading

- [Longhorn volumes and snapshots](https://longhorn.io/docs/1.12.1/nodes-and-volumes/volumes/)
- [Longhorn storage class parameters](https://longhorn.io/docs/1.12.1/references/storage-class-parameters/)
- [Kubernetes storage concepts](./02_Knowledge/technologies/kubernetes/concepts/storage.md)
