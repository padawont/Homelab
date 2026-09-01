---
title: "Alternative: Amazon GameLift"
status: draft
author: "padawont"
date: 2026-08-30
tags: [gamelift, aws, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/agones/overview.md"
references:
  - url: "https://aws.amazon.com/gamelift/"
    title: "Amazon GameLift"
last_audit_date: 2026-08-30
---

# Alternative: Amazon GameLift

## Overview

Amazon GameLift is a fully managed AWS service for hosting dedicated game servers. The product is now split into **GameLift Servers** — deploy, operate, and scale high-performance dedicated game servers for session-based multiplayer, with predictive scaling up to 100M concurrent players and matchmaking — and **GameLift Streams** — game streaming up to 1080p/60fps (https://aws.amazon.com/gamelift/). As a managed SaaS, AWS runs the fleet management; there is no self-hosted Kubernetes control plane to operate. It is aimed at large-scale commercial games (https://aws.amazon.com/gamelift/), in contrast to the self-hosted Agones model (./02_Knowledge/technologies/services/agones/overview.md).

## Pros

- **Zero operations**: fleet management, scaling, and matchmaking are fully managed by AWS (https://aws.amazon.com/gamelift/)
- **Enterprise-grade scaling**: predictive scaling built for up to 100M concurrent players (https://aws.amazon.com/gamelift/)
- **Global footprint**: game sessions can be placed across AWS regions to keep latency low for players (https://aws.amazon.com/gamelift/)
- **No cluster maintenance**: no control-plane components to install or patch — nothing like Agones' controller, extensions, allocator, or ping deployments to run (https://aws.amazon.com/gamelift/, ./02_Knowledge/technologies/services/agones/overview.md)

## Cons

- **Managed SaaS dependency**: AWS runs the fleet — contradicts the homelab's self-hosted constraint (https://aws.amazon.com/gamelift/)
- **Ongoing AWS cost**: pay-per-use for servers and bandwidth, with no way to run it on the homelab's own hardware (https://aws.amazon.com/gamelift/)
- **No local control**: cloud-only — no on-prem/self-hosted option, so the homelab would be entirely dependent on AWS (https://aws.amazon.com/gamelift/)
- **Overkill for a personal homelab**: designed for large-scale commercial titles, not a single-node k3s lab (https://aws.amazon.com/gamelift/)

## Evaluation

- **Self-hosted-over-managed constraint**: fails — GameLift is external SaaS, so the homelab would host nothing; Agones stays on-cluster (https://aws.amazon.com/gamelift/, ./02_Knowledge/technologies/services/agones/overview.md)
- **Cost**: per-use AWS spend that continues as long as fleets run — no free/self-managed tier (https://aws.amazon.com/gamelift/)
- **Control**: none locally — fleet operations, scaling policy, and matchmaking all live in AWS (https://aws.amazon.com/gamelift/)
- **Fit with node-main k3s**: none — GameLift never touches the cluster; no deployment on `node-main` is possible or needed (./02_Knowledge/technologies/services/agones/overview.md)
- **Role in comparison**: documents the managed SaaS extreme of the spectrum; useful as a contrast but not a homelab option (https://aws.amazon.com/gamelift/)

## Verdict

**Rejected** — managed SaaS (https://aws.amazon.com/gamelift/) conflicts with the homelab's self-hosted constraint and adds ongoing AWS cost; it is included for comparison only per the epic scope. See `./overview.md` and `./alternatives.md`.
