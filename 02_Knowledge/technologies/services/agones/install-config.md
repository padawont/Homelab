---
title: "Agones installation and configuration — Helm on k3s"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, kubernetes, helm, configuration]
sources:
  - url: "https://agones.dev/site/docs/installation/"
    title: "Agones installation guide"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/overview.md"
  - "./02_Knowledge/technologies/services/agones/rancher-k3s-integration.md"
  - "./02_Knowledge/technologies/services/agones/security.md"
  - "./05_Implementations/node-main/rancher/overview.md"
---

# Agones installation and configuration — Helm on k3s

## Overview

Agones is installed into the cluster through a Helm chart into the
`agones-system` namespace; a raw-YAML install is also available. This note
covers the install methods, the supported Kubernetes version matrix for Agones
1.60, and the chart values that matter in the homelab: TLS certs for the
controller/allocator, metrics toggles, and image settings. k3s/Rancher wiring
details are kept in the companion note
`./02_Knowledge/technologies/services/agones/rancher-k3s-integration.md`; TLS
and cert handling live in
`./02_Knowledge/technologies/services/agones/security.md`.

## Details

### Install methods

Helm is the preferred install path: add the Agones chart repository, then
install the chart (release name `agones`) into the `agones-system` namespace.
The installation guide also documents a raw-YAML install for clusters where
Helm is not desired. Nothing is deployed in the homelab yet — the commands
below are an abstract sketch.

Example — abstract (exploratory only; nothing is deployed in the homelab):

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 1. add the Agones Helm chart repo (repo URL per the installation guide)
helm repo add agones https://agones.dev/chart/stable
helm repo update

# 2. install the chart, release name "agones", into agones-system
helm install agones agones/agones \
  --namespace agones-system \
  --create-namespace \
  --values values.yaml
```

### Version and requirements

Agones 1.60.0 supports Kubernetes 1.34, 1.35, and 1.36. The homelab runs k3s on
the single-node, Rancher-managed cluster (`node-main`,
`KUBECONFIG=/etc/rancher/k3s/k3s.yaml`) with Helm 3 + kubectl available. k3s is
Kubernetes-compatible, but its minor version must be checked against the
1.34–1.36 matrix at deploy time — confirm with `kubectl version` before
installing.

### Key chart values

Three areas matter for the homelab:

- **TLS certs** — the chart provisions TLS for the controller and the
  allocator (the allocator uses mTLS for its gRPC/REST endpoint). Exact cert
  field names and cert-manager wiring are covered in
  `./02_Knowledge/technologies/services/agones/security.md` and the chart docs.
- **Metrics toggles** — `agones.metrics.prometheusEnabled` and
  `agones.metrics.prometheusServiceDiscovery` control Prometheus scraping of
  Agones metrics.
- **Image settings** — the chart supports overriding image repository/tag to
  pin the Agones 1.60.0 images.

Example — abstract (exploratory only; nothing is deployed in the homelab):

```yaml
# values.yaml sketch — metric field names per the Agones metrics guide;
# cert/allocator/image fields per the chart docs (v1.60.0)
agones:
  metrics:
    prometheusEnabled: true
    prometheusServiceDiscovery: true
  # certs:  TLS for controller + allocator (see security.md)
  # allocator:  endpoint/cert configuration
  # image:  repository/tag overrides to pin Agones 1.60.0
```

### What the chart sets up

Installing the chart creates and manages the `agones-system` namespace, the
service accounts for the control-plane components, and the four control-plane
deployments — `agones-controller`, `agones-extensions`, `agones-allocator`, and
`agones-ping` — plus their CRDs, admission webhooks, the GameServerAllocation
APIService, allocator TLS certs, and RBAC.

### Homelab placement

Exploratory only — Agones is **not deployed** in the homelab. If it moves
forward, the chart installs into `agones-system` on node-main with
`KUBECONFIG=/etc/rancher/k3s/k3s.yaml` and Helm 3 + kubectl available. Rancher
integration and the ingress pattern are covered in
`./02_Knowledge/technologies/services/agones/rancher-k3s-integration.md`; the
platform model and control-plane components are in
`./02_Knowledge/technologies/services/agones/overview.md`.

## Sources / Further Reading

- Agones installation guide: https://agones.dev/site/docs/installation/
- Agones documentation (v1.60.0): https://agones.dev/site/docs/
- Source repository: https://github.com/agones-dev/agones
- Sibling notes: `./02_Knowledge/technologies/services/agones/overview.md`,
  `./02_Knowledge/technologies/services/agones/rancher-k3s-integration.md`
