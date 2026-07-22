---
title: "Dagger — Overview"
status: draft
author: "padawont"
date: 2026-07-22
tags: ["dagger", "ci-cd", "overview", "architecture"]
sources:
  - url: "https://docs.dagger.io"
    title: "Dagger Documentation"
  - url: "https://docs.dagger.io/getting-started/concepts"
    title: "Dagger Core Concepts"
  - url: "https://pypi.org/project/dagger-io/"
    title: "dagger-io on PyPI"
last_audit_date: 2026-07-22
related_configs:
  - configs-and-adr/node-main/kubernetes/dagger-engine.yaml
---

# Dagger Overview

Dagger is a programmable CI/CD engine created by Solomon Hykes (Docker co-founder) that solves the "works on my machine" problem for CI/CD pipelines.

## What Is Dagger?

Dagger replaces YAML-based pipeline definitions with code written in real programming languages (Python, Go, TypeScript, etc.). Pipelines execute inside containers orchestrated by a **BuildKit engine**, making them fully portable — the same pipeline runs identically on a developer's laptop, a CI runner, or in production.

## Architecture

```
User (CLI / SDK / GraphQL)
        │
        ▼
  Dagger Engine  ──►  BuildKit
        │                  │
        ▼                  ▼
  GraphQL API        OCI Containers
        │
        ▼
  SDKs (Python, Go, TS, ...)
```

- **Dagger Engine** — core runtime that combines an execution engine, universal type system, data layer, and module system
- **BuildKit** — underlying container build orchestrator (same engine used by `docker build`)
- **GraphQL API** — all operations are expressed as typed GraphQL queries, accessible via CLI, SDKs, or raw API calls
- **SDKs** — language-specific wrappers over the GraphQL API (8 languages: Python, Go, TypeScript, PHP, Java, .NET, Elixir, Rust)

## Four Pillars

| Pillar | Description |
|---|---|
| **Programmable** | Pipelines are code — loops, conditionals, functions, type safety, IDE support |
| **Local-first** | Develop and test pipelines locally without pushing to CI |
| **Repeatable** | Content-addressed caching ensures consistent results |
| **Observable** | Built-in OpenTelemetry traces on every operation |

## Key Benefits for the Homelab

- **Portability** — pipelines run identically on devbox and in Forgejo Actions
- **Python-native** — define pipelines with the `dagger-io` package, async API
- **Caching** — fine-grained container caching for fast re-runs
- **Vendor independence** — not locked to GitHub Actions or any CI platform
