---
title: "k3s troubleshooting"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, k3s, troubleshooting, networking, containerd]
sources:
  - url: "https://docs.k3s.io/known-issues"
    title: "k3s known issues"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/k3s/networking.md"
---

# k3s troubleshooting

## Overview

The most common k3s failures in a homelab are firewall gaps, flannel problems, agent token mismatches, and containerd/CRI issues. Debug from the host: systemd logs first, then the bundled clients.

## Details

### Firewall ports

Symptom: agents can't join, pods can't reach each other across nodes, `kubectl` from another machine times out.

Check the three required ports (see `./02_Knowledge/technologies/kubernetes/k3s/networking.md`):

Example — real config (verify on node-main):

```bash
sudo ufw status
ss -lntup | grep -E '6443|10250'
# 8472/udp is hard to spot in ss; confirm with: sudo ufw status | grep 8472
```

Missing 8472/UDP shows up as flannel pods CrashLooping with VXLAN errors. Missing 10250 makes kubelet unreachable for `kubectl logs`/`exec`.

### flannel

Symptom: `kube-flannel` DaemonSet pods CrashLoopBackOff; pod IPs unreachable.

```bash
sudo k3s kubectl get pods -n kube-flannel -o wide
sudo k3s kubectl logs -n kube-flannel -l app=flannel --tail=50
```

Common causes: firewall blocks 8472/UDP, node IP changed (k3s cached the old one — restart after fixing `--node-ip`), or interface mismatch on multi-homed hosts.

### Token mismatch

Symptom: agent join fails with `Unauthorized`/`401` or "token does not match" errors.

The agent's `K3S_TOKEN` must equal the server's `/var/lib/rancher/k3s/server/node-token` (which is `K10<...>::server:<secret>`). On NixOS, a stale `tokenFile` secret (see `./02_Knowledge/technologies/kubernetes/k3s/configuration.md`) produces the same error — regenerate the secret and restart the agent.

### containerd / CRI debugging

Symptom: pods stuck in `ContainerCreating` or `ImagePullBackOff`; container runtime errors.

```bash
sudo k3s crictl ps -a
sudo k3s crictl images
sudo journalctl -u k3s | grep -i containerd
```

k3s runs its own containerd (socket `/run/k3s/containerd/containerd.sock`). If `crictl` from a system containerd is used, it points at the wrong socket — always use `k3s crictl` or set `--runtime-endpoint`.

### General approach

1. `sudo systemctl status k3s` — is the service up? `Type=notify` means it may be restarting.
2. `sudo journalctl -u k3s -n 100` — control-plane errors.
3. `sudo k3s kubectl get pods -A` — workload state.
4. Consult `./02_Knowledge/technologies/kubernetes/k3s/networking.md` for port expectations, then the Rancher docs below.

## Sources / Further Reading

- [k3s known issues](https://docs.k3s.io/known-issues)
- [k3s installation requirements / ports](https://docs.k3s.io/installation/requirements)
