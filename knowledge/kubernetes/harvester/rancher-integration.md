---
title: "Harvester Rancher Integration"
status: draft
date: 2026-07-28
author: padawont
tags:
  - harvester
  - rancher
  - virtualization-management
  - integration
  - csi-driver
  - node-driver
sources:
  - url: "https://docs.harvesterhci.io/v1.8/rancher"
    title: "Harvester Rancher Integration"
  - url: "https://docs.harvesterhci.io/v1.8/rancher/virtualization-management"
    title: "Virtualization Management"
  - url: "https://docs.harvesterhci.io/v1.8/rancher/node-driver"
    title: "Harvester Node Driver"
  - url: "https://docs.harvesterhci.io/v1.8/rancher/csi-driver"
    title: "Harvester CSI Driver"
last_audit_date: 2026-07-28
related_configs:
  - "configs-and-adr/node-main/vm/"
  - "configs-and-adr/adr/0003-harvester-vm-platform.md"
---

# Harvester Rancher Integration

## Overview

Harvester integrates natively with Rancher through several mechanisms. In the homelab, Rancher runs on the existing K3s cluster (node-1's management cluster), and Harvester is imported into Rancher's Virtualization Management feature.

## Virtualization Management

Rancher Virtualization Management provides a unified UI for managing Harvester clusters alongside Kubernetes clusters. From a single Rancher dashboard, operators can:

- View and manage VMs across all Harvester clusters
- Monitor host status and resource utilization
- Access the Harvester UI for detailed operations
- Create and manage Kubernetes clusters provisioned on Harvester VMs

### Importing Harvester into Rancher

The import process registers the Harvester cluster as a downstream cluster in Rancher:

1. In Rancher, navigate to **Virtualization Management > Clusters**
2. Click **Import Existing**
3. Give the cluster a name (e.g., `harvester`)
4. Rancher generates an import YAML manifest
5. Apply the manifest to the Harvester cluster:

```bash
kubectl apply -f rancher-import.yaml
```

6. The Harvester cluster appears in Rancher's cluster list and Virtualization Management view

After import, the Harvester UI is accessible from within Rancher as an embedded view. VM operations (start, stop, console, backup, restore) are available directly from Rancher.

### Authentication

When integrated with Rancher, Harvester uses Rancher's authentication provider. Users authenticated through Rancher (local, LDAP, OIDC, SAML, etc.) can access Harvester resources based on their Rancher permissions. This eliminates the need for separate Harvester user management.

## Harvester Node Driver

The Harvester node driver allows Rancher to provision new Kubernetes clusters on VMs running on Harvester. This is different from importing Harvester itself — the node driver uses Harvester as an infrastructure provider for downstream K8s clusters.

### How It Works

1. Rancher communicates with the Harvester API to create VMs
2. Each VM becomes a node in the downstream K8s cluster
3. Rancher installs RKE2 or K3s on the VMs via cloud-init
4. The Harvester CSI driver is optionally installed to provide persistent storage

### Prerequisites

- Harvester cluster imported into Rancher Virtualization Management
- Harvester cloud provider configured (for LoadBalancer services in the downstream cluster)
- Sufficient resources on Harvester (CPU, RAM, storage)

### Lab Context

The homelab does not use the Harvester node driver since Rancher already runs on an existing K3s cluster. The node driver would be relevant if additional guest K8s clusters were needed within Harvester VMs.

## Harvester CSI Driver v0.1.28

The Harvester CSI Driver (v0.1.28) allows downstream Kubernetes clusters running on Harvester VMs to provision persistent storage from Harvester's Longhorn backend. It treats Harvester as a storage provider.

### Features

| Feature | v0.1.28 Support | Notes |
|---|---|---|
| Dynamic volume provisioning | Yes | PVCs create volumes on Harvester |
| Storage tiering | Yes | Different StorageClasses for SSD/HDD |
| ReadWriteMany (RWX) | Yes | Shared volumes across multiple pods |
| Online volume resizing | Yes | Expand volumes without downtime |
| Volume snapshots | Yes | Via VolumeSnapshot API |
| Volume cloning | Yes | From snapshot or existing volume |

### Installation

The CSI driver is installed as a Helm chart:

```bash
helm repo add harvester https://harvester.github.io/harvester-csi-driver
helm install harvester-csi harvester/harvester-csi-driver \
  --namespace harvester-system \
  --kubeconfig <downstream-kubeconfig>
```

### StorageClasses

Once installed, the driver creates StorageClasses that reference Harvester's backing storage:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: harvester-csi
provisioner: csi.harvester.io
parameters:
  storageClassName: harvester-longhorn      # Target Harvester StorageClass
  dataLocality: disabled
  numberOfReplicas: "1"                      # Single replica for single-node
allowVolumeExpansion: true
```

## Harvester Cloud Provider (CCM)

The Harvester Cloud Controller Manager (CCM) integrates Harvester with Kubernetes cloud provider functionality:

- **LoadBalancer services** — Provisions a LoadBalancer IP from a Harvester IP pool for Services in the downstream cluster
- **Node controller** — Manages node lifecycle (add/remove) in the downstream cluster
- **Route controller** — Updates pod CIDR routes (if VPC networking is enabled)

### LoadBalancer Implementation

When a downstream K8s cluster requests a LoadBalancer service, the Harvester CCM:

1. Detects the LoadBalancer service creation
2. Allocates an IP from the configured IP pool (see [networking.md](networking.md))
3. Creates an iptables rule on the Harvester node to forward traffic to the VM
4. Updates the Service's `status.loadBalancer.ingress` with the allocated IP

### Installation

```bash
# Install Harvester cloud provider in the downstream cluster
kubectl apply -f https://raw.githubusercontent.com/harvester/cloud-provider-harvester/master/deploy/manifest.yaml
```

Configure the cloud provider via ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: harvester-cloud-provider
  namespace: kube-system
data:
  harvester-cloud-provider.yaml: |
    global:
      clusterName: "my-cluster"
      clusterID: "my-cluster-id"
    harvesterCredentialSecret: "harvester-credentials"
    harvesterKubeconfigSecret: "harvester-kubeconfig"
```

## Integration Summary

| Integration | Used in Lab | Purpose |
|---|---|---|
| Virtualization Management | Yes | Manage Harvester VMs from Rancher UI |
| Node Driver | No | Provision K8s clusters on Harvester VMs |
| CSI Driver | Conditional | Storage for downstream K8s clusters |
| Cloud Provider / CCM | Conditional | LoadBalancer for downstream K8s clusters |

In the homelab, Rancher runs on the existing K3s cluster (node-1's management cluster). Harvester is imported into Virtualization Management for unified VM management. The CSI driver and cloud provider are not currently needed since there are no downstream K8s clusters running on Harvester VMs.

## References

- [Harvester Rancher Integration](https://docs.harvesterhci.io/v1.8/rancher)
- [Virtualization Management](https://docs.harvesterhci.io/v1.8/rancher/virtualization-management)
- [Harvester Node Driver](https://docs.harvesterhci.io/v1.8/rancher/node-driver)
- [Harvester CSI Driver](https://docs.harvesterhci.io/v1.8/rancher/csi-driver)
- [Harvester Cloud Provider](https://github.com/harvester/cloud-provider-harvester)
