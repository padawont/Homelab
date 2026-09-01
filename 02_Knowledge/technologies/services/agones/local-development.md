---
title: "Agones local development — SDK server without a cluster"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, development, local]
sources:
  - url: "https://agones.dev/site/docs/guides/client-sdks/"
    title: "Agones client SDKs guide"
  - url: "https://agones.dev/site/docs/advanced/out-of-cluster-dev-server/"
    title: "Agones out of cluster dev server"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/overview.md"
  - "./02_Knowledge/technologies/services/agones/sdk-integration.md"
---

# Agones local development — SDK server without a cluster

## Overview

Agones ships local development tooling for working against the game-server SDK
without spinning up a full Kubernetes stack (or even a cluster at all). The
**SDK-server** — normally injected as a sidecar into every GameServer Pod — can
be run as a standalone binary, and the game server binary connects to it over
gRPC on `localhost:9357`. This makes the SDK testable from a laptop or CI
before anything is deployed.

## Details

### SDK-server modes

- **Fully local** — no cluster. Start the SDK-server with `--local` (or `--file`
  with a saved state file) and the game server talks to it on the local port
  with no Kubernetes involved. Good for SDK-conformance and single GameServer
  testing.
- **Out of cluster** — real cluster. Start the SDK-server with `--kubeconfig`
  pointing at a cluster, plus the GameServer name and namespace to bind to. The
  SDK-server talks to the cluster on your behalf while both it and the game
  server run on your machine.

### Out-of-cluster workflow

Prerequisites:

- A cluster reachable with `kubectl`, and a `GameServer` resource created in it
  (the GameServer carries an `agones.dev/dev-address` annotation so allocating
  clients can reach the dev game server running locally).
- The SDK-server binary and your game server binary.

Steps:

1. Create the `GameServer` in the cluster (annotate it for local development).
2. Run the SDK-server locally, pointing it at the cluster:
   `sdk-server --kubeconfig <path> --gameserver-name <name> --pod-namespace <ns>`.
3. Run the game server binary locally (in an IDE with breakpoints works), or in
   a container with `--network host` so it can reach `localhost:9357`.
4. The game server connects to the local SDK-server over gRPC on
   `localhost:9357`; the SDK-server relays to the cluster GameServer resource.

Example — abstract (exploratory only; nothing is deployed in the homelab):

```bash
# simplified, vendor-neutral — command sketch, not a config
# run the SDK-server locally against the cluster
sdk-server --kubeconfig ~/.kube/config --gameserver-name example-gameserver --pod-namespace default
```

### Why run the game server locally

- Debug with breakpoints — the full IDE toolchain works on the game process.
- Test real SDK calls (`Ready`, `Allocate`, `Health`, etc.) against a real
  cluster GameServer instead of a mock.
- Watch the state transitions live: `kubectl get gameserver <name> --watch`.

### Testing fleets without a full stack

Before a Fleet is ever created, the local SDK-server validates the game-server
SDK integration: the SDK handshake, the port, and the call flow all run against
a single GameServer (fully local or out-of-cluster) without needing the whole
Agones control plane. This catches SDK wiring problems long before Fleet
rollouts.

### Homelab fit

Exploratory only — Agones is **not deployed** in the homelab. If it moves
forward, local development is the natural first step for validating a game
server's SDK integration against the single-node, Rancher-managed k3s cluster
(`node-main`) before any Fleet/GameServer rollout; see the Agones overview note.
Per-engine SDK wiring (which SDK, which language bindings) belongs in the
companion note `./02_Knowledge/technologies/services/agones/sdk-integration.md`.

## Sources / Further Reading

- Agones client SDKs guide (Local Development): https://agones.dev/site/docs/guides/client-sdks/
- Agones out of cluster dev server: https://agones.dev/site/docs/advanced/out-of-cluster-dev-server/
- Agones documentation (v1.60.0): https://agones.dev/site/docs/
- Source repository: https://github.com/agones-dev/agones
- Sibling notes: `./02_Knowledge/technologies/services/agones/overview.md`,
  `./02_Knowledge/technologies/services/agones/sdk-integration.md`
