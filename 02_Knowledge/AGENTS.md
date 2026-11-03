---
title: "AGENTS.md — 02_Knowledge"
status: accepted
author: "padawont"
date: 2026-11-03
tags: []
sources: []
last_audit_date: 2026-11-03
related_docs: []
---

# AGENTS.md — 02_Knowledge

Structured reference notes on tech concepts, syntax guides, and foundational theory.

## Why have knowledge notes?

- **Reference**: something to come back to when deploying or troubleshooting
- **Learning**: writing things down solidifies understanding
- **Research input**: Knowledge is the foundation that Research builds upon
- **Onboarding**: a single place to understand how things work

## When to create

After an idea is promoted, or whenever you learn something worth documenting.

## Status Lifecycle

```
draft → accepted
  L__> archived → (move to 06_Archive/knowledge/)
```

- **draft**: Outline or incomplete
- **accepted**: Reviewed and finalized
- **archived**: Stale or superseded

## File system layout

```
02_Knowledge/
└── technologies/
    ├── tools/           # CLI tools, software utilities
    ├── services/        # specific services (forgejo, homepage, etc.)
    ├── kubernetes/      # k8s concepts, patterns, manifests
    └── hardware/        # physical hardware, specs, diagrams
```

Names follow the repo naming rule (`./AGENTS.md` § General Conventions). Each topic is a folder with atomic notes inside. Max 3 levels deep.

## Frontmatter (required)

```yaml
---
title: ""
status: draft        # draft | accepted | archived
author: ""
date: YYYY-MM-DD
tags: []
sources:
  - url: ""
    title: ""
last_audit_date: YYYY-MM-DD
related_docs: []
---
```

Example:

```yaml
---
title: "Ingress controllers in Kubernetes"
status: draft
author: "padawont"
date: 2026-08-13
tags: [kubernetes, networking, ingress]
sources:
  - url: "https://kubernetes.io/docs/concepts/services-networking/ingress/"
    title: "Kubernetes Ingress docs"
last_audit_date: 2026-08-13
related_docs:
  - "./05_Implementations/node-main/k3s/overview.md"
---
```

See `./Templates/knowledge/note.md` for a copyable template.

## Structure

```
# Title

## Overview
What is this concept? Why does it matter?

## Details
Deep dive with examples.

## Sources / Further Reading
```

## Conventions

- **Atomic notes**: one concept per file; split at the 150-line limit (`./AGENTS.md` § Atomic File Rule).
- Both abstract examples and real configs are welcome — label each block as "Example — abstract", "Example — planned/abstract", or "Example — real config"
- Set `last_audit_date` on every edit; re-audit weekly
- Use `related_docs` to cross-link to implementations; the reverse direction is defined in `./05_Implementations/AGENTS.md` § Conventions

### Example blocks

Example — abstract:

```yaml
# simplified, vendor-neutral
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata: { name: example-ingress }
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend: { service: { name: app-service, port: { number: 80 } } }
```

Example — planned/abstract (Forgejo is not deployed):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata: { name: forgejo-ingress, namespace: forgejo }
spec:
  ingressClassName: traefik
  tls: [{ hosts: [git.homelab.local], secretName: forgejo-tls }]
  rules:
    - host: git.homelab.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend: { service: { name: forgejo-http, port: { number: 3000 } } }
```

## Agent Behaviour

Role permissions, handoff contracts, and escalation are shared across sections — see the
roster in `./.opencode/WORKFLOW.md`; the review facets are owned by `./.opencode/REVIEW.md`
§ The Five Facets, and the report shape by § Facet Report.
