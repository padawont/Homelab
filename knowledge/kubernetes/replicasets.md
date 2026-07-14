---
title: "ReplicaSets"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - workloads
  - replicasets
sources:
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/"
    title: "ReplicaSet — Kubernetes Documentation"
last_audit_date: 2026-06-18
---
# ReplicaSets

## Overview

A ReplicaSet ensures a specified number of pod replicas are running at any given time. It is the mechanism that underpins Deployments — users should rarely create ReplicaSets directly. Deployments manage ReplicaSets and provide declarative updates, rollbacks, and revision history.

## Spec

The ReplicaSet spec contains three key fields. `replicas` sets the desired number of pod copies. `selector` defines label matching rules to identify which pods the ReplicaSet owns — this is immutable after creation. `template` is the pod template that the ReplicaSet instantiates. The `selector.matchLabels` must match the pod template's labels, otherwise the ReplicaSet controller will refuse to create pods. Set-based selectors via `matchExpressions` are also supported for more flexible matching.

## Selector Matching

ReplicaSets use two selector types. Equality-based selectors (`=`, `==`, `!=`) are specified in `matchLabels` and require exact label key-value matches. Set-based selectors (`In`, `NotIn`, `Exists`, `DoesNotExist`) are specified in `matchExpressions` and allow matching against a set of values. The selector becomes immutable once the ReplicaSet is created — if you need to change it, delete and recreate the ReplicaSet.

## Scaling

Scaling a ReplicaSet is done by changing `spec.replicas`, either imperatively with `kubectl scale replicaset <name> --replicas=N` or by editing the resource directly. The ReplicaSet controller watches for spec changes and creates or deletes pods to converge on the desired count. ReplicaSets are also the target of the HorizontalPodAutoscaler (HPA), which adjusts `replicas` automatically based on metrics like CPU or memory utilization.

## Ownership References

ReplicaSets are typically owned by Deployments via `metadata.ownerReferences`. When a Deployment is deleted, its ReplicaSets are garbage collected. When a ReplicaSet is deleted, its pods are garbage collected. This ownership chain is what enables rolling updates and rollbacks in Deployments — each revision corresponds to a ReplicaSet, and the Deployment controller scales old ReplicaSets down and new ones up.

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: example-rs
  labels:
    app: example
spec:
  replicas: 3
  selector:
    matchLabels:
      app: example
  template:
    metadata:
      labels:
        app: example
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
```

## References

- [ReplicaSet — Kubernetes Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)
- [Pods](./pods.md)
- [Deployments](./deployments.md)
