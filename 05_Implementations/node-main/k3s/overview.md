---
title: "k3s single-node cluster"
status: active
author: "padawont"
date: 2026-10-02
tags: [kubernetes, k3s, cluster, deployment]
technologies: [k3s, kubernetes, containerd, traefik]
related_docs:
  - "./04_ADRs/26-adopt-nixos-on-node-main.md"
  - "./02_Knowledge/technologies/kubernetes/k3s/overview.md"
  - "./02_Knowledge/technologies/kubernetes/k3s/installation.md"
  - "./02_Knowledge/technologies/kubernetes/k3s/configuration.md"
references:
  online:
    - url: "https://docs.k3s.io/"
      title: "k3s documentation"
    - url: "https://docs.k3s.io/installation"
      title: "k3s installation"
  repo:
    - "./04_ADRs/26-adopt-nixos-on-node-main.md"
    - "./configs/config.yaml"
    - "./rollback.md"
node: node-main
---

# k3s single-node cluster

Single-node k3s server on `node-main`, the Kubernetes control plane and workload
host for the homelab. The host runs **Ubuntu 26.04.1 LTS**. ADR-26
(`./04_ADRs/26-adopt-nixos-on-node-main.md`) is the governing platform decision and
targets a future NixOS migration, so the host is still Ubuntu today and this record
documents the **actual deployed state**, not the target.

## Prerequisites

- Ubuntu 26.04.1 LTS host `node-main` (192.168.111.7) with a 100 GB root LVM.
- Outbound access to `get.k3s.io` and `github.com` for the installer and release binaries.
- `sudo`/`root` to install the systemd unit and write `/etc/rancher/k3s/`.
- No other Kubernetes distribution or `kubelet` already present on the host.

## Deployment

### Pre-deploy checks

```bash
hostnamectl
ip -4 addr show
df -h /
```

Confirm the node IP is `192.168.111.7` and the root filesystem has room for the
k3s data directory.

### Deploy

Install k3s via the official curl installer as a single-node server. Node identity
and kubeconfig mode come from `/etc/rancher/k3s/config.yaml` — see
`./configs/config.yaml`:

```bash
curl -sfL https://get.k3s.io | sh -
```

### Post-deploy verification

```bash
sudo systemctl status k3s
sudo k3s kubectl get nodes -o wide
sudo k3s kubectl version
```

Expect `k3s.service` **enabled + active** and `node-main` reporting `Ready`.

## Configuration

- Version: **v1.36.5+k3s1** (Kubernetes **v1.36.5**).
- Bundled `containerd` **2.3.4-k3s1.36** and `traefik` **3.7.13**.
- Effective config `/etc/rancher/k3s/config.yaml` (see `./configs/config.yaml`):

| Key | Value |
|---|---|
| `write-kubeconfig-mode` | `"644"` |
| `node-ip` | `192.168.111.7` |
| `node-name` | `node-main` |

- Data directory: `/var/lib/rancher/k3s` (on the 100 GB root LVM).
- Kubeconfig: `/etc/rancher/k3s/k3s.yaml` (**0644**), copied to
  `/home/runic/.kube/config` (**0600**).
- `kubectl` is a symlink: `/usr/local/bin/kubectl -> k3s`.

## Operations

```bash
# Cluster state
sudo k3s kubectl get nodes
sudo k3s kubectl get pods -A

# Service control
sudo systemctl restart k3s
sudo systemctl status k3s

# Logs
sudo journalctl -u k3s -f
```

Routine access as `runic` uses the copied kubeconfig — see
`./05_Implementations/node-main/k9s/overview.md`. Teardown is documented in
`./rollback.md`.
