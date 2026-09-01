---
title: "Agones CRD/API model — GameServer, Fleet, FleetAutoscaler, GameServerAllocation"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, kubernetes, crd, api]
sources:
  - url: "https://agones.dev"
    title: "Agones — dedicated game server hosting on Kubernetes"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository (CRD definitions in install YAML / API reference)"
  - url: "https://agones.dev/site/docs/advanced/system-diagram/"
    title: "Agones system diagram"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/overview.md"
  - "./02_Knowledge/technologies/services/agones/game-server-lifecycle.md"
  - "./02_Knowledge/technologies/services/agones/fleet-autoscaling.md"
  - "./02_Knowledge/technologies/services/agones/allocator-service.md"
---

# Agones CRD/API model — GameServer, Fleet, FleetAutoscaler, GameServerAllocation

## Overview

Agones models dedicated game servers as Kubernetes custom resources across
three API groups: `GameServer` and `Fleet` use `agones.dev/v1`;
`FleetAutoscaler` uses `autoscaling.agones.dev/v1`; `GameServerAllocation`
uses `allocation.agones.dev/v1`. The API surface is four CRDs. `GameServer`, `Fleet`, and `FleetAutoscaler`
are reconciled by control loops in `agones-controller`;
`GameServerAllocation` is a request/response API served by the
`agones-extensions` aggregated APIService. Everything is declared as
standard YAML, so game server
infrastructure behaves like any other Kubernetes workload: `kubectl apply`
the manifests, and the controllers handle the rest.

## Details

### GameServer

The `GameServer` CRD is the unit of hosting — one `GameServer` instance maps to
a single Pod running the game binary plus the Agones SDK sidecar. Its spec
mirrors what a dedicated server needs at runtime:

- `template` — the Pod spec for the backing Pod.
- `ports` — the ports the game listens on, each with `name`, `containerPort`,
  `hostPort`, `portPolicy`, and `protocol`.
- `health` — SDK health-check settings (`initialDelaySeconds`,
  `periodSeconds`, `failureThreshold`).
- `scheduling` — `Packed` (default; bins GameServers tightly across nodes) or
  `Distributed` (spreads them across nodes).

`status` reports the runtime view: `state`, `address`, and `ports`. The state
machine (e.g. `Ready` → `Allocated` → `Shutdown`) will be detailed in the
companion note `./02_Knowledge/technologies/services/agones/game-server-lifecycle.md`.

### Fleet

A `Fleet` is a set of GameServers declared from one template, scaled by a
`replicas` count. It manages GameServer lifecycle at scale — the Fleet owns
GameServers and keeps the cluster at the desired count. `spec.scheduling`
mirrors the GameServer scheduling policy. `status` tracks `replicas`,
`readyReplicas`, and `allocatedReplicas` (plus `reservedReplicas`) so
operators can see capacity at a glance.

Example — abstract (exploratory only; nothing is deployed in the homelab):

```yaml
# simplified, vendor-neutral
apiVersion: agones.dev/v1
kind: Fleet
metadata:
  name: example-fleet
spec:
  replicas: 2
  template:
    spec:
      ports:
        - name: default
          containerPort: 7654
          portPolicy: Dynamic
          protocol: UDP
      template:
        spec:
          containers:
            - name: game-server
              image: example/game-server:latest
```

### FleetAutoscaler

A `FleetAutoscaler` (API group `autoscaling.agones.dev/v1`) adjusts the
`replicas` of a target Fleet based on a policy:

- `spec.fleetName` — the name of the Fleet to scale.
- Buffer strategy — keeps a buffer of ready GameServers using `bufferSize`
  (an absolute integer or a percentage string such as `20%`), `minReplicas`,
  and `maxReplicas`. The value format of `bufferSize` selects the mode: a
  percentage string enables percentage mode.
- Webhook strategy — calls an external webhook that returns the desired
  replica count for the Fleet, for custom scaling logic.

Scaling mechanics will be detailed in the companion note
`./02_Knowledge/technologies/services/agones/fleet-autoscaling.md`.

### GameServerAllocation

A `GameServerAllocation` requests one `Ready` GameServer from a Fleet to hand
to a player. The request is a custom resource served through the
`agones-extensions` APIService:

- selectors — find candidate GameServers via `matchLabels`/`matchExpressions`
  (Kubernetes label-selector semantics) plus `gameServerState`, `players`,
  `counters`, `lists`, and `metadata` to inject (e.g. player-count labels).
  `required`/`preferred` are deprecated selector lists, not scheduling
  constraints; `scheduling` (Packed/Distributed) is a separate top-level spec.
- `status` — the outcome: `state` (`Allocated`, `UnAllocated`, or
  `Contention`), plus `address` and `ports` for the player to connect to.

The allocation flow and the allocator service will be detailed in the
companion note `./02_Knowledge/technologies/services/agones/allocator-service.md`.

### Reconciliation

Two components make the API behave like native Kubernetes:

- `agones-controller` runs control loops for all Agones CRDs — it watches
  `GameServer`, `Fleet`, and `FleetAutoscaler` resources and reconciles the
  cluster toward the declared desired state.
- `agones-extensions` hosts the admission webhooks (defaulting + validation)
  and serves the `GameServerAllocation` APIService.

This split of controllers, admission webhooks, and an aggregated API service
is the standard Kubernetes extension pattern documented in the Agones system
diagram.

## Sources / Further Reading

- Agones official site: https://agones.dev
- Agones documentation (v1.60.0): https://agones.dev/site/docs/
- System diagram: https://agones.dev/site/docs/advanced/system-diagram/
- Source repository: https://github.com/agones-dev/agones
- Planned companion notes: `./02_Knowledge/technologies/services/agones/overview.md`,
  `./02_Knowledge/technologies/services/agones/game-server-lifecycle.md`,
  `./02_Knowledge/technologies/services/agones/fleet-autoscaling.md`,
  `./02_Knowledge/technologies/services/agones/allocator-service.md`
