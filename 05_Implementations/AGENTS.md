# AGENTS.md — 05_Implementations

Live running setups — deployment procedures, configs, and operational notes.

## Why have implementations?

To document how services are actually deployed. Configs drift, but docs + configs together capture the truth. When something breaks, this is the first place to look.

## When to create

After an ADR is accepted and before/during deployment.

## Status Lifecycle

```
draft → active
  L__> retired → (move to 06_Archive/implementations/)
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
    └── configs/
        ├── deployment.yaml
        ├── service.yaml
        └── ingress.yaml
```

All names in kebab-case.

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
  - "./04_ADRs/42-deploy-traefik-ingress.md"
references:
  online:
    - url: "https://doc.traefik.io/traefik/"
      title: "Traefik docs"
  repo:
    - "./04_ADRs/42-deploy-traefik-ingress.md"
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

## Rollback

How to revert the deployment.
```

## Conventions

- One folder per service under the relevant node
- Link back to governing ADR and relevant Knowledge notes via `related_docs`
- Document rollback before deploy
- `active` → `retired` transition: move entire service folder to `./06_Archive/implementations/`
