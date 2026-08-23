---
title: "DaemonSets in Kubernetes"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, workloads, daemonsets, node]
sources:
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/"
    title: "Kubernetes DaemonSets"
last_audit_date: 2026-08-22
related_docs: []
---

# DaemonSets in Kubernetes

## Overview

A DaemonSet ensures exactly one pod runs on every node that matches its selector. Use it for node-level infrastructure: log collectors, monitoring agents, node-exporter metrics, CNI or storage plugins. In a homelab, DaemonSets are how you observe or extend every node uniformly.

## Details

### Scheduling

The DaemonSet controller places a pod on each eligible node as it joins the cluster. New nodes automatically get the pod; removed nodes drop it. Use `nodeSelector`, `affinity`, or `tolerations` to restrict which nodes run the pod (e.g. only storage nodes).

### Update strategy

- **OnDelete** — pods are only replaced when you delete them manually.
- **RollingUpdate** (default) — replaces pods node by node; `maxUnavailable` (default 1) controls how many nodes can be down at once. Keep it at 1 for homelab infra to avoid losing monitoring on many nodes at once.

Example — abstract:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
spec:
  selector:
    matchLabels:
      name: node-exporter
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  template:
    metadata:
      labels:
        name: node-exporter
    spec:
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Exists
          effect: NoSchedule
      containers:
        - name: node-exporter
          image: prom/node-exporter:v1.8.2
          ports:
            - containerPort: 9100
```

## Sources / Further Reading

- [Kubernetes DaemonSets](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)
