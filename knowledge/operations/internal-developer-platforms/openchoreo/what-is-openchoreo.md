---
title: "What is OpenChoreo"
status: draft
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - openchoreo
  - idp
  - platform-engineering
  - kubernetes
  - cncf
sources:
  - url: "https://openchoreo.dev/"
    title: "OpenChoreo — home"
  - url: "https://openchoreo.dev/docs/"
    title: "What is OpenChoreo"
  - url: "https://github.com/openchoreo/openchoreo"
    title: "openchoreo/openchoreo GitHub repository"
  - url: "https://www.cncf.io/projects/openchoreo/"
    title: "CNCF — OpenChoreo project (Sandbox)"
last_audit_date: 2026-06-15
---

# What is OpenChoreo

OpenChoreo is an **open-source Internal Developer Platform (IDP) for Kubernetes**. It provides development and architecture abstractions, a Backstage-powered developer portal, application CI/CD, GitOps, and observability — a complete platform layer that lets developers (and AI agents) build, deploy, and operate applications without managing raw Kubernetes resources directly. Its stated design principle is that it "does not obscure Kubernetes; rather, it augments it into a complete developer platform."

## Origin, licensing, and governance

| Attribute | Value |
|---|---|
| License | Apache 2.0 |
| Originator | WSO2 (donated the project) |
| Governance | CNCF **Sandbox** project (accepted 2026-01-06) |
| Repository | `github.com/openchoreo/openchoreo` |
| Latest release (at audit) | v1.1.1 (May 2026) |
| Activity (at audit) | ~1.1k GitHub stars; active development (28 releases, several thousand commits) |

OpenChoreo is the open-source core derived from WSO2's commercial **Choreo** platform. As a CNCF **Sandbox** project it is in the earliest CNCF maturity tier (below Incubating and Graduated) — adopters should treat APIs and operational practices as still-evolving.

## What problem it solves

Plain Kubernetes is powerful but exposes a large surface area: developers must understand Deployments, Services, Ingress, network policy, RBAC, CI pipelines, and GitOps tooling to ship a single service. OpenChoreo raises the level of abstraction:

- Developers declare **Components** (services, web apps, scheduled tasks) and **Endpoints**, and the platform reconciles them into running workloads.
- A platform team defines **golden paths** (via `ComponentType` and `Trait` templates) that encode organizational standards once, so every team deploys consistently.
- Operations (logs, metrics, traces, promotion across environments) are exposed through a self-service portal, CLI, and API.

## Where it fits in the IDP landscape

OpenChoreo is a **Kubernetes-native, self-hosted, open-source** IDP. This distinguishes it from SaaS IDPs (e.g. Port, Humanitec) and from assemble-it-yourself stacks (Backstage + Argo CD + Crossplane). It is a single integrated product spanning portal, build, deploy, and observability rather than a catalogue/portal that you wire to external delivery tooling. See [architecture-planes.md](architecture-planes.md) for the runtime architecture, [core-abstractions.md](core-abstractions.md) for its resource model, and [idp-platform-engineering-concepts.md](idp-platform-engineering-concepts.md) for the general IDP background.
