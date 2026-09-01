---
title: "Agones SDK integration — game engine SDKs and SDK-server"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, sdk, grpc, game-engine]
sources:
  - url: "https://agones.dev/site/docs/guides/client-sdks/"
    title: "Agones client SDKs guide"
  - url: "https://agones.dev/site/docs/advanced/system-diagram/"
    title: "Agones system diagram"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/game-server-lifecycle.md"
  - "./02_Knowledge/technologies/services/agones/overview.md"
  - "./02_Knowledge/technologies/services/agones/local-development.md"
---

# Agones SDK integration — game engine SDKs and SDK-server

## Overview

The Agones SDK is the game-server side of Agones: it is how a game process
reports state back to the orchestration layer. Agones injects an **SDK-server
sidecar** into the same Pod as the game server, and the game binary connects
to it over gRPC through a thin SDK wrapper. The SDK hides the Kubernetes/Agones
API from the game engine — the game calls `Ready()`, `Health()`, `Shutdown()`,
and so on, and the SDK-server relays those to `agones-controller`.

Exploratory only — Agones is **not deployed** in the homelab; this note
documents the SDK integration for the planned rollout. The lifecycle state
machine that these SDK calls drive is covered in the companion note
`./02_Knowledge/technologies/services/agones/game-server-lifecycle.md`, and the
sidecar/control-plane architecture in
`./02_Knowledge/technologies/services/agones/overview.md`.

## Details

### How the SDK works

- The SDK-server sidecar runs alongside the game server **in the same Pod**.
- The game process embeds an SDK binary/library that connects to the sidecar
  over gRPC.
- SDKs are thin wrappers around gRPC-generated clients; where gRPC client
  generation is not well supported, the REST endpoint (grpc-gateway) is used
  instead.
- The SDK auto-discovers the sidecar gRPC port from the environment variables
  Agones sets on every game server container.

### Supported SDKs

Official client SDKs are published for the major game engines and languages
(client SDKs guide):

| Engine / language | Type |
|---|---|
| Unreal Engine | Plugin |
| Unity | SDK package |
| C++ | SDK package |
| C# | SDK package |
| Node.js | SDK package |
| Go | SDK package |
| Rust | SDK package |
| Python | SDK package |
| REST | HTTP API (grpc-gateway) |

### Connection

- gRPC port: `9357` (default) — the SDK's primary transport.
- REST/grpc-gateway port: `9358` (default) — for toolchains where gRPC client
  generation is not well supported.
- Agones sets `AGONES_SDK_GRPC_PORT` and `AGONES_SDK_HTTP_PORT` on all game
  server containers; the SDK reads the gRPC port from the environment
  automatically.

### Key SDK calls

The SDK exposes the state and metadata operations below. How each call drives
the GameServer state machine is detailed in
`./02_Knowledge/technologies/services/agones/game-server-lifecycle.md`.

- `Ready()` — signal the game server is ready to accept players.
- `Allocate()` — manually allocate a `Ready` GameServer to a client.
- `Reserve(seconds)` — hold the GameServer for a future allocation.
- `Shutdown()` — terminate the GameServer and its Pod.
- `Health()` — health ping for the health-check loop.
- `SetLabel(key, value)` / `SetAnnotation(key, value)` — set metadata for
  allocation selectors.
- `WatchGameServer(callback)` — receive GameServer state-change events.

Example — abstract (exploratory only; nothing is deployed in the homelab):

```go
// simplified, vendor-neutral — pseudocode against the SDK-server
sdk := connectToSDKServer()          // sidecar gRPC port, auto-discovered
sdk.Ready()                          // drive the GameServer to Ready
sdk.Health()                         // health-check loop ping
// ... run the match; WatchGameServer fires on Allocated ...
sdk.Shutdown()                       // terminate the GameServer + Pod at match end
```

### Writing your own SDK

Because official SDKs are thin wrappers, a custom integration is built the
same way:

- Generate a gRPC client from the Agones proto definitions (source in the
  Agones repository) and target the gRPC endpoint on port `9357`.
- Or call the REST/grpc-gateway endpoints directly on port `9358`.

For the homelab, use one of the official SDKs above; the custom route only
matters when an engine or toolchain is not covered.

### Local development

Local dev tooling (running a game server against a local SDK-server without a
cluster) is covered in the companion note
`./02_Knowledge/technologies/services/agones/local-development.md`.

## Sources / Further Reading

- Client SDKs guide: https://agones.dev/site/docs/guides/client-sdks/
- System diagram: https://agones.dev/site/docs/advanced/system-diagram/
- Documentation index (v1.60.0): https://agones.dev/site/docs/
- Source repository: https://github.com/agones-dev/agones
- Companion notes: `./02_Knowledge/technologies/services/agones/overview.md`,
  `./02_Knowledge/technologies/services/agones/game-server-lifecycle.md`,
  `./02_Knowledge/technologies/services/agones/local-development.md`
