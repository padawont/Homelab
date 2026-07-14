---
title: "k3d Volume Mounts"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k3d
  - volumes
  - kubernetes
  - storage
sources:
  - url: "https://k3d.io/v5.6.0/design/defaults/"
    title: "k3d — Defaults"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_cluster_create/"
    title: "k3d cluster create command (volume flags)"
  - url: "https://k3d.io/v5.6.0/usage/k3s/"
    title: "k3d — K3s Features (local-path-provisioner)"
last_audit_date: 2026-07-10
---

# k3d Volume Mounts

Volume mounts in k3d map directories from the **host machine** into the **k3s node containers**. These are Docker volume mounts on the container level — they are distinct from Kubernetes volumes (PVCs, ConfigMaps, Secrets).

## Syntax

```
[SOURCE:]DEST[@NODEFILTER[;NODEFILTER...]]
```

## Examples

```bash
# Mount host directory into all nodes
k3d cluster create mycluster -v /tmp/k3dvol:/data@all

# Mount into a specific server node
k3d cluster create mycluster -v /tmp/k3dvol:/data@server:0

# Mount into specific agent nodes
k3d cluster create mycluster -v /my/path@agent:0,1 --agents 2

# Multiple mounts
k3d cluster create mycluster \
  -v /tmp/data:/data@server:0 \
  -v /tmp/config:/etc/myapp-config@agent:*
```

## Read-Only Mounts

Append `:ro` to make the mount read-only inside the node:

```bash
k3d cluster create mycluster -v /tmp/config:/etc/config:ro@all
```

## Volume Mounts in Config File

```yaml
volumes:
  - volume: /my/host/path:/path/in/node
    nodeFilters:
      - server:0
      - agent:*
```

## Use Cases

### Persistent Data

Mount a host directory into the node's local storage paths used by k3s' local-path-provisioner:

```bash
k3d cluster create mycluster \
  -v /tmp/k3d-storage:/var/lib/rancher/k3s/storage@all
```

This makes data written to PVCs using the default `local-path` StorageClass persist on the host, surviving node restarts.

### Config Injection

Inject configuration files into k3s manifests directory to override built-in components:

```bash
k3d cluster create mycluster \
  -v ./custom-coredns.yaml:/var/lib/rancher/k3s/server/manifests/coredns.yaml@server:0
```

### Application Data

Mount application data that needs to be accessed via `hostPath` volumes in pods:

```bash
k3d cluster create mycluster -v /data/myapp:/mnt/data@all
```

Then reference in a pod:

```yaml
spec:
  containers:
    - volumeMounts:
        - name: data
          mountPath: /app/data
  volumes:
    - name: data
      hostPath:
        path: /mnt/data
```

## Important Distinction: Node Mounts vs Kubernetes Volumes

| Aspect | k3d Volume Mount | Kubernetes hostPath / PVC |
|---|---|---|
| Level | Docker container (k3s node) | Kubernetes Pod |
| Configuration | `k3d cluster create -v ...` | Pod/Deployment YAML spec |
| Persistence | Survives cluster stop/start | Depends on PV reclaim policy |
| Scope | Available via `hostPath` in pods | Direct pod-level |

k3d volume mounts expose paths inside the node containers, which can then be referenced by pods using `hostPath` volumes. They are a prerequisite for persistent storage in k3d, not a replacement for Kubernetes storage primitives (see [storage fundamentals](../storage.md)).

## Node-Level Mount Characteristics

- Each mount targets specific nodes via node filters
- Multi-node clusters can have different mounts per node
- Mounts survive `k3d cluster stop` / `k3d cluster start` (the Docker volumes persist)
- Mounts are removed when the cluster is deleted
