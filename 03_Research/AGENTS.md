# AGENTS.md — 03_Research

Deep dives that combine Ideas + Knowledge + online docs into a concrete plan for an ADR.

## Why have research?

To make informed decisions. Research is the bridge between "this seems interesting" (Knowledge) and "let's commit" (ADR). It evaluates alternatives and produces the raw material for the ADR.

## When to create

Before making a significant homelab decision. Research is required before an ADR.

## Status Lifecycle

```
draft → accepted → (proceed to 04_ADRs/)
  L__> archived → (move to 06_Archive/research/)
```

- **draft**: Gathering data, evaluating options
- **accepted**: Plan is ready — create an ADR
- **archived**: Not viable or superseded

## Inputs

- Ideas from `./01_Ideas/` (what sparked this)
- Knowledge from `./02_Knowledge/` (foundational understanding)
- Online documentation (vendor docs, articles, comparisons)

## File system layout

Example:

```
03_Research/ingress-comparison/
├── overview.md                  # goal, plan for ADR, recommendation
├── alternatives.md              # index of all alternatives considered
├── alternative-traefik.md       # detailed evaluation of one technology
├── alternative-nginx.md
└── alternative-haproxy.md
```

All names in kebab-case.

## Frontmatter (required)

```yaml
---
title: ""
status: draft        # draft | accepted | archived
author: ""
date: YYYY-MM-DD
tags: []
sources:
  - knowledge: ""
references:
  - url: ""
    title: ""
last_audit_date: YYYY-MM-DD
---
```

Example:

```yaml
---
title: "Ingress controller comparison"
status: draft
author: "padawont"
date: 2026-08-13
tags: [kubernetes, networking, ingress]
sources:
  - knowledge: "./02_Knowledge/technologies/kubernetes/ingress.md"
references:
  - url: "https://nginx.org/en/docs/"
    title: "NGINX documentation"
  - url: "https://doc.traefik.io/traefik/"
    title: "Traefik documentation"
last_audit_date: 2026-08-13
---
```

See `./Templates/research/overview.md` for a copyable template.

## Structure of overview.md

```
# Title

## Goal

What question am I answering? Which idea(s) sparked this?

## Alternatives

See ./alternatives.md for a full index of all technologies considered.
Each alternative has its own file: ./alternative-traefik.md, ./alternative-nginx.md, etc.

## Plan for ADR

- Recommended technology and why
- How it fits into the existing homelab
- Architecture overview
- Dependencies and integration points
- Risks and mitigation

## Recommendation

**approve** / **reject**
```

## Structure of alternative-{name}.md

```
# Alternative: Traefik

## Overview

Brief description of the technology.

## Pros

## Cons

## Evaluation

How it performs across relevant dimensions (complexity, fit, performance, security).

## Verdict

Why this was or wasn't selected.
```

## Structure of alternatives.md

```
# Alternatives index — Ingress comparison

| Technology | File | Verdict |
|---|---|---|
| Traefik | ./alternative-traefik.md | Selected |
| NGINX | ./alternative-nginx.md | Rejected — complexity |
| HAProxy | ./alternative-haproxy.md | Rejected — no k8s CRDs |
```

## Conventions

- Each alternative technology gets its own file under the topic folder
- Must reference at least one Knowledge note or online source
- Output must be detailed enough to write the ADR directly from the overview
- If rejected, move entire topic folder to `./06_Archive/research/`
