---
title: "Agones — dedicated game server orchestration on Kubernetes"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, kubernetes, game-servers, dedicated-game-servers]
sources:
  - url: "https://agones.dev"
    title: "Agones — dedicated game server hosting on Kubernetes"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://agones.dev/site/docs/advanced/system-diagram/"
    title: "Agones system diagram"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/crds-api.md"
  - "./02_Knowledge/technologies/services/agones/game-server-lifecycle.md"
  - "./02_Knowledge/technologies/kubernetes/k3s/overview.md"
---

# Agones — dedicated game server orchestration on Kubernetes

## Overview

Agones is a CNCF sandbox project (v1.60.0) for hosting, running, and scaling
dedicated game servers on Kubernetes. Game servers are declared as Kubernetes
custom resources and managed through the usual YAML/API workflows — `kubectl`
and the Kubernetes API — while Agones handles the scaling and lifecycle work a
dedicated game server workload needs on top of a stock cluster.

## Details

### Why dedicated game servers

Dedicated game servers are not matchmaking: a matchmaker matches players into
a game and hands off, whereas a dedicated server hosts the session and players
connect to it directly. Each match gets its own server instance, giving
low-latency, session-based play that does not share state with unrelated
players. Because instances are per-game, they must be created on demand, run
while players are connected, and be torn down when the match ends — the
lifecycle Agones automates.

### Platform model

The core object is the `GameServer` custom resource, backed by a single Pod.
Agones injects an **SDK-server sidecar** container into that Pod; the game
server binary connects to it over gRPC through a thin SDK wrapper (endpoints
on ports 9357/9358). The SDK is how the game process reports its state back to
Agones.

Example — abstract (exploratory only; nothing is deployed in the homelab):

```yaml
# simplified, vendor-neutral — image values are illustrative
apiVersion: agones.dev/v1
kind: GameServer
metadata:
  name: example-gameserver
spec:
  template:
    spec:
      containers:
        - name: game-server    # your game binary
          image: example/game-server:latest
        - name: sdk-server     # Agones sidecar, SDK endpoints on 9357/9358
          image: example/agones-sdk-server:1.60.0
```

### Control-plane components

The Agones control plane runs as four deployments:

- **agones-controller** — runs the control loops for all Agones custom
  resources.
- **agones-extensions** — hosts the admission webhooks and the
  GameServerAllocation APIService.
- **agones-allocator** — exposes allocation over gRPC and REST, so clients can
  request a ready GameServer for new players.
- **agones-ping** — provides latency testing endpoints for client-side
  connection measurement.

### Homelab placement

Exploratory only — Agones is **not deployed** in the homelab. If it moves
forward, the target is the `agones-system` namespace on the single-node,
Rancher-managed k3s cluster (`node-main`); see
`./02_Knowledge/technologies/kubernetes/k3s/overview.md` and
`./02_Knowledge/technologies/kubernetes/rancher/overview.md`. Companion notes
cover the CRDs/API surface (`./02_Knowledge/technologies/services/agones/crds-api.md`)
and the GameServer lifecycle
(`./02_Knowledge/technologies/services/agones/game-server-lifecycle.md`).

## Sources / Further Reading

- Agones official site: https://agones.dev
- Agones documentation (v1.60.0): https://agones.dev/site/docs/
- System diagram: https://agones.dev/site/docs/advanced/system-diagram/
- Source repository: https://github.com/agones-dev/agones
- Sibling notes: `./02_Knowledge/technologies/services/agones/crds-api.md`,
  `./02_Knowledge/technologies/services/agones/game-server-lifecycle.md`
- k3s cluster: `./02_Knowledge/technologies/kubernetes/k3s/overview.md`
