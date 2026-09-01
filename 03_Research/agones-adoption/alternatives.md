---
title: "Alternatives index — Agones adoption"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, research, alternatives]
sources:
  - knowledge: "./02_Knowledge/technologies/services/agones/overview.md"
references:
  - url: "https://agones.dev"
    title: "Agones official site"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"
    title: "Kubernetes Deployments"
  - url: "https://www.open-match.dev"
    title: "Open Match"
  - url: "https://github.com/EmbarkStudios/quilkin"
    title: "Quilkin"
  - url: "https://aws.amazon.com/gamelift/"
    title: "Amazon GameLift"
last_audit_date: 2026-08-30
---

# Alternatives index — Agones adoption

| Technology | File | Verdict |
|---|---|---|
| Agones | ./alternative-agones.md | Selected |
| Raw Kubernetes | ./alternative-raw-kubernetes.md | Rejected — Deployments/StatefulSets + HPA, no dedicated game server lifecycle |
| Open Match | ./alternative-open-match.md | Rejected — matchmaking framework; complement, not substitute |
| Quilkin | ./alternative-quilkin.md | Rejected — UDP proxy, networking layer only |
| Amazon GameLift | ./alternative-gamelift.md | Rejected — managed SaaS, not a homelab fit |

This index supports the research question of how to host dedicated game servers
in the homelab; see ./overview.md for the full recommendation. Each technology
has its own file with a detailed evaluation. The verdicts are preliminary and
reflect the research direction: Agones (CNCF sandbox) orchestrates dedicated
game servers on Kubernetes, while the other options either cover only a slice
of that problem (matchmaking, networking) or sit outside the homelab (managed
SaaS). Facts are grounded in the Agones knowledge note
(./02_Knowledge/technologies/services/agones/overview.md) and the vendor
sources listed in the frontmatter.
