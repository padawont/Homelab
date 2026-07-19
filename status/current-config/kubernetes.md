---
snapshot_date: 2026-07-19
domain: kubernetes
---

# Current Kubernetes Config

Deployed manifests on node-main (node-1):

| File | Resource Type | Namespace | Last Applied | Status |
|---|---|---|---|---|
| `nodes.yaml` | Node resources | — | — | Present |
| `k3s-kubeconfig.yaml` | Secret | kube-system | — | Present |
| `cluster-state.yaml` | ConfigMap | default | — | Present |
| `bookstack.yaml` | Deployment + Service + PVC | bookstack | — | Present |
| `kiwix.yaml` | Deployment + Service + PVC | kiwix | — | Present |
| `kiwix-copy-job.yaml` | Job | kiwix | — | Present |
| `extras.yaml` | Various | — | — | Present |

*Last Applied dates and Status are populated during deployment phase.*
