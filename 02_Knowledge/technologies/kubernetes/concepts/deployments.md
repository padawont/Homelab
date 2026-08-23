---
title: "Deployments in Kubernetes"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, workloads, deployments, replicaset, rolling-update]
sources:
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"
    title: "Kubernetes Deployments"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/statefulsets.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/jobs.md"
---

# Deployments in Kubernetes

## Overview

A Deployment manages stateless, identical replicas of a pod. It owns ReplicaSets: each change to the pod template creates a new ReplicaSet, which scales up/down to reach the desired replica count. This is the workload type for most homelab services (web frontends, APIs, workers).

## Details

### Ownership chain

Deployment → ReplicaSet → Pods. The Deployment only manages its template; you never edit ReplicaSets directly. `kubectl rollout status deployment/name` watches the current rollout.

### Update strategies

- **Recreate** — delete all old pods, then create new ones. Simple, but downtime. Use for single-instance jobs or apps that cannot run two copies at once.
- **RollingUpdate** (default) — replace pods gradually; `maxUnavailable` and `maxSurge` control the pace (default 25% each). Use for most services.

### Rollbacks and revision history

Every rollout creates a revision. `kubectl rollout undo deployment/name` reverts to the previous revision; `--to-revision=N` picks a specific one. `revisionHistoryLimit` caps how many old ReplicaSets are kept (default 10). Keep rollback history small on homelab nodes to save resources.

Example — abstract:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27
```

Use StatefulSets when pods need stable identity or persistent storage; use Jobs for batch work that must complete.

## Sources / Further Reading

- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [StatefulSets note](./02_Knowledge/technologies/kubernetes/concepts/statefulsets.md)
- [Jobs note](./02_Knowledge/technologies/kubernetes/concepts/jobs.md)
