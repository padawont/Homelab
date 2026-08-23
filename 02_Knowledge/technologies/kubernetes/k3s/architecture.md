---
title: "k3s architecture"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, k3s, architecture, etcd]
sources:
  - url: "https://docs.k3s.io/architecture"
    title: "k3s architecture"
  - url: "https://docs.k3s.io/datastore"
    title: "k3s datastore options"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/rancher/overview.md"
---

# k3s architecture

## Overview

k3s splits nodes into **servers** (control plane) and **agents** (workers). One binary runs both roles — the role is chosen at install/join time. All control-plane components are embedded in a single process, and the cluster datastore is SQLite by default instead of etcd.

## Details

### Server vs agent

- **Server**: runs the k8s control plane (API server, scheduler, controller manager) plus bundled extras (traefik, ServiceLB, local-path, metrics-server, CoreDNS, flannel). A server can also run workloads.
- **Agent**: runs kubelet, kube-proxy, and flannel, and joins the control plane over `https://<server>:6443`.

In a single-node homelab, `node-main` is a server and there are no agents — the server is also the only worker. Adding capacity means joining agents with the server's token.

Example — abstract:

```
server (node-main):  API 6443, scheduler, controller-manager, datastore, bundled add-ons
                        │  https://server:6443 + token
agent (node-2):      kubelet, kube-proxy, flannel
```

### Single binary

The k3s binary is a wrapper that launches all control-plane processes as child processes of one PID: kube-apiserver, kube-scheduler, kube-controller-manager, kubelet, containerd, and the embedded components. This is why `k3s kubectl`, `k3s crictl`, and `k3s etcdctl` work without extra installs.

### Datastore: SQLite vs embedded etcd

| Mode | Datastore | Use case |
|---|---|---|
| Single node (default) | SQLite in `/var/lib/rancher/k3s/server/db/` | Homelab single-server |
| HA (embedded etcd) | etcd, 3+ servers | High availability, ports 2379/2380 open |
| HA (external) | External etcd/MySQL/PostgreSQL | Managed datastore |

The single-node default avoids etcd's resource cost entirely. HA requires at least three servers so etcd can form a quorum.

### Bundled components

| Component | Role | Flag |
|---|---|---|
| Traefik | Ingress controller (with CRDs) | `--disable=traefik` |
| flannel | CNI, VXLAN overlay | `--flannel-backend=none` |
| klipper-lb (ServiceLB) | LoadBalancer via host ports | `--disable=servicelb` |
| local-path provisioner | Dynamic PVs on host disk | `--disable=local-storage` |
| CoreDNS | Cluster DNS | `--disable=coredns` |
| metrics-server | Resource metrics API | `--disable=metrics-server` |
| kube-router | Network policy controller | `--disable-network-policy` |
| Spegel | Distributed registry mirror (off by default) | `--embedded-registry` (enable) |

Most flags in this column disable the bundled component. Spegel is the exception: it is off by default, and `--embedded-registry` is an **enable** flag that turns on the distributed registry mirror (see [Embedded Registry Mirror](https://docs.k3s.io/installation/registry-mirror)).

See `./02_Knowledge/technologies/kubernetes/rancher/overview.md` for the Rancher ecosystem context. The bundles are covered in their own notes: `./02_Knowledge/technologies/kubernetes/k3s/networking.md` (flannel, traefik, klipper-lb) and `./02_Knowledge/technologies/kubernetes/k3s/storage.md` (local-path).

## Sources / Further Reading

- [k3s architecture](https://docs.k3s.io/architecture)
- [k3s datastore options](https://docs.k3s.io/datastore)
- [k3s server config reference](https://docs.k3s.io/cli/server)
