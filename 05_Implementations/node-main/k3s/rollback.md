---
title: "k3s single-node cluster — Rollback"
status: active
author: "padawont"
date: 2026-10-02
tags: [kubernetes, k3s, rollback, teardown]
technologies: [k3s, kubernetes]
related_docs:
  - "./overview.md"
  - "./04_ADRs/26-adopt-nixos-on-node-main.md"
references:
  online:
    - url: "https://docs.k3s.io/installation/uninstall"
      title: "k3s uninstall"
  repo:
    - "./overview.md"
node: node-main
---

# k3s single-node cluster — Rollback

Tear down the k3s server on `node-main`. The uninstall script **removes the data
directory**; use `k3s-killall.sh` to stop without deleting data.

## Prerequisites

- `sudo`/`root` on `node-main`.
- Backup of anything irreplaceable: manifests, PVC data under
  `/var/lib/rancher/k3s`, and `/etc/rancher/k3s/k3s.yaml` if still needed.
- Confirmation that no other host workload depends on the cluster.

## Rollback steps

1. Stop k3s and all containers, keeping the data directory intact:

```bash
sudo /usr/local/bin/k3s-killall.sh
```

2. Full teardown — **removes `/var/lib/rancher/k3s`** (all cluster state and
   `local-path` PVC data):

```bash
sudo /usr/local/bin/k3s-uninstall.sh
```

3. Remove any leftovers:

```bash
sudo rm -rf /etc/rancher/k3s
sudo rm -f /usr/local/bin/k3s /usr/local/bin/kubectl
sudo rm -rf /home/runic/.kube
```

## Verification

```bash
systemctl status k3s        # inactive / not-found
which k3s kubectl           # no usable binaries
ls /var/lib/rancher/k3s     # gone after full teardown
```

A remote `kubectl` should no longer reach `192.168.111.7:6443`.
