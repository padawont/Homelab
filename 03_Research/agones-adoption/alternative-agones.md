---
title: "Alternative: Agones"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, kubernetes, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/agones/overview.md"
  - knowledge: "./02_Knowledge/technologies/services/agones/crds-api.md"
  - knowledge: "./02_Knowledge/technologies/services/agones/install-config.md"
  - knowledge: "./02_Knowledge/technologies/services/agones/metrics-monitoring.md"
references:
  - url: "https://agones.dev"
    title: "Agones official site"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
last_audit_date: 2026-08-30
---

# Alternative: Agones

## Overview

Agones is a CNCF sandbox project (v1.60.0) for hosting, running, and scaling dedicated game servers on Kubernetes ([overview](./02_Knowledge/technologies/services/agones/overview.md), [agones.dev](https://agones.dev)). Game servers are declared as Kubernetes custom resources — `GameServer`, `Fleet`, `FleetAutoscaler`, and `GameServerAllocation` — and managed through standard YAML/`kubectl` workflows ([crds-api](./02_Knowledge/technologies/services/agones/crds-api.md)). Each `GameServer` maps to a single Pod running the game binary plus an injected SDK-server sidecar that the game reports its state through ([overview](./02_Knowledge/technologies/services/agones/overview.md)). The control plane is four deployments — `agones-controller`, `agones-extensions`, `agones-allocator`, and `agones-ping` — installed via Helm into the `agones-system` namespace ([overview](./02_Knowledge/technologies/services/agones/overview.md), [install-config](./02_Knowledge/technologies/services/agones/install-config.md)).

## Pros

- **Purpose-built for dedicated game servers**: a Fleet keeps a desired replica count, FleetAutoscaler scales it via buffer or webhook policies, and GameServerAllocation hands a Ready GameServer to a player — no custom controller work needed ([crds-api](./02_Knowledge/technologies/services/agones/crds-api.md))
- **Lifecycle, health, and allocation built in**: the SDK-server sidecar exposes lifecycle (Ready → Allocated → Shutdown) and health checks over gRPC, so the game binary just reports its state ([overview](./02_Knowledge/technologies/services/agones/overview.md), [crds-api](./02_Knowledge/technologies/services/agones/crds-api.md))
- **Kubernetes-native**: everything is declared as CRDs with admission webhooks and an aggregated APIService, so it behaves like any other workload on the cluster ([crds-api](./02_Knowledge/technologies/services/agones/crds-api.md))
- **Metrics built in**: OpenCensus metrics with Prometheus toggles in the Helm chart (`prometheusEnabled`, `prometheusServiceDiscovery`) ([install-config](./02_Knowledge/technologies/services/agones/install-config.md), [metrics-monitoring](./02_Knowledge/technologies/services/agones/metrics-monitoring.md))
- **Open source and self-hostable**: CNCF sandbox project with a documented Helm chart and raw-YAML install, deployable on a single-node cluster ([overview](./02_Knowledge/technologies/services/agones/overview.md), [install-config](./02_Knowledge/technologies/services/agones/install-config.md))

## Cons

- **Control-plane overhead on a single node**: four control-plane deployments plus admission webhooks, the GameServerAllocation APIService, and an SDK sidecar in every GameServer Pod all share node-main's resources alongside game workloads ([overview](./02_Knowledge/technologies/services/agones/overview.md), [install-config](./02_Knowledge/technologies/services/agones/install-config.md))
- **Feature complexity with no live game servers yet**: dedicated servers need players (and typically a matchmaker) to be useful, and the knowledge notes mark everything "exploratory only" — nothing is deployed or exercised in the homelab today ([overview](./02_Knowledge/technologies/services/agones/overview.md))
- **Kubernetes version matrix constraint**: Agones 1.60.0 only supports Kubernetes 1.34–1.36, and the k3s minor version on node-main must be checked with `kubectl version` before installing ([install-config](./02_Knowledge/technologies/services/agones/install-config.md))

## Evaluation

- **Fit on single-node k3s**: acceptable — control-plane deployments and game server pods co-locate on node-main in the `agones-system` namespace, Rancher-managed with Helm 3 + kubectl available ([overview](./02_Knowledge/technologies/services/agones/overview.md), [install-config](./02_Knowledge/technologies/services/agones/install-config.md))
- **Deploy effort via Helm**: low-moderate — add the chart repo, install release `agones` into `agones-system`, then configure TLS for the controller/allocator, metrics toggles, and image pins; verify the k3s minor version against 1.34–1.36 first ([install-config](./02_Knowledge/technologies/services/agones/install-config.md))
- **Resource footprint**: moderate — four control-plane deployments, webhooks, an aggregated APIService, and per-GameServer SDK sidecars on one node ([overview](./02_Knowledge/technologies/services/agones/overview.md), [crds-api](./02_Knowledge/technologies/services/agones/crds-api.md))
- **Maintenance**: moderate — upgrades track the Agones/Kubernetes version matrix; TLS certs (allocator uses mTLS) and RBAC are chart-managed but need operator attention ([install-config](./02_Knowledge/technologies/services/agones/install-config.md))

## Verdict

**Selected** (tentative — final in overview.md) — the only purpose-built option for dedicated game server orchestration on Kubernetes: lifecycle, autoscaling, allocation, and metrics come out of the box as CRDs, installable via Helm on node-main. The caveats are real but bounded: single-node resource overhead, complexity with no live game servers yet, and a strict Kubernetes version matrix. See the [overview](./overview.md) for the full adoption plan.
