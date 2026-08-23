---
title: "Rancher Manager"
status: active
author: "padawont"
date: 2026-08-23
tags: [kubernetes, rancher, multi-cluster, management, helm]
technologies: [rancher, cert-manager, helm, k3s]
related_docs:
  - "./02_Knowledge/technologies/kubernetes/rancher/overview.md"
  - "./02_Knowledge/technologies/kubernetes/rancher/installation.md"
  - "./02_Knowledge/technologies/kubernetes/rancher/architecture.md"
  - "./05_Implementations/node-main/nixos/overview.md"
references:
  online:
    - url: "https://ranchermanager.docs.rancher.com/"
      title: "Rancher Manager documentation"
  repo:
    - "./04_ADRs/26-adopt-nixos-on-node-main.md"
node: node-main
---

# Rancher Manager

## Prerequisites

- k3s cluster on node-main running (`sudo k3s kubectl get nodes` → Ready).
- `rancher.local` resolves to `192.168.111.7` on the node (flake `networking.extraHosts`)
  and on any browser machine (`/etc/hosts`).
- Helm 3 + kubectl available (`KUBECONFIG=/etc/rancher/k3s/k3s.yaml`).

## Deployment

### Pre-deploy checks

- `kubectl get nodes` shows node-main Ready.
- `curl -k https://rancher.local` reachable from the browser machine (after hosts entry).

### Deploy

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 1. namespace + cert-manager (before Rancher)
kubectl create namespace cattle-system
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.21.1/cert-manager.yaml
kubectl -n cert-manager rollout status deploy/cert-manager deploy/cert-manager-webhook --timeout=300s

# 2. Rancher chart (current repo: releases.rancher.com; charts.rancher.io only hosts operators)
helm repo add rancher-releases https://releases.rancher.com/server-charts/stable
helm install rancher rancher-releases/rancher \
  --namespace cattle-system \
  --set hostname=rancher.local \
  --set bootstrapPassword=<STRONG_PASSWORD> \
  --set ingress.tls.source=rancher \
  --set replicas=1
```

### Post-deploy verification

- `kubectl -n cattle-system rollout status deploy/rancher --timeout=540s`.
- `kubectl -n cattle-system get ingress rancher` → HOSTS `rancher.local`, ADDRESS `192.168.111.7`.
- Open `https://rancher.local` in a browser, log in with the `admin` user and the
  `bootstrapPassword`, then set a new admin password.

## Configuration

| Setting | Value |
|---|---|
| hostname | `rancher.local` |
| `ingress.tls.source` | `rancher` (cert-manager self-signed, auto-rotated) |
| replicas | 1 (single-node k3s) |
| TLS | self-signed via cert-manager; browsers warn unless the CA is trusted |

## Operations

- **Status**: `kubectl -n cattle-system get pods`, `kubectl -n cattle-system logs deploy/rancher`.
- **Upgrade**: pin the chart version; `helm upgrade rancher rancher-releases/rancher -n cattle-system -f values.yaml`.
- **Backup**: rancher-backup operator (charts.rancher.io) if Rancher becomes the single
  source of truth for cluster state.
- **Bootstrap secret**: `kubectl get secret --namespace cattle-system bootstrap-secret -o go-template='{{.data.bootstrapPassword|base64decode}}'`.
- **Rollback**: see `./rollback.md`.
