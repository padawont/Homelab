---
title: "Rancher Manager"
status: active
author: "padawont"
date: 2026-10-02
tags: [kubernetes, rancher, management, ingress, tls]
technologies: [rancher, cert-manager, helm, traefik, kubernetes]
related_docs:
  - "./04_ADRs/26-adopt-nixos-on-node-main.md"
  - "./02_Knowledge/technologies/kubernetes/rancher/overview.md"
  - "./02_Knowledge/technologies/kubernetes/rancher/installation.md"
  - "./05_Implementations/node-main/k3s/overview.md"
references:
  online:
    - url: "https://ranchermanager.docs.rancher.com/"
      title: "Rancher Manager documentation"
    - url: "https://cert-manager.io/docs/"
      title: "cert-manager documentation"
  repo:
    - "./04_ADRs/26-adopt-nixos-on-node-main.md"
    - "./05_Implementations/node-main/k3s/overview.md"
    - "./rollback.md"
node: node-main
---

# Rancher Manager

Browser-based operations UI and cluster management for the single-node k3s
cluster on `node-main`, served over Traefik at `https://rancher.local`.

## Prerequisites

- Working k3s cluster — see `./05_Implementations/node-main/k3s/overview.md`.
- Helm 3 and `kubectl` on the admin machine.
- Workstation `/etc/hosts` entry mapping `rancher.local` to `192.168.111.7`.
- cert-manager installed **first** (Rancher's webhook depends on it).

## Deployment

### Pre-deploy checks

```bash
kubectl get nodes
kubectl get ingressclass        # traefik must be the default class
helm version
```

### Deploy

1. Install cert-manager **v1.21.1** into the `cert-manager` namespace (before
   Rancher):

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.21.1/cert-manager.yaml
```

2. Install the Rancher chart **2.15.2** into `cattle-system`:

```bash
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo update
kubectl create namespace cattle-system
helm install rancher rancher-stable/rancher \
  --namespace cattle-system \
  --version 2.15.2 \
  --set hostname=rancher.local \
  --set replicas=1 \
  --set ingress.tls.source=rancher
```

A bootstrap password is set at install time and must be changed on first login.
It is **never recorded in this repo**.

### Post-deploy verification

```bash
kubectl -n cert-manager get pods
kubectl -n cattle-system get pods
kubectl -n cattle-system get ingress
kubectl -n cattle-system get certificate tls-rancher-ingress
```

Then open `https://rancher.local` (self-signed cert → browser warning), log in,
and change the bootstrap password.

## Configuration

- Chart: `rancher-stable/rancher` **2.15.2** in namespace `cattle-system`,
  `replicas=1`.
- Hostname `rancher.local`; `ingress.tls.source=rancher`.
- Served through k3s's bundled **Traefik** (IngressClass `traefik` is the default).
- Certificate `tls-rancher-ingress` issued by **cert-manager v1.21.1** (self-signed).
- Workstation `/etc/hosts`:

```
192.168.111.7 rancher.local
```

- Admin credentials: bootstrap password set at install time, changed on first login.

## Operations

```bash
# Status
kubectl -n cattle-system get pods
helm -n cattle-system status rancher

# Logs
kubectl -n cattle-system logs deploy/rancher

# Upgrade (pin the chart version)
helm repo update
helm -n cattle-system upgrade rancher rancher-stable/rancher --version <new>
```

Rollback is documented in `./rollback.md`.
