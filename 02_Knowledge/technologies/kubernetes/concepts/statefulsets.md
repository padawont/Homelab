---
title: "StatefulSets in Kubernetes"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, workloads, statefulsets, storage, headless-service]
sources:
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/"
    title: "Kubernetes StatefulSets"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/pods.md"
---

# StatefulSets in Kubernetes

## Overview

A StatefulSet manages pods that need stable identity and stable storage: databases, message brokers, anything where "which pod am I and what data do I own" matters. Unlike Deployments, each pod gets a deterministic name, ordinal index, and its own PersistentVolumeClaim.

## Details

### Ordinal identity

Pods are named `{statefulset-name}-{ordinal}` starting at 0 (`db-0`, `db-1`, ...). The name is stable across reschedules — a replacement pod reuses the ordinal. Use the ordinal for sharding decisions and replica roles (e.g. `db-0` is primary).

### Headless Services

A headless Service (`clusterIP: None`) publishes DNS records per pod instead of one ClusterIP. Each pod resolves as `{pod-name}.{headless-service}.{namespace}.svc.cluster.local`, letting clients and peers address individual pods.

### PVC templates

`volumeClaimTemplates` generates one PVC per replica, named `{pvc-name}-{statefulset-name}-{ordinal}`. Deleting a StatefulSet does not delete the PVCs — data survives by design; delete PVCs deliberately.

### Ordered pod management

By default pods are created and terminated one at a time in ordinal order: `0, 1, 2` on scale-up and `2, 1, 0` on scale-down. Set `podManagementPolicy: Parallel` to skip ordering when replicas do not depend on each other.

Example — abstract:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db
spec:
  serviceName: db
  replicas: 3
  podManagementPolicy: OrderedReady
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
        - name: db
          image: postgres:16
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
```

## Sources / Further Reading

- [Kubernetes StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Pods note](./02_Knowledge/technologies/kubernetes/concepts/pods.md)
