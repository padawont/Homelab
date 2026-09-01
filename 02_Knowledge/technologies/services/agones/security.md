---
title: "Agones security — RBAC, service accounts, TLS"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, security, rbac, tls]
sources:
  - url: "https://agones.dev/site/docs/advanced/service-accounts/"
    title: "Agones GameServer Pod service accounts"
  - url: "https://agones.dev/site/docs/advanced/allocator-service/"
    title: "Agones allocator service (mTLS)"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/install-config.md"
  - "./02_Knowledge/technologies/services/agones/allocator-service.md"
---

# Agones security — RBAC, service accounts, TLS

## Overview

Agones' security surface has three parts: the service account and RBAC that let
the SDK sidecar manage Agones custom resources, TLS for the control-plane
services (notably the allocator's mTLS), and network isolation for GameServer
Pods. This note records the posture to apply if Agones moves forward — nothing
is deployed in the homelab yet. Install mechanics live in the companion
`install-config.md` note; allocation-flow TLS specifics live in the companion
`allocator-service.md` note.

## Details

### Service accounts and RBAC for GameServer Pods

By default Agones sets up a service account plus extra RBAC so the **SDK
sidecar** can read and modify Agones custom resources (GameServer, Fleet,
etc.). The sidecar runs under the `agones-sdk` service account.

- **SDK sidecar**: needs Kubernetes API access to report state and update the
  Agones CRDs.
- **Game-server container**: does not need Kubernetes API access — players
  connect to it directly, so it is publicly exposed. Agones overwrites the
  mounted service-account key inside the game-server container so it cannot
  use the SDK's elevated permissions.
- **Bring your own service account**: you can set your own service account on
  the GameServer Pod spec, but you must match the default RBAC permissions or
  GameServers can fail.
- **Authoritative RBAC**: the default permissions are in the Agones
  installation YAML on GitHub; use that as the reference when customizing.

### TLS

- **Allocator mTLS**: the agones-allocator service authenticates clients with
  mutual TLS — the server presents its own certificate and clients present a
  client certificate. cert-manager is the recommended way to issue the TLS
  certificates.
- **Cert rotation**: certificates should be issued and rotated on a schedule;
  with cert-manager, renewals are handled through its Certificate lifecycle.
  Exposure and rotation specifics are kept in the companion
  `allocator-service.md` note.
- **Controller / extensions**: cert specifics for controller/extension services
  are out of scope until a sourced update. The cert-manager workflow Agones
  recommends for the allocator is the natural fit; Agones-documented specifics
  for controller/extension certs are not covered by the sources in this note.

### Network policies

General Kubernetes hardening guidance, not Agones-documented specifics:
isolate the control-plane namespace (`agones-system`) and GameServer Pods with
Kubernetes NetworkPolicies, allowing only the traffic the game actually needs
(e.g. the SDK sidecar endpoints). This is standard cluster hardening to apply
at deploy time; no specific NetworkPolicy YAML is recorded here because the
Agones sources in this note do not document one.

### Homelab fit

Exploratory only — Agones is **not deployed** in the homelab. If it moves
forward, the target is the `agones-system` namespace on the single-node,
Rancher-managed k3s cluster (`node-main`); see
`./02_Knowledge/technologies/kubernetes/k3s/overview.md`. On a minimal
single-node setup the key security concerns are:

- **Allocator mTLS** — only matters if the allocator is exposed outside the
  cluster; the companion `allocator-service.md` note uses the in-cluster
  GameServerAllocation CR path instead.
- **Service-account least privilege** — keep the default Agones SA/RBAC setup;
  do not grant the game-server container Kubernetes API permissions.

## Sources / Further Reading

- GameServer Pod service accounts: https://agones.dev/site/docs/advanced/service-accounts/
- Allocator service (mTLS): https://agones.dev/site/docs/advanced/allocator-service/
- Agones documentation (v1.60.0): https://agones.dev/site/docs/
- Source repository: https://github.com/agones-dev/agones
- Sibling notes: `./02_Knowledge/technologies/services/agones/install-config.md`,
  `./02_Knowledge/technologies/services/agones/allocator-service.md`
- k3s cluster: `./02_Knowledge/technologies/kubernetes/k3s/overview.md`
