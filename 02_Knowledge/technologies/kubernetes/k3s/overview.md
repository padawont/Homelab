---
title: "k3s overview"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, k3s, lightweight, rancher]
sources:
  - url: "https://docs.k3s.io/"
    title: "k3s documentation"
last_audit_date: 2026-08-22
related_docs:
  - "./03_Research/nixos-adoption/overview.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/overview.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/architecture.md"
---

# k3s overview

## Overview

k3s is Rancher's (SUSE) lightweight, CNCF-certified Kubernetes distribution. It packages the upstream control plane and runtime into a single binary (less than 100 MB) with a small memory footprint (agent minimum ~512 MB RAM; single-node server minimum 2 cores/2 GB RAM), designed for edge, IoT, and homelab deployments.

For this homelab, k3s runs single-node on `node-main` (currently Ubuntu, being migrated to NixOS) — one server node doing double duty as control plane and workload host. See `./03_Research/nixos-adoption/overview.md` for the migration context.

## Details

### k3s vs upstream Kubernetes

| Aspect | Upstream k8s | k3s |
|---|---|---|
| Distribution | Multiple binaries, kubeadm/kops to assemble | Single binary, one installer command |
| Datastore | etcd required | SQLite by default; etcd optional for HA |
| CNI | Choose and install (Calico, Cilium, …) | flannel bundled and enabled by default |
| Ingress | Choose and install | Traefik bundled (can be disabled) |
| Storage | Choose a provisioner | local-path provisioner bundled (can be disabled) |
| Footprint | ~1 GB+ RAM across components | ~2 GB RAM server / ~512 MB agent, binary < 100 MB |

k3s is API-compatible with upstream k8s — the same manifests, `kubectl`, and tooling work unchanged. The trade-off is a smaller default feature set and opinionated bundled choices, not a different API.

### Why single-node k3s in a homelab

- **One install command** to a working cluster; no kubeadm ceremony.
- **Low resource use** leaves room for workloads on the same host.
- **Bundled components** cover the common homelab stack (ingress, CNI, load balancer, storage) out of the box.
- **Easy migration**: state lives in `/var/lib/rancher/k3s` + `/etc/rancher/k3s`, so the host OS can be replaced (Ubuntu → NixOS) without rebuilding the cluster.
- **Single point of failure is acceptable** for a homelab; if HA is needed later, k3s supports embedded etcd or an external datastore.

Related notes: `./02_Knowledge/technologies/kubernetes/k3s/architecture.md` for how the pieces fit together, `./02_Knowledge/technologies/kubernetes/k3s/installation.md` for the two install paths.

## Sources / Further Reading

- [k3s documentation](https://docs.k3s.io/)
- [k3s architecture](https://docs.k3s.io/architecture)
- ./03_Research/nixos-adoption/overview.md — homelab migration context
