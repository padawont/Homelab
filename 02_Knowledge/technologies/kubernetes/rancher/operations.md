---
title: "Rancher operations"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, rancher, operations, helm, monitoring]
sources:
  - url: "https://ranchermanager.docs.rancher.com/"
    title: "Rancher Manager documentation"
  - url: "https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/install-upgrade-on-a-kubernetes-cluster/upgrades"
    title: "Upgrading Rancher"
  - url: "https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/helm-charts-in-rancher/"
    title: "Helm charts and apps in Rancher"
  - url: "https://ranchermanager.docs.rancher.com/how-to-guides/advanced-user-guides/monitoring-alerting-guides/enable-monitoring"
    title: "Enable monitoring"
last_audit_date: 2026-08-25
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/configmaps.md"
---

# Rancher operations

## Overview

Day-2 tasks in Rancher: upgrading the Rancher server and managed clusters,
deploying apps from the UI (Helm under the hood), and enabling monitoring and
logging. Most operations are UI-driven or plain Helm/kubectl against the
management cluster. Because apps are Helm releases, understanding Helm values
(and the ConfigMaps holding them — see ./02_Knowledge/technologies/kubernetes/concepts/configmaps.md) helps debugging.

## Details

### Cluster upgrades

- **Rancher server upgrade**: `helm upgrade rancher rancher-stable/rancher -n cattle-system -f values.yaml` after reviewing chart options; rolling, reversible with `helm rollback`. Upgrade cert-manager first if the release notes require it.
- **Managed k3s/RKE2 cluster upgrades**: from the cluster page pick a new Kubernetes version and trigger the upgrade; Rancher rolls nodes (control-plane first, then workers) using the provisioning operator. In a homelab, test on a non-production cluster first.
- **Kubernetes without Rancher**: upgrading the k3s binary underneath an imported cluster is possible, but Rancher's cluster state may drift — prefer Rancher-initiated upgrades for provisioned clusters.

Example — abstract Rancher server upgrade:

```bash
helm repo update rancher-stable
helm upgrade rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname=rancher.local \
  --set ingress.tls.source=rancher
kubectl -n cattle-system rollout status deploy/rancher
```

### App marketplace (Helm charts via UI)

- Rancher ships a catalog of curated charts (Longhorn, Traefik, monitoring, etc.) plus the ability to add custom Helm repositories.
- Installing a chart from the UI creates a Helm release in the target cluster/namespace; the UI shows release state, values, and revision history.
- Charts are grouped as **Apps** in the UI — manage upgrades/rollbacks from the Apps view.
- Custom chart repos: add via Apps & Marketplace → Repositories, pointing at a chartmuseum or OCI registry.

Example — abstract custom chart repo:

```yaml
apiVersion: catalog.cattle.io/v1
kind: ClusterRepo
metadata:
  name: homelab-charts
spec:
  url: https://charts.example.com
```

### Monitoring and logging integrations

- **Monitoring**: enable the built-in monitoring app per cluster → deploys Prometheus + Grafana + Alertmanager. Add ServiceMonitors/PodMonitors for custom scrapes; routes send alerts to receivers (webhook, email, Slack).
- **Logging**: the Rancher logging app collects cluster logs (via Fluent Bit) and ships to Elasticsearch, Loki, or Syslog endpoints.
- Both are Helm apps — enable/disable per cluster and per project from the UI; resource usage is non-trivial, so size for the homelab (small retention, one replica).

### Backup / restore

- The `rancher-backup` operator snapshots the management cluster's CRDs and etcd to S3 or a local PVC; restore recreates the management server state. Make it part of the homelab backup routine.

### Homelab tips

- Keep Rancher and cert-manager upgrades separate; cert-manager first.
- Pin chart versions in a Git repo and use Fleet to apply them declaratively instead of clicking in the UI.
- Monitor the management cluster itself — if it is down, all cluster views are down.
- Use the UI's kubeconfig download for per-user access instead of sharing the admin kubeconfig.

## Sources / Further Reading

- Upgrading Rancher: https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/install-upgrade-on-a-kubernetes-cluster/upgrades
- Helm charts and apps in Rancher: https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/helm-charts-in-rancher/
- Enable monitoring: https://ranchermanager.docs.rancher.com/how-to-guides/advanced-user-guides/monitoring-alerting-guides/enable-monitoring
- Rancher Manager documentation: https://ranchermanager.docs.rancher.com/
