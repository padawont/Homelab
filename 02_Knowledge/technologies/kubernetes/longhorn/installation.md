---
title: "Longhorn installation on k3s"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, storage, longhorn, installation, k3s]
sources:
  - url: "https://longhorn.io/docs/1.12.1/deploy/install/install-with-helm/"
    title: "Install Longhorn with Helm"
  - url: "https://longhorn.io/docs/1.12.1/deploy/install/"
    title: "Longhorn Quick Installation"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/k3s/installation.md"
---

# Longhorn installation on k3s

## Overview

Longhorn installs into an existing cluster as a Helm chart. On k3s the usual blockers are missing host packages (open-iscsi, NFS client) and kernel modules; k3s ships its own storage but does not pre-install the initiators Longhorn relies on.

## Details

### Prerequisites

- **open-iscsi** — required on every node; Longhorn uses iSCSI for the volume data path. Install with the distro package manager and enable the service.
- **NFS client** — needed for NFS backups and for ReadWriteMany (RWX) volumes; install `nfs-common` on nodes that will take backups or serve RWX volumes.
- **Kernel modules** — `iscsi_tcp` (and `nvme_tcp` if using NVMe volumes) must be loadable; verify with `modprobe`.
- **k3s specifics** — ensure the kubelet can mount volumes (k3s enables this by default) and that no conflicting storage provisioner claims the same PVC class.

### Helm install

```bash
Example — abstract
helm repo add longhorn https://charts.longhorn.io
helm repo update
helm install longhorn longhorn/longhorn --namespace longhorn-system --create-namespace
```

After install, confirm pods come up in the `longhorn-system` namespace:

```bash
Example — abstract
kubectl -n longhorn-system get pods -w
```

### Node and disk configuration

- Longhorn automatically uses the writable mount points on each node as **default disks**. Add or remove disks per node from the UI or via the Node CRD.
- Set **node tags** to constrain replica scheduling (e.g. tag a fast NVMe node and pin critical volumes to it).
- Reserve disk space on each node (`storageReservedPercentageForDefaultDisk`) so replicas do not fill the OS disk.

## Sources / Further Reading

- [Install Longhorn with Helm](https://longhorn.io/docs/1.12.1/deploy/install/install-with-helm/)
- [Longhorn quick installation](https://longhorn.io/docs/1.12.1/deploy/install/)
- [k3s installation](./02_Knowledge/technologies/kubernetes/k3s/installation.md)
