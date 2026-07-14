---
title: "Deployments"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - workloads
  - deployments
sources:
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"
    title: "Deployments — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# Deployments

## Overview
A Deployment provides declarative updates for Pods and ReplicaSets. It manages the rollout of changes, tracks revision history, and supports rollbacks. This is the primary workload controller for stateless applications.

## Strategy Types
Two strategies: `Recreate` (kills all existing pods before creating new ones — causes downtime, used when simultaneous pod versions cannot coexist) and `RollingUpdate` (default — gradually replaces old pods with new ones, maintaining availability).

## Rolling Update Parameters
`maxSurge` (max pods above desired count during update, can be absolute or percentage, default 25%), `maxUnavailable` (max pods unavailable during update, default 25%).

## Rollout Status
`kubectl rollout status deployment/<name>` shows progress. `kubectl rollout history deployment/<name>` shows revision history.

## Rollback
`kubectl rollout undo deployment/<name>` rolls back to the previous revision. `--to-revision=N` targets a specific revision. Rollbacks are implemented by scaling up the old ReplicaSet and scaling down the new one.

## Paused Deployments
Setting `spec.paused: true` suspends a rollout. Changes made while paused are batched and applied when unpaused.

## Deployment Conditions
The deployment controller updates status conditions: `Available` (pods are ready), `Progressing` (rollout in progress), `ReplicaFailure` (ReplicaSet issues).

## Example: RollingUpdate Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
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
```

## Related
- [Pods](./pods.md)
- [ReplicaSets](./replicasets.md)
