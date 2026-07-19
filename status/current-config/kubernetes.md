---
snapshot_date: 2026-07-19
domain: kubernetes
---

# Current Kubernetes Config

Deployed manifests on node-main (node-1):

| File | Resource Type | Namespace | Last Applied | Status |
|---|---|---|---|---|
| `nodes.yaml` | Node resources | — | 2026-07-19 | Present |
| `k3s-kubeconfig.yaml` | Secret | kube-system | 2026-07-19 | Present |
| `cluster-state.yaml` | ConfigMap | default | 2026-07-19 | Present |
| `bookstack.yaml` | Deployment + Service + PVC | bookstack | 2026-07-19 | Present |
| `kiwix.yaml` | Deployment + Service + PVC | kiwix | 2026-07-19 | Present |
| `kiwix-copy-job.yaml` | Job | kiwix | 2026-07-19 | Present |
| `extras.yaml` | Various | — | 2026-07-19 | Present |

*Snapshot taken 2026-07-19. All manifests verified present on cluster via kubectl.*
