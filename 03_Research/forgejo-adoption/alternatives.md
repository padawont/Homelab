---
title: "Forgejo adoption research — alternatives index"
status: draft
author: "padawont"
date: 2026-08-30
tags: [forgejo, gitea, gitlab, gogs, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/forgejo/overview.md"
references:
  - url: "https://forgejo.org/compare-to-gitea/"
    title: "Forgejo comparison with Gitea"
last_audit_date: 2026-08-30
---

# Alternatives index — Forgejo adoption

| Technology | File | Verdict |
|---|---|---|
| Forgejo | ./alternative-forgejo.md | Selected |
| Gitea | ./alternative-gitea.md | Rejected — near-parity but for-profit corporate governance |
| GitLab CE | ./alternative-gitlab-ce.md | Rejected — heavy resource footprint, overkill for homelab |
| Gogs | ./alternative-gogs.md | Rejected — too minimal, no built-in CI or packages |

The full recommendation and reasoning live in ./overview.md. Each alternative above was evaluated against the same six dimensions: resource footprint, k3s deploy effort, CI, GitHub parity, upgrade path, and maintenance burden. Forgejo wins on the combination of low footprint, simple k3s deployment, and community-governed development.
