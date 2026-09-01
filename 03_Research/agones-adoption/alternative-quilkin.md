---
title: "Alternative: Quilkin"
status: draft
author: "padawont"
date: 2026-08-30
tags: [quilkin, udp, proxy, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/agones/overview.md"
references:
  - url: "https://github.com/EmbarkStudios/quilkin"
    title: "Quilkin — UDP proxy for game servers"
last_audit_date: 2026-08-30
---

# Alternative: Quilkin

## Overview

Quilkin is a non-transparent UDP proxy specifically designed for large-scale multiplayer dedicated game server deployments (https://github.com/EmbarkStudios/quilkin). It sits between clients and game servers and provides security, access control, telemetry data, and metrics without custom-building those features into game clients/servers. It is written in Rust, released under Apache-2.0 by Embark Studios, and its concepts are inspired by Envoy Proxy (https://github.com/EmbarkStudios/quilkin). Project state is **beta**: actively developed and used in production systems, but the API may break or functionality may change between releases. Latest release: v0.9.0 (https://github.com/EmbarkStudios/quilkin).

## Pros

- **Solves the networking layer**: UDP proxying, access control, telemetry, and metrics between clients and game servers without changes to game clients/servers (https://github.com/EmbarkStudios/quilkin)
- **Open source**: Apache-2.0, written in Rust by Embark Studios (https://github.com/EmbarkStudios/quilkin)
- **Production-tracked despite beta**: actively developed and used in production systems today (https://github.com/EmbarkStudios/quilkin)
- **Familiar architecture**: concepts inspired by Envoy Proxy, easing adoption for Kubernetes-native environments (https://github.com/EmbarkStudios/quilkin)

## Cons

- **Beta API instability**: API may break or functionality may change between releases (https://github.com/EmbarkStudios/quilkin)
- **Networking layer only**: does NOT host, run, or scale game servers — needs an orchestration layer like Agones or manual Kubernetes (https://github.com/EmbarkStudios/quilkin; per `./02_Knowledge/technologies/services/agones/overview.md`)
- **Extra component to operate**: a separate proxy deployment to maintain on top of whatever platform hosts the game servers (https://github.com/EmbarkStudios/quilkin)
- **Does not answer the hosting question**: the homelab decision is how to host and scale dedicated game servers; Quilkin assumes that problem is already solved (per `./02_Knowledge/technologies/services/agones/overview.md`)

## Evaluation

- **Problem it solves**: traffic plumbing — UDP proxying, access control, telemetry — not hosting or scaling game server instances (https://github.com/EmbarkStudios/quilkin)
- **Where it sits relative to Agones**: complement for UDP ingress — a potential front layer for Agones-managed GameServers, not a substitute for the orchestration that creates, scales, and tears down servers (https://github.com/EmbarkStudios/quilkin; per `./02_Knowledge/technologies/services/agones/overview.md`)
- **Fit for this epic**: out of scope — the epic decides how to host dedicated game servers in the homelab, which Quilkin does not address (per `./02_Knowledge/technologies/services/agones/overview.md`)
- **Maturity risk**: beta — API breakage between releases is possible and expected until a stable release (https://github.com/EmbarkStudios/quilkin)
- **License**: Apache-2.0, homelab-friendly (https://github.com/EmbarkStudios/quilkin)

## Verdict

**Rejected as standalone** — Quilkin is a networking complement, not an orchestration alternative. It solves UDP traffic plumbing (proxying, access control, telemetry) but does not host or scale game servers, so it is out of scope for this epic's hosting decision. It could be revisited as a UDP-ingress component in front of an Agones deployment (per `./02_Knowledge/technologies/services/agones/overview.md` and https://github.com/EmbarkStudios/quilkin), not as a replacement for the orchestration layer.
