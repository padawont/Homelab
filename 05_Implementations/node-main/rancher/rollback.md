---
title: "Rancher Manager — rollback"
status: active
author: "padawont"
date: 2026-08-23
tags: [kubernetes, rancher, rollback]
technologies: [rancher, helm]
related_docs:
  - "./overview.md"
references:
  online:
    - url: "https://ranchermanager.docs.rancher.com/"
      title: "Rancher Manager documentation"
  repo: []
node: node-main
---

# Rancher Manager — Rollback

## Prerequisites

- Working k3s cluster and `KUBECONFIG=/etc/rancher/k3s/k3s.yaml`.
- The chart version currently installed (`helm list -n cattle-system`).

## Rollback steps

1. **Helm rollback** to a previous chart revision:

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
helm history rancher -n cattle-system
helm rollback rancher <revision> -n cattle-system
kubectl -n cattle-system rollout status deploy/rancher --timeout=540s
```

2. **Full removal** (destructive — loses Rancher-managed cluster state):

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
helm uninstall rancher -n cattle-system
kubectl delete namespace cattle-system
```

3. **Reinstall clean**: follow `./overview.md` (namespace + cert-manager + chart).

## Verification

- `kubectl -n cattle-system get pods` shows the `rancher-*` pod `1/1 Running`.
- `curl -sk https://rancher.local/v3` returns HTTP 401 (API up, requires auth).
