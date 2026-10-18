---
title: "Rancher Manager — Rollback"
status: active
author: "padawont"
date: 2026-10-02
tags: [kubernetes, rancher, rollback, teardown]
technologies: [rancher, cert-manager, helm, kubernetes]
related_docs:
  - "./overview.md"
  - "./05_Implementations/node-main/k3s/overview.md"
references:
  online:
    - url: "https://ranchermanager.docs.rancher.com/"
      title: "Rancher Manager documentation"
  repo:
    - "./overview.md"
node: node-main
---

# Rancher Manager — Rollback

Remove Rancher Manager, its namespace, and the cert-manager it depends on.

## Prerequisites

- Helm 3 and `kubectl` pointed at the cluster.
- The cert-manager manifest URL/path used at install, for removal.
- Acknowledgement that deleting `cattle-system` removes Rancher's configuration.

## Rollback steps

1. Uninstall the Rancher release:

```bash
helm uninstall rancher -n cattle-system
```

2. Delete the namespace:

```bash
kubectl delete namespace cattle-system
```

3. Remove cert-manager:

```bash
kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.21.1/cert-manager.yaml
```

4. Remove the workstation `/etc/hosts` entry for `rancher.local`:

```
192.168.111.7 rancher.local
```

## Verification

```bash
kubectl get ns cattle-system cert-manager   # not found
helm list -n cattle-system                   # empty
```

`https://rancher.local` no longer serves the Rancher UI.
