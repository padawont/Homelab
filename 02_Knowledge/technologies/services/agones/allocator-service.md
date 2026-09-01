---
title: "Agones allocator service — GameServerAllocation flow"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, allocation, networking]
sources:
  - url: "https://agones.dev/site/docs/advanced/allocator-service/"
    title: "Agones docs — allocator service"
  - url: "https://agones.dev/site/docs/reference/gameserverallocation/"
    title: "Agones docs — GameServerAllocation reference"
  - url: "https://agones.dev/site/docs/advanced/system-diagram/"
    title: "Agones system diagram"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/game-server-lifecycle.md"
  - "./02_Knowledge/technologies/services/agones/security.md"
---

# Agones allocator service — GameServerAllocation flow

## Overview

A player or matchmaker is connected to a game server through a
`GameServerAllocation` (CRD in `allocation.agones.dev/v1`): a request that
selects one `Ready` GameServer from a Fleet and returns its connection details.
The request can go through the **agones-allocator** service — a TLS (mTLS)
gRPC/REST endpoint for clients outside the cluster — or, for clients already
inside the cluster, directly through the Kubernetes API. Either way the answer
comes back as an `Allocated` GameServer with an `address` and `ports` for the
player to connect to.

## Details

### The allocation request

A `GameServerAllocation` is a Kubernetes custom resource. Its `spec` describes
which GameServer should be picked:

- `scheduling` — how to pick a node: `Packed` (default; fills nodes before
  moving on) or `Distributed` (spread across nodes).
- Selectors — candidate selection via `matchLabels`/`matchExpressions`
  (Kubernetes label-selector semantics) plus:
  - `gameServerState` — e.g. request a `Ready` GameServer.
  - `players` — filter by current/desired player counts.
  - `counters` / `lists` — filter on Agones counters and lists.
  - `metadata` — labels/annotations to inject onto the allocated GameServer.
- `required` / `preferred` — deprecated selector lists, kept for backwards
  compatibility; not scheduling constraints.

`status` reports the outcome: `state` (`Allocated`, `UnAllocated`, or
`Contention`), and when allocated, `address` and `ports` for the player to
connect to.

Example — abstract (exploratory only; nothing is deployed in the homelab):

```yaml
# simplified, vendor-neutral
apiVersion: allocation.agones.dev/v1
kind: GameServerAllocation
metadata:
  name: example-allocation
spec:
  scheduling: Packed
  selectors:
    - matchLabels:
        agones.dev/fleet: example-fleet
      gameServerState: Ready
```

### The allocation flow

1. A player (or matchmaker) asks for a server.
2. The request hits the allocator (external client) or the Kubernetes API
   (in-cluster client), which creates a `GameServerAllocation`.
3. `agones-extensions` serves the GameServerAllocation APIService and hands the
   request to the allocation logic.
4. A `Ready` GameServer from the target Fleet is reserved (`Allocated`).
5. The client receives the GameServer `address` and `ports` and connects
   directly to the game server.

The full chain — client → agones-allocator → GameServerAllocation → Ready
GameServer from Fleet → connection details — is documented in the Agones
allocator-service guide and the system diagram.

### agones-allocator service

- Deployment: `agones-allocator` — exposes allocation over **gRPC** and **REST**
  for clients outside the cluster (game clients direct, external matchmakers).
- Auth: mTLS. Server presents its own cert; clients authenticate with a client
  cert. TLS certs are provisioned via cert-manager.
- The allocator translates incoming allocation requests into
  `GameServerAllocation` resources; namespace-scoped RBAC limits what it can
  touch.

TLS and cert details are kept in the companion note
`./02_Knowledge/technologies/services/agones/security.md`.

### Alternative: Kubernetes API directly

Because `GameServerAllocation` is a normal CRD, an in-cluster client (or an
operator with `kubectl`) can create the resource directly through the
Kubernetes API and read the result — no allocator service needed. For the
homelab (single-node cluster), where any matchmaker or game client would run in
the same cluster, the direct CR path is the appropriate flow; the
agones-allocator mTLS service only matters when requests come from outside the
cluster.

### Homelab placement

Exploratory only — Agones is **not deployed** in the homelab. If it moves
forward, the target is the `agones-system` namespace on the single-node,
Rancher-managed k3s cluster (`node-main`); see the Agones overview note.
Companion notes cover the GameServer lifecycle states
(`./02_Knowledge/technologies/services/agones/game-server-lifecycle.md`) and
TLS/cert handling (`./02_Knowledge/technologies/services/agones/security.md`).

## Sources / Further Reading

- Allocator service guide: https://agones.dev/site/docs/advanced/allocator-service/
- GameServerAllocation reference: https://agones.dev/site/docs/reference/gameserverallocation/
- System diagram: https://agones.dev/site/docs/advanced/system-diagram/
- Agones documentation (v1.60.0): https://agones.dev/site/docs/
- Source repository: https://github.com/agones-dev/agones
- Sibling notes: `./02_Knowledge/technologies/services/agones/game-server-lifecycle.md`,
  `./02_Knowledge/technologies/services/agones/security.md`
