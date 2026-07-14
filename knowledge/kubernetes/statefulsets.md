---
title: "StatefulSets"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - workloads
  - statefulsets
sources:
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/"
    title: "StatefulSets — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# StatefulSets

## Overview
StatefulSets manage stateful applications requiring stable, persistent identities and ordered deployment/scaling. Unlike Deployments, StatefulSets guarantee pod identity persists across rescheduling. Used for databases (PostgreSQL, Cassandra), message queues (Kafka, RabbitMQ), and any workload where pod identity matters.

## Ordinal Index
Each pod gets a stable ordinal index starting from 0 (e.g., `web-0`, `web-1`, `web-2`). The index determines ordering for creation (lowest first), scaling (highest ordinal deleted first), and updates. The pod's hostname is `<statefulset-name>-<ordinal>`.

## Pod Identity
Pods retain their identity across rescheduling: stable storage (via PVC templates), stable network identity (via headless Service), and stable hostname (via ordinal). When a pod is rescheduled, it reattaches to the same PVCs and keeps the same DNS name.

## Headless Service
StatefulSets require a headless Service (`clusterIP: None`). Each pod's DNS name follows: `<pod-name>.<service-name>.<namespace>.svc.cluster.local`. This enables direct pod addressing for clustered applications that need to discover peers.

## PVC Templates
`volumeClaimTemplates` in the StatefulSet spec cause each pod to get its own PVC. When pod `web-0` is created, it also creates `data-web-0` (from the template). On reschedule, the pod reuses the same PVC. This is how state survives pod restarts.

## Update Strategies
Two strategies: `RollingUpdate` (default) updates pods in reverse ordinal order one at a time; `OnDelete` requires manual pod deletion to trigger update. `RollingUpdate` also supports `partition` for canary-style updates (only pods with ordinal >= partition are updated).

## Ordered Pod Management
Two `podManagementPolicy` values: `OrderedReady` (default) creates pods sequentially, waits for each to become Ready; `Parallel` creates all pods simultaneously.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: nginx
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```

## References

- [StatefulSets — Kubernetes Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Pods](./pods.md)
- [Services](./services.md)
- [Storage](./storage.md)
