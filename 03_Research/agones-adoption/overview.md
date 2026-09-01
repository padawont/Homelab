---
title: "Agones adoption — dedicated game server orchestration comparison"
status: accepted
author: "padawont"
date: 2026-08-30
tags: [agones, research, game-servers, kubernetes]
sources:
  - knowledge: "./02_Knowledge/technologies/services/agones/overview.md"
  - knowledge: "./02_Knowledge/technologies/services/agones/install-config.md"
  - knowledge: "./02_Knowledge/technologies/services/agones/rancher-k3s-integration.md"
  - knowledge: "./02_Knowledge/technologies/services/agones/sdk-integration.md"
  - knowledge: "./02_Knowledge/technologies/services/agones/allocator-service.md"
  - knowledge: "./02_Knowledge/technologies/services/agones/fleet-autoscaling.md"
  - knowledge: "./02_Knowledge/technologies/services/agones/metrics-monitoring.md"
  - knowledge: "./02_Knowledge/technologies/services/agones/local-development.md"
references:
  - url: "https://agones.dev"
    title: "Agones official site"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"
    title: "Kubernetes Deployments"
  - url: "https://www.open-match.dev"
    title: "Open Match"
  - url: "https://github.com/EmbarkStudios/quilkin"
    title: "Quilkin"
  - url: "https://aws.amazon.com/gamelift/"
    title: "Amazon GameLift"
last_audit_date: 2026-08-30
---

# Agones adoption — dedicated game server orchestration comparison

## Goal

Goal: decide which technology hosts dedicated game servers on the homelab's single-node k3s cluster (`node-main`). Sparked by the Agones epic (#313); this research stage is sub-issue #316. Research is required before an ADR per the PKM pipeline (Research → ADR).

## Alternatives

See `./alternatives.md` for the full index; each alternative has its own evaluation file (`./alternative-agones.md`, `./alternative-raw-kubernetes.md`, `./alternative-open-match.md`, `./alternative-quilkin.md`, `./alternative-gamelift.md`).

- Agones — **Selected** — CNCF sandbox project for hosting, running, and scaling dedicated game servers on Kubernetes (per https://agones.dev and `./02_Knowledge/technologies/services/agones/overview.md`).
- Raw Kubernetes — Rejected — Deployments/StatefulSets + HPA run workloads but lack the dedicated-server lifecycle, allocation API, and SDK sidecar that Agones adds on top of a stock cluster (per https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ and the overview note).
- Open Match — Rejected — complement, not substitute — a matchmaking framework; it matches players into a game and hands off, it does not host the session (per https://www.open-match.dev and the overview note).
- Quilkin — Rejected — complement, not substitute — Embark Studios UDP proxy (beta) for the networking layer; routing, not orchestration (per https://github.com/EmbarkStudios/quilkin).
- GameLift — Rejected — managed SaaS (GameLift Servers + Streams); a cloud dependency that does not fit a self-hosted homelab (per https://aws.amazon.com/gamelift/).

## Plan for ADR

### Recommended technology and why

Agones (v1.60.0) — game servers are declared as Kubernetes custom resources and managed through the usual YAML/API workflows, while Agones handles the scaling and lifecycle work a dedicated game server workload needs on top of a stock cluster (per https://agones.dev and `./02_Knowledge/technologies/services/agones/overview.md`). It builds on the existing k3s stack instead of introducing a separate platform, and it is CNCF-sandbox-governed open source rather than a proprietary SaaS (per https://agones.dev).

### How it fits into the existing homelab

Agones installs via Helm into the `agones-system` namespace on the single-node, Rancher-managed k3s cluster (`node-main`, 192.168.111.7), with Helm 3 + kubectl using `KUBECONFIG=/etc/rancher/k3s/k3s.yaml` (per `./02_Knowledge/technologies/services/agones/install-config.md` and `./02_Knowledge/technologies/services/agones/rancher-k3s-integration.md`). Deployment is not live yet — all config references are **Example — abstract**, not running config.

### Architecture overview

The Agones control plane runs as four deployments in `agones-system`: `agones-controller` (control loops for the Agones custom resources), `agones-extensions` (admission webhooks + GameServerAllocation APIService), `agones-allocator` (gRPC/REST allocation), and `agones-ping` (latency testing endpoints) (per the overview and install-config notes). Each `GameServer` is backed by a single Pod with an Agones **SDK-server sidecar**; the game binary reports state over gRPC on ports 9357/9358 (per the overview note). On the single node every control-plane and GameServer Pod lands on `node-main`, so the default `Packed` scheduling is the sensible choice — `Distributed` has no second node to spread across (per `./02_Knowledge/technologies/services/agones/rancher-k3s-integration.md`). The control plane needs no persistent volume; GameServer Pods that want volumes can use Longhorn (per the rancher-k3s-integration note).

### Dependencies and integration points

k3s on `node-main` with its minor version checked against the Agones 1.60.0 support matrix (Kubernetes 1.34–1.36) before install; Helm 3 + kubectl; cert-manager (v1.21.1, already installed for Rancher) reused for controller/allocator TLS; Prometheus metrics toggles; optional Longhorn for GameServer volumes (per the install-config and rancher-k3s-integration notes). Game code integrates via the SDK (`./02_Knowledge/technologies/services/agones/sdk-integration.md`), client allocation via the allocator service (`./02_Knowledge/technologies/services/agones/allocator-service.md`), and ready-GameServer buffers via `FleetAutoscaler` (`./02_Knowledge/technologies/services/agones/fleet-autoscaling.md`). Any allocator endpoint hostname needs the `rancher.local` hosts-entry pattern — `networking.extraHosts` in the NixOS flake on node-main plus `/etc/hosts` on browser machines (per the rancher-k3s-integration note).

### Risks and mitigation

- **Single-node capacity** — there is no cross-node scaling; a `FleetAutoscaler` can keep a buffer of ready GameServers but capacity is bounded by `node-main` (per the rancher-k3s-integration note). Mitigation: size the buffer to node resources and watch Agones metrics (`./02_Knowledge/technologies/services/agones/metrics-monitoring.md`).
- **Kubernetes version mismatch** — Agones 1.60.0 only supports k8s 1.34–1.36; the k3s minor version must be confirmed at deploy time (per the install-config note). Mitigation: run `kubectl version` before installing and upgrade k3s if it falls outside the matrix.
- **SDK integration cost** — the game process must be instrumented to report state to the SDK-server sidecar over gRPC (per the overview note). Mitigation: use the supported SDK wrappers and validate the lifecycle locally (`./02_Knowledge/technologies/services/agones/local-development.md`).
- **Player-facing networking** — Agones automates lifecycle, but routing player UDP traffic to GameServer Pods is still wiring that must be solved; Quilkin (beta) is an optional networking layer (per https://github.com/EmbarkStudios/quilkin). Mitigation: defer the choice and evaluate at the Implementation stage.

## Recommendation

**approve** — adopt Agones (v1.60.0) as the dedicated game server orchestration layer on the homelab k3s cluster. It is the only alternative purpose-built for the dedicated-server lifecycle on Kubernetes (CNCF sandbox, per https://agones.dev), fits the existing single-node Rancher-managed k3s stack in the `agones-system` namespace, and is governed as open source rather than proprietary SaaS. Raw Kubernetes is rejected because it would reinvent the lifecycle and allocator work Agones already does; Open Match and Quilkin are complements, not substitutes — Open Match only matches players into games and Quilkin only proxies UDP. GameLift is rejected for the homelab as a managed cloud SaaS that contradicts the self-hosted setup.
