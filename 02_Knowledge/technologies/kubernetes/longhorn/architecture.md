---
title: "Longhorn architecture"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, storage, longhorn, architecture]
sources:
  - url: "https://longhorn.io/docs/1.12.1/concepts/"
    title: "Longhorn architecture and concepts"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/storage.md"
---

# Longhorn architecture

## Overview

Longhorn is split into a control plane that manages volumes and a data path that serves I/O. The control plane is Kubernetes-native (Deployments, DaemonSets, CRDs); the data path is a set of lightweight processes that run as pods on the nodes holding the actual data.

## Details

### Control plane

- **longhorn-manager** — the core controller. Watches Longhorn CRDs (Volume, Replica, Engine, Node, etc.) and reconciles them toward the desired state, much like the Kubernetes controller pattern. Runs as a DaemonSet (one pod per node).
- **longhorn-ui** — web dashboard for managing volumes, snapshots, backups, nodes, and settings. Read-only RBAC-friendly access can be exposed for monitoring.
- **CSI driver** — the CSI plugin (csi-attacher, csi-provisioner, csi-resizer, longhorn-csi-plugin) that makes Longhorn volumes appear as normal PVCs to the Kubernetes scheduler and kubelet.

### Data path

- **longhorn-engine** — the volume engine process. Exposes the block device to the workload and fans writes out to all healthy replicas. One engine per volume, scheduled on the node where the workload pod runs.
- **longhorn-instance-manager** — manages the lifecycle of engine and replica processes on a node (start/stop/monitor). One instance-manager pod per node per engine type.

### Volume / replica model

- A **volume** is a block device made of one **active replica** plus N replica copies. Replicas are stored as sparse files in a dedicated directory on node disks.
- Writes go to the active replica and are replicated synchronously to the others; reads come from the active replica.
- If a replica falls behind or is lost, Longhorn **rebuilds** it in the background by copying the delta from the active replica. Rebuild is transparent to the workload and does not require detaching the volume.

```text
Example — abstract
Workload pod ──> engine (active) ──> replica 1 (node A)
                             └────> replica 2 (node B)  [rebuild from engine if stale]
```

## Sources / Further Reading

- [Longhorn architecture and concepts](https://longhorn.io/docs/1.12.1/concepts/)
- [Kubernetes storage concepts](./02_Knowledge/technologies/kubernetes/concepts/storage.md)
