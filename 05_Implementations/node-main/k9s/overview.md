---
title: "k9s terminal Kubernetes UI"
status: active
author: "padawont"
date: 2026-10-02
tags: [kubernetes, k9s, tui, operations]
technologies: [k9s, helm, kubectl, kubernetes]
related_docs:
  - "./02_Knowledge/technologies/kubernetes/k9s/overview.md"
  - "./05_Implementations/node-main/k3s/overview.md"
  - "./04_ADRs/26-adopt-nixos-on-node-main.md"
references:
  online:
    - url: "https://k9scli.io/"
      title: "k9s documentation"
    - url: "https://github.com/derailed/k9s/releases"
      title: "k9s releases"
  repo:
    - "./02_Knowledge/technologies/kubernetes/k9s/overview.md"
    - "./05_Implementations/node-main/k3s/overview.md"
    - "./rollback.md"
node: node-main
---

# k9s terminal Kubernetes UI

Terminal UI for day-2 operations on the single-node k3s cluster, installed for
the `runic` user on `node-main` alongside Helm and `kubectl`.

## Prerequisites

- Working k3s cluster with a `runic`-readable kubeconfig — see
  `./05_Implementations/node-main/k3s/overview.md`.
- `curl`/`tar` to fetch the release and `sudo` to install into `/usr/local/bin`.
- Helm and `kubectl` if used for cluster operations.

## Deployment

### Pre-deploy checks

```bash
uname -s -m          # Linux x86_64
kubectl version --client
```

### Deploy

Install the k9s binary from the latest release (`k9s_Linux_amd64`):

```bash
curl -sL https://github.com/derailed/k9s/releases/latest/download/k9s_Linux_amd64.tar.gz | tar xz
sudo install -m 0755 k9s /usr/local/bin/k9s
```

Helm **v3.22.0** and `kubectl` **v1.36.5** are installed on the host as well.

### Post-deploy verification

```bash
k9s version
helm version
kubectl version --client
KUBECONFIG=/etc/rancher/k3s/k3s.yaml k9s
```

## Configuration

- Binaries: `/usr/local/bin/k9s` (latest release), Helm **v3.22.0**,
  `kubectl` **v1.36.5**.
- Run as user `runic` against the local cluster:

```bash
KUBECONFIG=/etc/rancher/k3s/k3s.yaml k9s
```

- k9s reads the kubeconfig directly; no k3s changes are required.

## Operations

```bash
# Open the TUI
KUBECONFIG=/etc/rancher/k3s/k3s.yaml k9s

# Version
k9s version
```

Views, keybindings, and trade-offs are covered in
`./02_Knowledge/technologies/kubernetes/k9s/overview.md`. Removal is documented in
`./rollback.md`.
