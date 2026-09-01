---
title: "Alternative: Open Match"
status: draft
author: "padawont"
date: 2026-08-30
tags: [open-match, research, matchmaking]
sources:
  - knowledge: "./02_Knowledge/technologies/services/agones/overview.md"
  - knowledge: "./02_Knowledge/technologies/services/agones/allocator-service.md"
references:
  - url: "https://www.open-match.dev"
    title: "Open Match"
last_audit_date: 2026-08-30
---

# Alternative: Open Match

## Overview

Open Match is a flexible, scalable matchmaking framework for games (v1.8.0) that groups players into matches (https://www.open-match.dev). It promotes a "write code, not config" approach to matchmaking, the ability to scale up and down quickly, and tooling to measure match quality and latency (https://www.open-match.dev). The front page now promotes the next-generation "Open Match 2" (https://www.open-match.dev).

Matchmaking is a distinct layer from dedicated server hosting: a matchmaker matches players into a game and then hands off, whereas a dedicated server hosts the session and players connect to it directly (per `./02_Knowledge/technologies/services/agones/overview.md`). Open Match therefore complements Agones — it groups players into a match and hands off to a server obtained through the Agones allocation flow (per `./02_Knowledge/technologies/services/agones/allocator-service.md`).

## Pros

- **Flexible, scalable matchmaking**: Open Match groups players into matches and can scale up and down quickly (https://www.open-match.dev)
- **Complements the Agones allocation flow**: a player or matchmaker requests a server via `GameServerAllocation`, which returns an `Allocated` GameServer with `address` and `ports` — Open Match is the matchmaker that makes that request (per `./02_Knowledge/technologies/services/agones/allocator-service.md`)
- **Measurable match quality and latency**: built-in support for evaluating how good a match is and how fast it is produced (https://www.open-match.dev)
- **"Write code, not config"**: matchmaking logic is expressed in code rather than configuration, which keeps it adaptable (https://www.open-match.dev)

## Cons

- **Not a substitute for dedicated server hosting**: matchmaking only groups players — a dedicated server must still host the session underneath, so a GS layer like Agones is still required (per `./02_Knowledge/technologies/services/agones/overview.md`)
- **Adds a full extra system to operate**: a second distributed framework with its own scaling and telemetry to maintain alongside Agones (https://www.open-match.dev)
- **Overkill for a homelab with no live games**: there are no live multiplayer players to group, so the matchmaking problem does not exist yet; Agones itself is still exploratory and not deployed (per `./02_Knowledge/technologies/services/agones/overview.md`)

## Evaluation

- **Problem it solves**: player grouping and match formation — distinct from hosting and scaling game servers (per `./02_Knowledge/technologies/services/agones/overview.md`)
- **Fit with Agones**: complement only — the matchmaker hands off to an allocated GameServer via `GameServerAllocation` (per `./02_Knowledge/technologies/services/agones/allocator-service.md`)
- **Complexity for the homelab**: a full additional framework for a single-node k3s cluster with no players; heavy for the current footprint (per `./02_Knowledge/technologies/services/agones/overview.md`)
- **Scope fit**: deploying matchmaking is explicitly excluded from this epic, so Open Match is out of scope regardless of technical merit

## Verdict

**Rejected as standalone** — Open Match is a matchmaking framework, not a game server host, so it is a complement to Agones at best, not a substitute. It is overkill for a homelab with no live games and out of scope for this epic, which explicitly excludes deploying matchmaking. It is worth revisiting only as an add-on if live multiplayer games ever land on the Agones fleet.
