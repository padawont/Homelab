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

All names in kebab-case. Each topic is a folder with atomic notes inside. Max 3 levels deep.

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
---
```

See `./Templates/knowledge/note.md` for a copyable template.

## Structure

```
# Title

Overview — what is this concept? Why does it matter?

## Details

Deep dive with examples.

## Sources / Further Reading
```

Example — abstract code snippet:

```yaml
# simplified, vendor-neutral
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: example-service
                port:
                  number: 80
```

Example — real config from node-main:

```yaml
# actual running config, may drift from this doc
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: forgejo-ingress
  namespace: forgejo
spec:
  ingressClassName: traefik
  rules:
    - host: git.homelab.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: forgejo-http
                port:
                  number: 3000
```

## Conventions

- **Atomic notes**: one concept per file. When a file hits 150 lines, split it.
- Both abstract examples and real configs are welcome — label each block as "Example — abstract" or "Example — real config"
- Set `last_audit_date` on every edit; re-audit weekly
- Use `related_docs` to cross-link to implementations and vice-versa
