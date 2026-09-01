---
title: "Agones fleet autoscaling — Fleet and FleetAutoscaler"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, autoscaling, fleet]
sources:
  - url: "https://agones.dev/site/docs/advanced/scheduling-and-autoscaling/"
    title: "Agones docs — Scheduling and autoscaling (buffer + webhook, Fleet scheduling, scale-down, cluster autoscaler)"
  - url: "https://agones.dev/site/docs/reference/fleetautoscaler/"
    title: "Agones API reference — FleetAutoscaler"
  - url: "https://agones.dev/site/docs/guides/metrics/"
    title: "Agones docs — Metrics (autoscaling observability)"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/crds-api.md"
  - "./02_Knowledge/technologies/services/agones/metrics-monitoring.md"
---

# Agones fleet autoscaling — Fleet and FleetAutoscaler

## Overview

A `Fleet` declares a desired number of identical `GameServer` instances, and a
`FleetAutoscaler` keeps that number in sync with demand. The Fleet is the
scale unit: all GameServers come from one template, and the FleetAutoscaler
adjusts the Fleet's `replicas` count so there are always enough ready (but not
yet allocated) servers for incoming players. The default **buffer** strategy
maintains a configurable pool of ready GameServers; a **webhook** strategy
delegates the replica-count decision to custom logic.

## Details

### Fleet — the scalable unit

A Fleet is a set of GameServers declared from a common template with a
`spec.replicas` count. The Fleet controller creates and maintains GameServers
to match that count, and `status` reports the running state:

- `replicas` — total GameServers the Fleet owns.
- `readyReplicas` — GameServers in `Ready` state, available for allocation.
- `allocatedReplicas` — GameServers already handed to players.

`spec.scheduling` selects the placement strategy:

- **Packed** (default) — bins GameServers onto as few nodes as possible.
- **Distributed** — spreads GameServers across as many nodes as possible.

On a single-node homelab cluster the two behave identically in practice: there
is only one node to place on. Packed remains the default because it is
designed to work with cluster/node autoscalers (see below). The API shape of
the Fleet is covered in the companion note
`./02_Knowledge/technologies/services/agones/crds-api.md`.

### FleetAutoscaler — the autoscaling policy

A `FleetAutoscaler` is a custom resource in the `autoscaling.agones.dev/v1`
API group. It targets exactly one Fleet via `spec.fleetName` and re-evaluates
its policy every `spec.sync` interval (a struct configured via
`sync.fixedInterval.seconds`), adjusting
the Fleet's `replicas` count accordingly.

`spec.policy.type` selects the strategy:

- **Buffer** (default) — keep a pool of ready GameServers.
- **Webhook** — ask an external endpoint how many replicas the Fleet should
  have.

The buffer policy (`spec.policy.buffer`) has three fields:

- `bufferSize` — the target buffer of ready GameServers. An integer sets an
  absolute count (e.g. `2`); a percentage string (e.g. `"20%"`) sets the
  buffer as a percentage of the desired number of Ready game server instances
  over the Allocated count.
- `minReplicas` / `maxReplicas` — hard bounds the autoscaler will not scale
  below or above.

Example — abstract (exploratory only; nothing is deployed in the homelab):

```yaml
# simplified, vendor-neutral
apiVersion: autoscaling.agones.dev/v1
kind: FleetAutoscaler
metadata:
  name: example-fleet-autoscaler
spec:
  fleetName: example-fleet
  sync:
    type: FixedInterval
    fixedInterval:
      seconds: 30
  policy:
    type: Buffer
    buffer:
      bufferSize: "20%"   # int count (2) or percentage string ("20%")
      minReplicas: 0
      maxReplicas: 10
```

### Scale-up and scale-down behavior

The buffer policy watches ready (unallocated) capacity, not just the total
replica count. When allocations hand GameServers to players,
`allocatedReplicas` rises and `readyReplicas` falls, so the autoscaler scales
up to restore the buffer. When the buffer exceeds `bufferSize`, it scales
down.

Scale-down only removes GameServers that are ready and unallocated — allocated
servers keep running until the match ends. The order in which surplus
GameServers are removed is governed by the Fleet's `spec.scheduling`: **Packed**
empties the least-loaded nodes first, **Distributed** removes GameServers at
random. The scheduling mode also governs allocation: Packed/Distributed is set
on both the Fleet and on `GameServerAllocation`, so placement and allocation
follow the same policy.

### Cluster autoscaler interaction — homelab note

Packed scheduling is designed to work with a cluster/node autoscaler: packing
GameServers tightly lets empty nodes be scaled away. On the single-node
homelab cluster a cluster autoscaler is not applicable — there are no nodes to
add or remove — so the scheduling choice is about behaviour (tight packing vs.
spreading) rather than about node economy.

### Webhook policy — custom autoscaling

With `policy.type: Webhook` the FleetAutoscaler calls an external HTTP
endpoint (a Kubernetes `Service` or a plain URL) that returns the desired
replica count for the Fleet. This suits game-specific scaling logic the buffer
heuristic cannot express (e.g. player-count thresholds from the matchmaker).
The reference page below documents the request/response payload.

## Sources / Further Reading

- Fleet autoscaling (buffer + webhook, scheduling, scale-down, cluster
  autoscaler): https://agones.dev/site/docs/advanced/scheduling-and-autoscaling/
- FleetAutoscaler API reference: https://agones.dev/site/docs/reference/fleetautoscaler/
- Metrics / autoscaling observability: https://agones.dev/site/docs/guides/metrics/
- Agones documentation (v1.60.0): https://agones.dev/site/docs/
- Source repository: https://github.com/agones-dev/agones
- Sibling notes: `./02_Knowledge/technologies/services/agones/crds-api.md`,
  `./02_Knowledge/technologies/services/agones/metrics-monitoring.md`
