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
| `longhorn` (Helm) | Storage system | longhorn-system | 2026-07-19 | Present |
| `rancher` (Helm) | Management UI | cattle-system | 2026-07-19 | Present |
| `cert-manager` (Helm) | Certificate controller | cert-manager | 2026-07-19 | Present |
| `metallb` (Helm) | Load balancer | metallb-system | 2026-07-19 | Present |
| `fleet` (Helm) | GitOps controller | cattle-fleet-system | 2026-07-19 | Present |
| `rancher-webhook` (Helm) | Webhook validation | cattle-system | 2026-07-19 | Present |
| `rancher-turtles` (Helm) | Cluster API provider | cattle-turtles-system | 2026-07-19 | Present |
| `system-upgrade-controller` (Helm) | OS upgrade controller | cattle-system | 2026-07-19 | Present |

*Snapshot taken 2026-07-19. Raw manifests verified present in cluster via kubectl. Helm entries verified via `helm list -A`. All NixOS configs match live `/etc/nixos/` files (diff confirmed).*
