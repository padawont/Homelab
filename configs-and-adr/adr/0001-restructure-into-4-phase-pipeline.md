---
# This is a MADR-style Architecture Decision Record
status: accepted
date: 2026-07-19
related_configs:
  - configs-and-adr/node-main/
---

# ADR 0001 — Restructure Repo into 4-Phase Pipeline

## Context

The Homelab repository had three loosely coupled sections — `configs/`, `knowledge/`, `changelog/` — with several structural problems: content boundary bleed between homelab-specific and generic content, orphaned dot-directories (`.research/`, `.validation/`), naming skew (`node-main` vs `node-1`), and no documented pipeline for how content flows from idea through deployment to status.

## Decision

Restructure the repository into a 4-phase pipeline that enforces clear content placement and establishes a documented workflow:

| Phase | Directory | Purpose |
|-------|-----------|---------|
| 1 | `knowledge/` | Research, reference docs, hardware specs (homelab-relevant only) |
| 2 | `configs-and-adr/` | Node configs, K8s manifests, architecture decisions |
| 3 | `deployment/` | CI/CD pipelines, deployment procedures, Helm values |
| 4 | `status/` | Cluster state snapshots, version inventory, health |

Key changes:
- Renamed `configs/` → `configs-and-adr/` to include architecture decision records
- Removed `changelog/`, `.research/`, `.validation/` (content relocated or deleted)
- Created `deployment/` and `status/` directories with subdirectory scaffolding
- Collapsed `knowledge/tooling/` into `knowledge/operations/` for homelab-relevant content; flagged generic tooling for weekly upstream pruning
- Added `.gitignore` entry for CI-generated status snapshots

## Consequences

- Unambiguous content placement — every file has a clear home phase
- Generic tooling docs remain in the repo (flagged, not deleted) until the weekly pruning skill handles them
- ADRs are co-located with configs, keeping architectural decisions close to the configurations they inform
- Future node additions follow the same `configs-and-adr/node-<role>/` pattern
