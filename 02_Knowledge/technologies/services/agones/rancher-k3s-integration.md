---
title: "Agones on Rancher-managed k3s — homelab integration"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, rancher, k3s, kubernetes]
sources:
  - url: "https://agones.dev/site/docs/installation/"
    title: "Agones installation guide"
  - url: "https://agones.dev/site/docs/advanced/allocator-service/"
    title: "Agones allocator service (TLS)"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/install-config.md"
  - "./02_Knowledge/technologies/services/agones/security.md"
  - "./05_Implementations/node-main/rancher/overview.md"
---

# Agones on Rancher-managed k3s — homelab integration

## Overview

This note wires the Agones control plane to the real homelab cluster: a
single-node, Rancher-managed k3s on `node-main` (192.168.111.7). It covers
how Agones fits inside that cluster, how the cert-manager already installed
for Rancher is reused for allocator TLS, and what single-node homelab wiring
means for scheduling and storage.

Exploratory only — Agones is **not deployed** in the homelab. Every config
block below is `Example — abstract`. Install mechanics live in the companion
note `./02_Knowledge/technologies/services/agones/install-config.md`; TLS
details in `./02_Knowledge/technologies/services/agones/security.md`.

## Details

### Target cluster

The homelab cluster is a single-node k3s on `node-main`
(`192.168.111.7`), managed by Rancher (real cluster facts in
`./05_Implementations/node-main/rancher/overview.md`):

- **Access**: Helm 3 + kubectl with `KUBECONFIG=/etc/rancher/k3s/k3s.yaml`.
- **Rancher**: installed via Helm into namespace `cattle-system` from the
  `releases.rancher.com` server-charts repo; UI at `https://rancher.local`.
- **Hosts entry**: `rancher.local` resolves to `192.168.111.7` via
  `networking.extraHosts` in the NixOS flake on the node, and `/etc/hosts`
  on browser machines.
- **cert-manager**: v1.21.1 installed before Rancher to mint its ingress TLS
  certificates (`ingress.tls.source=rancher`, self-signed, auto-rotated).

Agones is a separate Helm install into its own namespace on this same
cluster.

### How Agones fits

Agones installs via Helm into the `agones-system` namespace. The control
plane then runs as four deployments:

- **agones-controller** — control loops for the Agones custom resources.
- **agones-extensions** — admission webhooks and the GameServerAllocation
  APIService.
- **agones-allocator** — gRPC/REST allocation endpoint.
- **agones-ping** — latency testing endpoints.

On the single node, all control-plane pods and every GameServer Pod land on
`node-main`; there is no second node to spread across. The chart values and
namespace setup are covered in
`./02_Knowledge/technologies/services/agones/install-config.md`.

Example — abstract (exploratory only; nothing is deployed in the homelab):

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
# intended target namespace for Agones (chart + values in install-config.md)
kubectl create namespace agones-system
```

### cert-manager ingress pattern

Rancher already installed cert-manager on the cluster, so the same issuer
pattern is reused instead of introducing a second one. Agones documents the
allocator service with cert-manager-provided TLS certificates (see the
allocator-service docs); the Issuer/ClusterIssuer choice, certificate SANs,
and secret handling are detailed in
`./02_Knowledge/technologies/services/agones/security.md`.

The `rancher.local` hosts-entry pattern carries over: any hostname chosen
for the allocator endpoint needs the same treatment — `networking.extraHosts`
in the NixOS flake on node-main and `/etc/hosts` on browser machines.

### Homelab wiring

- **Scheduling**: Agones `scheduling` is `Packed` (default; bins GameServers
  tightly across nodes) or `Distributed` (spreads them across nodes). With a
  single node every GameServer lands on `node-main` either way, so the
  `Packed` default is the sensible choice — `Distributed` has no other node
  to spread across.
- **Autoscaling**: a `FleetAutoscaler` can still keep a buffer of ready
  GameServers, but capacity is bounded by the single node — there is no
  cross-node scaling.
- **Storage**: Agones itself needs no persistent volume — the control-plane
  components run without PVCs. GameServer Pods that do want volumes can use
  Longhorn; see `./02_Knowledge/technologies/kubernetes/longhorn/overview.md`
  and `./02_Knowledge/technologies/kubernetes/k3s/storage.md` for the
  homelab storage picture.

### Verification

Once Agones is installed (see `./02_Knowledge/technologies/services/agones/install-config.md`), confirm the control plane
is healthy:

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
kubectl -n agones-system get pods   # expect all Ready
```

## Sources / Further Reading

- Agones installation guide: https://agones.dev/site/docs/installation/
- Agones allocator service (TLS): https://agones.dev/site/docs/advanced/allocator-service/
- Agones documentation (v1.60.0): https://agones.dev/site/docs/
- Agones source repository: https://github.com/agones-dev/agones
- Real cluster facts: `./05_Implementations/node-main/rancher/overview.md`
- Companion notes: `./02_Knowledge/technologies/services/agones/install-config.md`,
  `./02_Knowledge/technologies/services/agones/security.md`
- Scheduling model: `./02_Knowledge/technologies/services/agones/crds-api.md`
