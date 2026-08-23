---
title: "k3s networking"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, k3s, networking, firewall, flannel]
sources:
  - url: "https://docs.k3s.io/networking"
    title: "k3s networking"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/services.md"
---

# k3s networking

## Overview

k3s networking is three layers: the cluster API (6443), the pod overlay (flannel VXLAN on 8472/UDP), and the kubelet/control traffic (10250). Bundled traefik fronts services via ingress, and klipper-lb assigns NodePort-range ports to `LoadBalancer` services.

## Details

### Ports

| Port | Protocol | Purpose | Required |
|---|---|---|---|
| 6443 | TCP | Kubernetes API server | Always |
| 8472 | UDP | flannel VXLAN overlay (pod-to-pod) | Always |
| 10250 | TCP | kubelet metrics/API | Always |
| 2379/2380 | TCP | etcd client/peer — HA only | Only with embedded etcd |
| 30000–32767 | TCP | NodePort range (klipper-lb) | Only if using NodePort |

Example — real config (homelab firewall, node-main):

```bash
# ufw on Ubuntu; mirror as networking.firewall rules on NixOS post-migration
sudo ufw allow 6443/tcp      # k3s API
sudo ufw allow 8472/udp      # flannel VXLAN
sudo ufw allow 10250/tcp     # kubelet
# sudo ufw allow 2379/tcp && sudo ufw allow 2380/tcp   # only for HA etcd
```

These are the only three open ports on `node-main` — see `./03_Research/nixos-adoption/overview.md`. The NodePort range stays closed unless a workload explicitly needs NodePort access.

### flannel (CNI)

Default CNI. VXLAN overlay on 8472/UDP; each node gets a `/24` pod CIDR (`10.42.0.0/24`, `10.42.1.0/24`, …) and services run on `10.43.0.0/16`. Cluster traffic stays inside the overlay, so only the three ports above must cross the firewall.

### Traefik (ingress)

Bundled ingress controller with CRDs. Listens on host ports 80/443 and routes by `Ingress`/`IngressRoute` host rules to cluster services. Disable with `--disable=traefik` if another ingress is used.

### klipper-lb (ServiceLB)

Default `LoadBalancer` implementation: for each `LoadBalancer` service it creates a DaemonSet pod that binds the service port on the node IP and forwards to the service ClusterIP. With a single node, `LoadBalancer` services are effectively node-port + host bind — see `./02_Knowledge/technologies/kubernetes/concepts/services.md` for how service types compare.

## Sources / Further Reading

- [k3s networking](https://docs.k3s.io/networking)
- [k3s installation requirements / ports](https://docs.k3s.io/installation/requirements)
- [flannel](https://github.com/flannel-io/flannel)
