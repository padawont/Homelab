---
title: "Rancher Upgrades"
status: draft
author: padawont
date: 2026-07-11
tags:
  - rancher
  - upgrade
  - kubernetes
  - lifecycle
sources:
  - url: "https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/install-upgrade-on-a-kubernetes-cluster/upgrades"
    title: "Rancher — Upgrading the Server"
  - url: "https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/kubernetes-resources-setup/manage-clusters"
    title: "Rancher — Managing Downstream Clusters"
last_audit_date: 2026-07-11
---

# Rancher Upgrades

## Prerequisites

- [Rancher instance](../rancher-install-k3d.md) — installed and running
- [Rancher Architecture](../rancher-architecture.md) — understanding of management vs downstream clusters
- [Kubernetes Fundamentals](../) — K8s concepts (etcd, Pod lifecycle, node management)
- [Kubernetes Storage](../storage.md) — etcd snapshots and PersistentVolume backup
- [Kubernetes Pods](../pods.md) — understanding of pod lifecycle for rollout verification

## Upgrading the Rancher Server

Rancher Server is upgraded via `helm upgrade` on the management cluster.

### Pre-Upgrade Checklist

- [ ] Check [Rancher supported K8s versions](https://rancher.com/support-matrix/) — the management cluster's K8s version must be compatible with the target Rancher version
- [ ] Check cert-manager version compatibility — cert-manager may need upgrading before or after Rancher
- [ ] Review the Rancher [release notes](https://github.com/rancher/rancher/releases) for breaking changes and deprecations
- [ ] Backup the Rancher management cluster's etcd (`k3d etcd-snapshot` or equivalent)
- [ ] Backup `cattle-system` resources: `kubectl get all -n cattle-system -o yaml > rancher-backup.yaml`
- [ ] Record the current Helm values: `helm get values rancher -n cattle-system -o yaml > rancher-values-backup.yaml`

### Upgrade Steps

1. Update the Helm repository:

```bash
helm repo update rancher-stable
```

2. Check the available versions:

```bash
helm search repo rancher-stable/rancher --versions
```

3. Perform the upgrade using the saved values:

```bash
helm upgrade rancher rancher-stable/rancher \
  --namespace cattle-system \
  -f rancher-values-backup.yaml
```

If you need to pass values explicitly:

```bash
helm upgrade rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname=rancher.127.0.0.1.nip.io \
  --set replicas=1 \
  --set ingress.tls.source=rancher
```

4. Wait for the rollout to complete:

```bash
kubectl -n cattle-system rollout status deploy/rancher --timeout=300s
```

5. Verify the new version:

```bash
kubectl -n cattle-system get deploy rancher -o jsonpath='{.spec.template.spec.containers[0].image}'
```

### Post-Upgrade Validation

- [ ] All `cattle-system` pods in `Running` state
- [ ] Downstream clusters show "Active" in the Rancher UI
- [ ] `cattle-cluster-agent` logs clean on downstream clusters
- [ ] Existing workloads accessible and functional
- [ ] Fleet GitRepo bundles syncing correctly

## Upgrading Downstream Clusters

### Rancher-Provisioned Clusters

For clusters provisioned by Rancher (via RKE2 or K3s node drivers):

1. Navigate to cluster → **⋮** → **Edit Config**
2. Select the target Kubernetes version from the dropdown
3. Configure upgrade strategy:
   - `maxUnavailable` — how many nodes can be down simultaneously
   - `drain` — whether to drain nodes before upgrading (recommended for stateful workloads)
4. Click **Save**

Rancher uses node-by-node rolling upgrades:
1. Cordon the node (mark unschedulable)
2. Drain pods (respecting PDBs)
3. Replace node with new K8s version
4. Uncordon

### Imported Clusters

Imported clusters must be upgraded independently of Rancher. Rancher does not manage the node lifecycle for imported clusters. After the cluster is upgraded:

- The `cattle-cluster-agent` should automatically reconnect
- If agent connectivity is lost, re-import the cluster using a fresh registration token

## Rollback

### Server Rollback

```bash
helm history rancher -n cattle-system
helm rollback rancher <revision-number> -n cattle-system
```

After rollback, verify the same post-upgrade validation steps.

### Downstream Cluster Rollback

Rollback of downstream clusters is only possible if an etcd snapshot was taken before the upgrade:

1. Restore the downstream cluster from etcd snapshot
2. Re-register the cluster with Rancher (use a new registration token from the UI)
3. The `cattle-cluster-agent` will reconnect using the new token

Node pool version changes are not directly reversible — you must edit the cluster config to set the previous K8s version and let Rancher reprovision nodes.

## References

- [Rancher — Upgrading the Server](https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/install-upgrade-on-a-kubernetes-cluster/upgrades)
- [Rancher — Managing Downstream Clusters](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/kubernetes-resources-setup/manage-clusters)
- [Rancher Release Notes](https://github.com/rancher/rancher/releases)
- [Rancher Support Matrix](https://rancher.com/support-matrix/)
