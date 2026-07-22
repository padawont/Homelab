---
title: "Dagger — Knowledge Section Rules"
status: draft
author: "padawont"
date: 2026-07-22
tags: ["dagger", "ci-cd", "knowledge-rules"]
sources:
  - url: "https://docs.dagger.io"
    title: "Dagger Documentation"
  - url: "https://github.com/padawont/Homelab/issues/6"
    title: "Issue #6 — Dagger.io knowledge docs and deploy"
last_audit_date: 2026-07-22
related_configs:
  - configs-and-adr/node-main/kubernetes/dagger-engine.yaml
  - deployment/procedures/setup-dagger.md
  - deployment/pipelines/dagger-pipeline.yml
---

# Dagger — Section Rules

Rules and conventions for Dagger-related documentation in this repository.

## In Scope

- **Python SDK only** — this repo uses Python (`dagger-io` PyPI package). No Go, TypeScript, Java, or other SDKs.
- **Local-first** — pipelines must run identically on devbox and in CI (Forgejo Actions).
- **Engine auto-provisioning** — default approach. Persistent engine on node-1 is optional.
- **DevBox integration** — Dagger CLI is installed via devbox, not system-wide.

## Out of Scope

- Dagger Cloud or Dagger Enterprise features
- High-availability Dagger Engine cluster
- Go SDK or TypeScript SDK
- Writing the actual test pipeline (covered in Issue #7)

## Cross-Referencing

Knowledge docs about Dagger should link to:
- `configs-and-adr/node-main/kubernetes/dagger-engine.yaml` — persistent engine manifest
- `deployment/procedures/setup-dagger.md` — setup guide
- `deployment/pipelines/dagger-pipeline.yml` — pipeline config
- `.forgejo/workflows/ci.yml` — CI workflow trigger

## Frontmatter

All Dagger docs must include:
- `sources` — official Dagger docs and relevant community references
- `last_audit_date` — date of last accuracy review
- `tags` — at minimum `dagger` and topic-specific tags
- `related_configs` — where applicable
