---
title: "DaemonSets"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - workloads
  - daemonsets
sources:
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/"
    title: "DaemonSet — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# DaemonSets

## Overview

A DaemonSet ensures all (or some) nodes run a copy of a pod. As nodes are added to the cluster, pods are added to them; as nodes are removed, pods are garbage collected. Deleting a DaemonSet cleans up its pods. Common uses: cluster storage daemons, log collectors, node monitoring, and network proxies.

## Scheduling

DaemonSet pods are scheduled by the DaemonSet controller, not the kube-scheduler. By default, pods run on every node. Use `nodeSelector`, `nodeAffinity`, or tolerations to limit which nodes run the DaemonSet. For example, a DaemonSet with a `nodeSelector` for `node-role.kubernetes.io/control-plane` runs only on control plane nodes.

## Rolling Update Strategy

`RollingUpdate`: `maxSurge` controls the maximum extra DaemonSet pods created during an update; `maxUnavailable` controls the maximum pods unavailable during the update. `OnDelete`: requires manual pod deletion — no automatic rolling update is performed.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      nodeSelector:
        kubernetes.io/os: linux
      containers:
      - name: fluentd
        image: fluentd:latest
```

Cross-links: [Pods](./pods.md), [Nodes](./nodes.md).
