---
title: "Kubernetes Storage: PV, PVC, StorageClass"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, storage, persistence]
sources:
  - url: "https://kubernetes.io/docs/concepts/storage/persistent-volumes/"
    title: "Kubernetes Persistent Volumes documentation"
  - url: "https://kubernetes.io/docs/concepts/storage/storage-classes/"
    title: "Kubernetes Storage Classes documentation"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/longhorn/overview.md"
  - "./02_Knowledge/technologies/kubernetes/k3s/storage.md"
---

# Kubernetes Storage: PV, PVC, StorageClass

## Overview

Containers are ephemeral, so stateful homelab services (forgejo, databases,
media) need persistent storage. Kubernetes abstracts storage through three
objects: PersistentVolume (PV, the actual disk), PersistentVolumeClaim (PVC,
the request), and StorageClass (the provisioner). Users request storage with a
PVC; the cluster binds it to a PV, either statically or dynamically.

## Details

### PersistentVolumes and Claims

- **PV**: cluster resource representing real storage (hostPath, NFS, block
  device, CSI volume). Independent of any namespace.
- **PVC**: namespaced request for storage (size + access mode). The control
  plane binds a matching PV to the PVC (one-to-one). A PVC remains `Pending`
  until a suitable PV exists.
- Pods reference the PVC by name; the volume is mounted into the container.

### Access modes

| Mode | Meaning |
|---|---|
| `ReadWriteOnce` (RWO) | Single node read-write |
| `ReadOnlyMany` (ROX) | Many nodes read-only |
| `ReadWriteMany` (RWX) | Many nodes read-write |
| `ReadWriteOncePod` (RWOP) | Single Pod read-write (CSI only) |

RWX is required for multi-replica workloads sharing files (e.g. media
libraries); local-path only supports RWO.

### Reclaim policies

- `Retain`: PV keeps data after PVC deletion — manual cleanup required.
- `Delete`: PV (and backing storage) deleted automatically with the PVC.
- `Recycle` (deprecated): basic scrub and re-use.

### StorageClasses and dynamic provisioning

A StorageClass defines a provisioner (e.g. `local-path`, `longhorn`,
`nfs.csi.k8s.io`) and parameters. When a PVC names a StorageClass, the
provisioner creates the PV on demand — no manual PV creation.

Example — abstract:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 10Gi
```

### Homelab notes

- k3s ships the `local-path` provisioner by default — fast, simple host
  storage, but RWO only and tied to one node.
- Longhorn is the alternative block storage for the homelab: replicated,
  RWX-capable, with UI and backups. Details in the linked notes.
- Make `storageClassName` explicit in manifests; don't rely on the default
  class changing between clusters.

## Sources / Further Reading

- Kubernetes docs — Persistent Volumes: https://kubernetes.io/docs/concepts/storage/persistent-volumes/
- Kubernetes docs — Storage Classes: https://kubernetes.io/docs/concepts/storage/storage-classes/
- Kubernetes docs — CSI: https://kubernetes.io/docs/concepts/storage/volumes/#csi
