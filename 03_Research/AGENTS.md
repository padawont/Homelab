---
title: "AGENTS.md — 03_Research"
status: accepted
author: "padawont"
date: 2026-11-03
tags: []
sources: []
last_audit_date: 2026-11-03
related_docs: []
---

# AGENTS.md — 03_Research

Section purpose is owned by `./AGENTS.md` § Repository Structure (row `03_Research/`).

## Why have research?

To make informed decisions. Research is the bridge between "this seems interesting" (Knowledge) and "let's commit" (ADR). It evaluates alternatives and produces the raw material for the ADR.

## When to create

Before making a significant homelab decision — an ADR requires a Research doc (`./AGENTS.md` § Dependency Rules).

## Status Lifecycle

```
draft → accepted → (proceed to 04_ADRs/)
  L__> archived → (move to 06_Archive/research/)
```

- **draft**: Gathering data, evaluating options
- **accepted**: Plan is ready — create an ADR
- **archived**: Not viable or superseded

## Inputs

`./AGENTS.md` § Content Pipeline — row **Knowledge → Research**.

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

Names follow the repo naming rule (`./AGENTS.md` § General Conventions).

## Frontmatter (required)

Applies to every file in the topic folder — `overview.md`, `alternatives.md` and
`alternative-{name}.md` all carry the same keys below. The `alternatives.md` and
`alternative.md` templates are body-only snippets, per `./Templates/AGENTS.md`
§ Conventions: when copying one, wrap its body in this frontmatter before saving it as
`alternatives.md` or `alternative-{name}.md`.

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
  - knowledge: "./02_Knowledge/technologies/kubernetes/concepts/ingress.md"
references:
  - url: "https://nginx.org/en/docs/"
    title: "NGINX documentation"
  - url: "https://doc.traefik.io/traefik/"
    title: "Traefik documentation"
last_audit_date: 2026-08-13
---
```

See `./Templates/research/overview.md`, `./Templates/research/alternatives.md` and
`./Templates/research/alternative.md` for copyable templates — the two fragment templates
are bodies only and need the frontmatter above.

## Structure of overview.md

```
# Title

## Goal

What question am I answering? Which idea(s) sparked this?

## Alternatives

See ./alternatives.md for a full index; each alternative has its own file (./alternative-traefik.md, ./alternative-nginx.md, etc.)

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
- Each research topic requires at least 3 `alternative-{name}.md` files
- Must reference at least one Knowledge note or online source (`./AGENTS.md` § Dependency Rules)
- Output must be detailed enough to write the ADR directly from the overview
- If rejected, archive the entire topic folder to `./06_Archive/research/` — see `./06_Archive/AGENTS.md` § Conventions
