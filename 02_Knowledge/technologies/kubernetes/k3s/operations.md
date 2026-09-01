---
title: "k3s operations"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, k3s, operations, backup, upgrade]
sources:
  - url: "https://docs.k3s.io/upgrades"
    title: "k3s upgrades"
  - url: "https://docs.k3s.io/datastore/backup-restore"
    title: "k3s backup and restore"
last_audit_date: 2026-08-25
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/kubectl.md"
---

# k3s operations

## Overview

Day-2 tasks for the homelab k3s node: using the bundled clients, backing up and restoring the cluster, upgrading, and managing the systemd service. Everything is host-level — no in-cluster operator required.

## Details

### k3s kubectl / crictl

The k3s binary embeds the client tools; run them through it or symlink them.

Example — abstract:

```bash
sudo k3s kubectl get nodes
sudo k3s kubectl get pods -A
sudo k3s crictl ps                # containerd containers
sudo k3s crictl images            # images pulled by containerd
```

Non-root users can use plain `kubectl` with `/etc/rancher/k3s/k3s.yaml` (`KUBECONFIG=...`) when installed with `--write-kubeconfig-mode 644`. See `./02_Knowledge/technologies/kubernetes/concepts/kubectl.md` for general kubectl usage.

### Backup

k3s state lives in two places:

| Path | Contents |
|---|---|
| `/var/lib/rancher/k3s/` | SQLite datastore, manifests, containerd images, local-path PVs, server token (`server/token` / `server/node-token`) |
| `/etc/rancher/k3s/` | `config.yaml`, `k3s.yaml` (kubeconfig) |

Example — real config (homelab backup snapshot):

```bash
sudo tar -czf k3s-backup-$(date +%F).tar.gz \
  -C /var/lib/rancher/k3s . \
  -C /etc/rancher/k3s .
```

Restore: stop k3s (`sudo systemctl stop k3s`), replace the two directories from the tarball, keep the node IP, start k3s. This is exactly the migration path used for the Ubuntu → NixOS move — see `./03_Research/nixos-adoption/overview.md`.

### Upgrade

Example — abstract:

```bash
curl -sfL https://get.k3s.io | sh -s -   # re-runs installer, upgrades in place
```

Or upgrade the k3s package on NixOS by bumping the nixpkgs input. Either way, a systemd restart picks up the new binary.

### systemd service management

Example — abstract:

```bash
sudo systemctl status k3s            # server node
sudo systemctl status k3s-agent      # agent node
sudo journalctl -u k3s -f            # live logs
sudo systemctl restart k3s
```

The service is `Type=notify` — it reports ready only once the API is up. On NixOS the module wires the same units; `systemctl restart k3s` works identically.

## Sources / Further Reading

- [k3s backup and restore](https://docs.k3s.io/datastore/backup-restore)
- [k3s upgrades](https://docs.k3s.io/upgrades)
- [k3s known issues](https://docs.k3s.io/known-issues)
