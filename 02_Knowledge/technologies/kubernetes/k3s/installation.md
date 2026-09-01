---
title: "k3s installation"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, k3s, installation, nixos]
sources:
  - url: "https://docs.k3s.io/installation"
    title: "k3s installation"
  - url: "https://docs.k3s.io/quick-start"
    title: "k3s quick start"
last_audit_date: 2026-08-25
related_docs:
  - "./03_Research/nixos-adoption/overview.md"
  - "./02_Knowledge/technologies/tools/nixos/services-secrets.md"
---

# k3s installation

## Overview

Two supported paths: the official curl installer (systemd-managed, works on any systemd Linux) and the NixOS in-tree module (`services.k3s.enable`). The homelab runs curl-installed k3s on Ubuntu today and will move to the NixOS module during the host migration — see `./03_Research/nixos-adoption/overview.md`.

## Details

### Curl installer — server

The installer downloads a release binary and creates a `k3s.service` systemd unit.

Example — abstract:

```bash
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
```

Notes: `--write-kubeconfig-mode 644` makes `/etc/rancher/k3s/k3s.yaml` readable for non-root `kubectl` use. Node IP is auto-detected; pin it with `--node-ip` because the installer can pick the wrong interface on multi-homed hosts.

### Curl installer — agent join

Example — abstract:

```bash
curl -sfL https://get.k3s.io | K3S_URL=https://server:6443 K3S_TOKEN=... sh -
```

The agent needs the server's token (from `/var/lib/rancher/k3s/server/node-token`). `K3S_TOKEN` matches that file's content; `K3S_URL` points at the API server port 6443.

### k3s on NixOS

The in-tree nixpkgs module is the supported route. `nix-community/k3s-nix` is dead (404) — do not use it.

Example — abstract (recommended tokenFile pattern):

```nix
services.k3s = {
  enable = true;
  role = "server";
  tokenFile = "/run/secrets/k3s-token";   # not `token` — avoid world-readable store secrets
  extraFlags = "--write-kubeconfig-mode 644";
};
```

Key options: `role` (`server` | `agent`), `serverAddr` (agent only), `token`/`tokenFile`, `extraFlags`. Node-main currently runs without `tokenFile` — it uses the auto-generated token (sops-nix skeleton only; see `./04_ADRs/26-adopt-nixos-on-node-main.md`). The module is first-class systemd: `Type=notify`, `Delegate=yes`, and k3s brings its own containerd — no docker dependency. See `./02_Knowledge/technologies/tools/nixos/services-secrets.md` for secret provisioning via sops-nix.

### Verification

Example — abstract:

```bash
sudo k3s kubectl get nodes
sudo systemctl status k3s
```

The API is reachable on 6443; worker traffic uses flannel UDP 8472 and kubelet 10250 — see `./02_Knowledge/technologies/kubernetes/k3s/networking.md`. Config precedence and `config.yaml` live in `./02_Knowledge/technologies/kubernetes/k3s/configuration.md`.

## Sources / Further Reading

- [k3s quick start](https://docs.k3s.io/quick-start)
- [k3s installation](https://docs.k3s.io/installation)
- [NixOS k3s module options](https://nixos.org/manual/nixos/stable/options#opt-services.k3s.enable)
