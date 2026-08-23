---
title: "Longhorn overview"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, storage, longhorn, block-storage]
sources:
  - url: "https://longhorn.io/docs/1.12.1/what-is-longhorn/"
    title: "Longhorn — What is Longhorn"
  - url: "https://longhorn.io/docs/1.12.1/"
    title: "Longhorn documentation"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/storage.md"
  - "./02_Knowledge/technologies/kubernetes/k3s/storage.md"
---

# Longhorn overview

## Overview

Longhorn is a CNCF incubating distributed block storage system for Kubernetes. It runs entirely inside the cluster: each node's local disks are pooled and exposed as replicated volumes through a CSI driver, with no external SAN or network storage required.

**Status in this homelab: not yet deployed** — under evaluation as a future multi-node storage option; the cluster currently uses k3s local-path.

Why a homelab would use it:

- **Replicated local storage** — data is synchronously mirrored across node disks (default 3 replicas), surviving single-node disk failures without an external NAS.
- **No extra hardware or services** — storage lives on the disks already in the cluster; no iSCSI target, NFS server, or SAN to operate.
- **Built-in snapshots and backups** — volume snapshots plus scheduled backups to S3, NFS, or SMB out of the box.
- **Kubernetes-native** — volumes are ordinary PVCs consumed through a StorageClass; pods and workloads need no special handling.

When to prefer Longhorn over `local-path`:

- You need data durability across node or disk failure (replicas).
- You need snapshots, backup/restore, or volume expansion.
- You run a multi-node cluster and want to schedule replicas across nodes.

When `local-path` is enough:

- Single-node clusters, or workloads that can tolerate data loss (caches, scratch, rebuildable state).
- You want zero storage-layer overhead and host-path simplicity.

## Details

Longhorn in one sentence: it turns ordinary node disks into a software-defined storage pool and exposes replicated block devices as Kubernetes PersistentVolumes. The control plane (longhorn-manager) and data path (engine/replica processes) both run as pods on the cluster nodes, so capacity scales by adding nodes or disks — no separate storage cluster to administer.

Typical homelab topology (3 nodes, default settings):

```text
Example — abstract
Node A ── replica 1 (volume engine)
Node B ── replica 2 (sync copy)
Node C ── replica 3 (if replica count = 3)
```

The engine on the node where a workload runs presents the volume; the replica processes on other nodes hold synchronous copies. If one replica becomes unavailable, the remaining replicas keep serving the volume with no downtime.

## Sources / Further Reading

- [What is Longhorn](https://longhorn.io/docs/1.12.1/what-is-longhorn/)
- [Longhorn documentation](https://longhorn.io/docs/1.12.1/)
- [Kubernetes storage concepts](./02_Knowledge/technologies/kubernetes/concepts/storage.md)
- [Storage on k3s](./02_Knowledge/technologies/kubernetes/k3s/storage.md)
