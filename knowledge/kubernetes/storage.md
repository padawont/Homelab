---
title: "PersistentVolumes, PersistentVolumeClaims, and StorageClasses (PV/PVC/SC)"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - storage
  - persistent-volumes
sources:
  - url: "https://kubernetes.io/docs/concepts/storage/persistent-volumes/"
    title: "Persistent Volumes — Kubernetes Documentation"
  - url: "https://kubernetes.io/docs/concepts/storage/storage-classes/"
    title: "Storage Classes — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# PersistentVolumes, PersistentVolumeClaims, and StorageClasses (PV/PVC/SC)

## Overview
Storage management in Kubernetes is decoupled into three layers: PersistentVolumes (PV) are cluster storage resources provisioned by an administrator, PersistentVolumeClaims (PVC) are requests for storage by a user, and StorageClasses (SC) enable dynamic provisioning. Pods consume storage via PVCs mounted as volumes.

## PV Lifecycle
Five-phase lifecycle: Provision (static by admin or dynamic via StorageClass) → Bind (PVC matched to PV) → Use (pod mounts the PVC) → Release (PVC deleted, PV released) → Reclaim (PV recycled, deleted, or retained).

## Access Modes
Access modes describe how a volume can be mounted: `ReadWriteOnce` (RWO, single node read-write), `ReadOnlyMany` (ROX, many nodes read-only), `ReadWriteMany` (RWX, many nodes read-write), `ReadWriteOncePod` (RWOP, single pod read-write). Not all access modes are supported by all storage backends.

## Reclaim Policies
When a PVC is deleted, the PV's reclaim policy determines what happens: `Retain` (admin must manually reclaim), `Delete` (PV and backing storage are deleted), `Recycle` (basic scrub, then available again — deprecated).

## StorageClass and Dynamic Provisioning
StorageClasses define a provisioner and parameters for dynamic PV creation. When a PVC requests a StorageClass, the provisioner automatically creates the PV. Example:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: fast
```

Cross-links: [Pods](./pods.md) (volume mounts), [StatefulSets](./statefulsets.md) (volumeClaimTemplates).
