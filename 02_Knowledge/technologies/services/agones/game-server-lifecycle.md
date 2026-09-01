---
title: "Agones game server lifecycle — SDK states and port policies"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, lifecycle, sdk]
sources:
  - url: "https://agones.dev/site/docs/guides/client-sdks/"
    title: "Agones — Client SDKs"
  - url: "https://agones.dev/site/docs/reference/gameserver/"
    title: "Agones GameServer reference (v1.60.0)"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/crds-api.md"
  - "./02_Knowledge/technologies/services/agones/sdk-integration.md"
  - "./02_Knowledge/technologies/services/agones/allocator-service.md"
---

# Agones game server lifecycle — SDK states and port policies

## Overview

A GameServer is stateful: it moves through a documented state machine, and
the game process drives the transitions through the Agones SDK. The SDK talks
to the SDK-server sidecar (see `./02_Knowledge/technologies/services/agones/overview.md`),
which reports the game's state back to `agones-controller`; the current state
is visible in `GameServer.status.state`. Lifecycle state names come from the
GameServer reference — `Creating`, `Scheduled`, `RequestReady`, `Ready`,
`Allocated`, `Reserved`, `Shutdown`, `Unhealthy` — and port policies
(`Dynamic`, `Static`, `Passthrough`) control how the game's listening port
is exposed on the node.

## Details

### Lifecycle state machine

The GameServer reference defines these states:

- `Creating` — the GameServer resource exists; the controller is still
  provisioning the backing Pod.
- `Scheduled` — the Pod has been scheduled onto a node.
- `RequestReady` — the SDK has called `Ready()` and Agones is confirming the
  transition.
- `Ready` — the game server is ready to accept players (allocatable).
- `Allocated` — the GameServer has been allocated to a player/session.
- `Reserved` — the GameServer is held for a future allocation via
  `Reserve(seconds)`.
- `Shutdown` — the GameServer is shutting down and its Pod is terminating.
- `Unhealthy` — health checks have failed (see health checking below).

The usual flow for a player session: creation → `Creating` → `Scheduled` →
(SDK `Ready()`) → `RequestReady` → `Ready` → (allocation: SDK `Allocate()` or
a `GameServerAllocation` request) → `Allocated` → (SDK `Shutdown()` at match
end) → `Shutdown`, then the Pod terminates. A `Ready` GameServer can instead
be reserved: `Reserve(seconds)` moves it to `Reserved`, and when the timer
expires it returns to `Ready`. The SDK docs mirror this set as `Ready`,
`Allocated`, `Reserved`, `Shutdown`, `Unhealthy`.

### SDK functions that drive states

The client SDKs expose lifecycle functions that are proxied to the
SDK-server:

- `Ready()` — signal that the game server is ready to serve players.
- `Allocate()` — manually allocate a `Ready` GameServer to a client.
- `Reserve(seconds)` — reserve the GameServer for a duration; expires back to
  `Ready`.
- `Shutdown()` — shut down the GameServer and the Pod it runs on.
- `Health()` — send a health ping (see health checking below).
- `SetLabel(key, value)` / `SetAnnotation(key, value)` — set metadata on the
  GameServer so allocation selectors can match it.
- `WatchGameServer(callback)` — register a callback that fires on GameServer
  state changes.

SDK calls are asynchronous: state changes are batched and sent in the
background, so the game process should not assume an instant, ordered
response.

### SDK transport

The SDK-server sidecar listens on two ports, both overridable via
environment variables:

- gRPC on port `9357` (default) — `AGONES_SDK_GRPC_PORT`
- REST/grpc-gateway on port `9358` (default) — `AGONES_SDK_HTTP_PORT`

### Health checking

`GameServer.spec.health` configures the health-check loop:

- `initialDelaySeconds` — delay after startup before health pings count.
- `periodSeconds` — interval between expected health pings.
- `failureThreshold` — consecutive missed pings before the GameServer is
  marked `Unhealthy`.
- `disabled` — turns health checking off.

The game calls `Health()` to ping; after `failureThreshold` failures the
GameServer state becomes `Unhealthy`.

### Port policies

Each GameServer port (`spec.ports[]`) declares a `portPolicy`:

- `Dynamic` (default) — a host port is allocated from a configured range at
  creation time; the actual port appears in `status.ports`.
- `Static` — the host port is fixed and must be unique on the node.
- `Passthrough` — the container port equals the host port; no port mapping.
- `protocol` — `UDP` by default (`TCP` is also supported).

Example — abstract (exploratory only; nothing is deployed in the homelab):

```yaml
# simplified, vendor-neutral — illustrative values only
apiVersion: agones.dev/v1
kind: GameServer
metadata:
  name: example-gameserver
spec:
  ports:
    - name: default
      containerPort: 7654
      portPolicy: Dynamic
      protocol: UDP
  health:
    initialDelaySeconds: 5
    periodSeconds: 5
    failureThreshold: 3
```

In a session the pieces combine: `Ready()` to become allocatable,
`WatchGameServer` to react to the `Allocated` event, periodic `Health()` pings
to stay healthy, and `Shutdown()` when the match ends. Allocation flow
details live in the companion note
`./02_Knowledge/technologies/services/agones/allocator-service.md`, CRD
structure in `./02_Knowledge/technologies/services/agones/crds-api.md`, and
SDK integration per engine in
`./02_Knowledge/technologies/services/agones/sdk-integration.md`.

## Sources / Further Reading

- Client SDKs guide: https://agones.dev/site/docs/guides/client-sdks/
- GameServer reference: https://agones.dev/site/docs/reference/gameserver/
- Documentation index (v1.60.0): https://agones.dev/site/docs/
- Source repository: https://github.com/agones-dev/agones
- Companion notes: `./02_Knowledge/technologies/services/agones/crds-api.md`,
  `./02_Knowledge/technologies/services/agones/sdk-integration.md`
