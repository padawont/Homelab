---
title: "AGENTS.md — 05_Implementations"
status: accepted
author: "padawont"
date: 2026-11-03
tags: []
sources: []
last_audit_date: 2026-11-03
related_docs: []
---

# AGENTS.md — 05_Implementations

Section purpose is owned by `./AGENTS.md` § Repository Structure (row `05_Implementations/`).

## Why have implementations?

To document how services are actually deployed. Configs drift, but docs + configs together capture the truth. When something breaks, this is the first place to look.

## When to create

After an ADR is accepted and before/during deployment. The prerequisites themselves —
an ADR plus Knowledge note(s) — are owned by `./AGENTS.md` § Dependency Rules.

## Status Lifecycle

```
draft → active
  L__> retired → (archived per ./06_Archive/AGENTS.md § Conventions)
```

- **draft**: Setting up, not yet live
- **active**: Running and maintained
- **retired**: Decommissioned

## File system layout

Example:

```
05_Implementations/node-main/
└── traefik/
    ├── overview.md
    ├── rollback.md
    └── configs/
        ├── deployment.yaml
        ├── service.yaml
        └── ingress.yaml
```

Names follow the repo naming rule (`./AGENTS.md` § General Conventions).

## Spec files

Descriptive specs record *observed* state, not intent. `spec-writer` owns them and
they are **append-only**: a correction is appended as a replacement block, never an
edit to existing content.

- `spec-cluster.md` — nodes, k3s version, namespaces
- `spec-topology.md` — ingress → service → workload wiring
- `spec-service-stack.md` — one service's deployed components

They live inside the service folder beside `overview.md`, are copied from
`./Templates/specs/`, and take `status` from the lifecycle above. Append-only
starts once the file exists: on first fill the template's own placeholder diagram
is replaced.

`runesmith` decides the `status:` value; `spec-writer` is the only agent that writes
the line, on that directive (`./.opencode/agents/runesmith.md` § Negative Constraints).
The body below it remains `spec-writer`'s append-only replacement block and is never
edited (`./.opencode/agents/spec-writer.md` § Append-Only and Diagrams).

A confirmed finding on a spec is answered by `spec-writer` as a replacement block and
never reaches `editor` (`./.opencode/REVIEW.md` § Routing); the only line that changes is
`status:`, written by `spec-writer` on `runesmith`'s directive, and the body stays
append-only.

## Frontmatter (required)

```yaml
---
title: ""
status: draft        # draft | active | retired
author: ""
date: YYYY-MM-DD
tags: []
technologies: []
related_docs: []
references:
  online: []
  repo: []
node: ""
---
```

Example:

```yaml
---
title: "Traefik ingress controller"
status: active
author: "padawont"
date: 2026-08-13
tags: [kubernetes, networking, ingress, deployment]
technologies: [traefik, kubernetes, helm]
related_docs:
  - "./04_ADRs/26-adopt-nixos-on-node-main.md"
references:
  online:
    - url: "https://doc.traefik.io/traefik/"
      title: "Traefik docs"
  repo:
    - "./04_ADRs/26-adopt-nixos-on-node-main.md"
node: node-main
---
```

See `./Templates/implementations/service.md` for a copyable template.

## Structure of overview.md

Example:

```
# Traefik Ingress Controller

## Prerequisites

Hardware, software, DNS, secrets needed.

## Deployment

Step-by-step with code blocks referencing `configs/` files.

### Pre-deploy checks
### Deploy
### Post-deploy verification

## Configuration

Env vars, config files, secrets references (point to `configs/`)

## Operations

Backup, restore, update, monitoring commands.
```

Rollback is documented separately in `rollback.md`, not in `overview.md`.

## Structure of rollback.md

Copy from `./Templates/implementations/rollback.md`. Required for every implementation, including platform bootstraps (e.g. Kubernetes reset/teardown as rollback).

```
# {Service Name} — Rollback

## Prerequisites
## Rollback steps
## Verification
```

## Conventions

- One folder per service under the relevant node
- Link back to governing ADR and relevant Knowledge notes via `related_docs`
- Every folder ships `overview.md` + `rollback.md` (+ `configs/` where applicable)
- Document the rollback procedure before deploy
- Retiring a service moves its folder to `./06_Archive/implementations/node-main/<service>/`
  — the copy is `worker`'s and the source deletion is `editor`'s, in that order — see
  `./06_Archive/AGENTS.md` § Conventions and § Frontmatter (required)
