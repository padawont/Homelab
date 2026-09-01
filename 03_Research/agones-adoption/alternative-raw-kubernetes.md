---
title: "Alternative: Raw Kubernetes"
status: draft
author: "padawont"
date: 2026-08-30
tags: [kubernetes, research]
sources:
  - knowledge: "./02_Knowledge/technologies/kubernetes/k3s/overview.md"
references:
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"
    title: "Kubernetes Deployments"
  - url: "https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/"
    title: "Horizontal Pod Autoscaling"
last_audit_date: 2026-08-30
---

# Alternative: Raw Kubernetes

## Overview

Raw Kubernetes means hosting game servers on stock primitives — Deployments/StatefulSets for the server processes, Services for stable endpoints, and the Horizontal Pod Autoscaler (HPA) for replica counts — with no dedicated game-server layer on top. This is the baseline any game server hosting approach on K8s builds from: Deployments manage stateless, identical replicas via ReplicaSets with rolling updates (https://kubernetes.io/docs/concepts/workloads/controllers/deployment/); StatefulSets add stable per-pod identity and storage where a server needs them (per `./02_Knowledge/technologies/kubernetes/concepts/statefulsets.md`); Services give pods a stable DNS name and load balancing (per `./02_Knowledge/technologies/kubernetes/concepts/services.md`). In the homelab these primitives are already in daily use on the single-node k3s cluster (`node-main`) — see `./02_Knowledge/technologies/kubernetes/k3s/overview.md`.

## Pros

- **No extra control plane**: raw K8s adds nothing beyond the stock components the homelab already runs, unlike Agones which adds four control-plane deployments — `agones-controller`, `agones-extensions`, `agones-allocator`, `agones-ping` (per `./02_Knowledge/technologies/services/agones/overview.md`)
- **Standard, already-familiar primitives**: Deployments, StatefulSets, Services, and HPA are the same objects used for every other homelab service — no new CRDs, controllers, or SDKs to learn (per `./02_Knowledge/technologies/kubernetes/concepts/deployments.md`)
- **Already proven in the homelab stack**: k3s is API-compatible with upstream K8s and bundles ingress, CNI, and storage — the workload machinery is in place (per `./02_Knowledge/technologies/kubernetes/k3s/overview.md`)
- **Full flexibility**: nothing is abstracted, so any game-server behavior is implementable — but nothing is provided either

## Cons

- **No allocation logic**: raw K8s has no equivalent of Agones' GameServerAllocation — selecting a `Ready` server for a player and returning its address/ports must be hand-rolled (contrast: `./02_Knowledge/technologies/services/agones/allocator-service.md`)
- **No SDK lifecycle for dedicated servers**: no `Ready()` / `Allocate()` / `Shutdown()` / `Health()` calls to drive a server from boot to match end — that state-reporting loop must be built from scratch (contrast: `./02_Knowledge/technologies/services/agones/sdk-integration.md` and `./02_Knowledge/technologies/services/agones/game-server-lifecycle.md`)
- **Player→server allocation must be hand-rolled**: a matchmaker or custom controller would have to track which pods are free and hand out connection details itself
- **Scaling is replica-based, not ready-server-buffer-based**: HPA scales on metrics such as CPU (https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/), whereas a game server fleet needs a buffer of ready-but-unallocated servers — which Agones' FleetAutoscaler buffer strategy provides natively (per `./02_Knowledge/technologies/services/agones/fleet-autoscaling.md`)
- **No game server state machine**: there is no `Creating → Ready → Allocated → Shutdown` lifecycle object; pod readiness via probes is the closest primitive (per `./02_Knowledge/technologies/kubernetes/concepts/pods.md`)
- **Per-game boilerplate**: every new game title would reimplement allocation, lifecycle, and cleanup logic

## Evaluation

- **Effort to build a GS lifecycle manually**: high — allocation tracking, SDK-style state reporting, health/teardown, and buffer-based autoscaling would all be bespoke controllers or scripts on top of stock primitives
- **What Agones automates vs what raw K8s leaves to you**: Agones automates the whole dedicated-server lifecycle — GameServer CRs, SDK state machine, allocation, fleet autoscaling with a ready buffer, port policies; raw K8s provides only replica management (Deployments/StatefulSets + HPA) and networking (Services) — every game-server-specific behavior is left to you
- **Fit for the exploratory single-node homelab**: technically viable — the k3s cluster can run Deployments, Services, and HPA today — but it buys none of the dedicated-server behavior this research is evaluating, and a manual build would duplicate what Agones already provides (per `./02_Knowledge/technologies/services/agones/overview.md`)

## Verdict

**Rejected** — raw Kubernetes is a viable baseline and every other option builds on it, but it provides no dedicated game server lifecycle or allocator. Recreating allocation, SDK state reporting, and ready-server-buffer autoscaling by hand duplicates Agones while losing the maintained CRD/controller/SDK surface. For a homelab evaluating Agones on an exploratory single-node k3s cluster, raw K8s is the "do it all yourself" fallback, not a chosen alternative.
