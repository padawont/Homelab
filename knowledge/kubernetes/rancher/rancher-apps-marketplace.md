---
title: "Rancher Apps and Marketplace"
status: draft
author: padawont
date: 2026-07-11
tags:
  - rancher
  - helm
  - marketplace
  - apps
  - catalogs
sources:
  - url: "https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/helm-charts-in-rancher"
    title: "Rancher — Helm Charts and Apps"
  - url: "https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/helm-charts-in-rancher/create-apps"
    title: "Rancher — Creating Apps"
last_audit_date: 2026-07-11
---

# Rancher Apps and Marketplace

## Prerequisites

- [Rancher instance](../rancher-install-k3d.md) — running and accessible
- [Kubernetes Fundamentals](../) — K8s concepts (Deployments, Services, Ingress, Helm)
- [Helm Fundamentals](../deployments.md) — understanding of charts, values, releases, repositories
- [Kubernetes Ingress](../ingress.md) — for understanding how deployed apps are exposed

## Overview

Rancher's App Marketplace is a graphical Helm chart management interface. It wraps the `helm` CLI with a UI layer that provides catalog browsing, version selection, values editing with schema validation, and multi-cluster deployment orchestration.

## Default Catalogs

Rancher ships with several built-in catalog sources:

| Catalog | Source | Contents |
|---|---|---|
| **Rancher Partner Charts** | [partner-charts](https://github.com/rancher/partner-charts) | Certified partner applications (Grafana, Prometheus, Elastic, Datadog, etc.) |
| **Rancher Stable** | [rancher-stable](https://github.com/rancher/charts) | First-party Rancher extensions (Monitoring, Logging, Istio, Longhorn) |
| **Rancher Prime** | Private | Commercial Rancher Prime catalog (requires license) |

## Installing an App

From the Rancher UI:

1. Navigate to the target cluster → **Apps** → **Charts**
2. Browse or search for the desired chart
3. Select a version from the version dropdown
4. Configure the values YAML (the UI provides schema-validated form fields)
5. Click **Install**

Under the hood, Rancher runs `helm template` with the provided values then applies the result with `kubectl apply`. The release is tracked as a `helmrelease` resource.

### Example: Deploying an nginx Ingress Controller

1. Navigate to cluster → **Apps** → **Charts**
2. Search for `nginx-ingress`
3. Select version, configure values (replica count, service type, resource limits)
4. Install into `ingress-nginx` namespace

The equivalent Helm command:

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.replicaCount=2
```

## Custom Catalogs

You can add private Helm repositories as custom catalogs:

1. Navigate to cluster → **Apps** → **Repositories** → **Create**
2. Set a name and the repository URL
3. Optionally configure authentication (HTTP basic auth, OCI credentials, SSH key for Git-based repos)

Supported repository types:

| Type | URL format | Auth support |
|---|---|---|
| HTTP Helm repo | `https://charts.example.com` | Basic auth, token |
| OCI registry | `oci://registry.example.com/charts` | Docker config |
| Git repo | `https://github.com/org/charts` | SSH key, token |
| S3/GCS bucket | `s3://my-bucket/charts` | IAM role, access key |

## Multi-Cluster Apps

Rancher supports installing a chart across multiple downstream clusters with different values per cluster. This is done via the **Multi-Cluster Apps** feature (available in the upstream management view):

1. Navigate to **☰** → **Multi-Cluster Apps**
2. Select targets (individual clusters or cluster groups)
3. Set a default values YAML
4. Override values per target cluster as needed

This is useful for deploying common infrastructure (monitoring agents, service mesh sidecars, logging forwarders) across all clusters with per-cluster configuration.

Limitations:
- Stateful charts (databases, message queues) are difficult to manage with multi-cluster apps because each instance is independent
- Secret and ConfigMap values must be replicated or injected per cluster

## App Lifecycle

| Action | UI Path | Notes |
|---|---|---|
| **Upgrade** | Cluster → Apps → Installed Apps → ⋮ → Edit/Upgrade | Shows a diff view between current and new values |
| **Rollback** | Cluster → Apps → Installed Apps → ⋮ → Revision History | Select a previous revision to roll back to |
| **Delete** | Cluster → Apps → Installed Apps → ⋮ → Delete | Removes the Helm release and all created resources |

The revision history shows all past versions with timestamps, user who triggered each change, and the values used.

## Differences from the `helm` CLI

| Aspect | Rancher UI | `helm` CLI |
|---|---|---|
| **Values editing** | Schema-validated form editor with autocomplete | Raw YAML/values file |
| **Diff view** | Side-by-side YAML diff before upgrade | `helm diff` plugin required |
| **Multi-cluster** | Built-in via Multi-Cluster Apps | Must manage each cluster separately |
| **RBAC gating** | Rancher RBAC controls who can install which charts | No chart-level authorization |
| **Catalog browsing** | Graphical with search, filter, version history | `helm search repo` |
| **Underlying engine** | `helm template` + `kubectl apply` (managed) | `helm install` (direct) |

Despite these differences, Rancher apps are regular Helm releases underneath — you can inspect them with `helm list -n <namespace>` on the downstream cluster.

## References

- [Rancher Helm Charts and Apps](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/helm-charts-in-rancher)
- [Rancher Creating Apps](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/helm-charts-in-rancher/create-apps)
- [Adding Custom Helm Repositories in Rancher](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/helm-charts-in-rancher#manage-repos)
