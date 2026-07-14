---
title: "Internal Developer Platforms and Platform Engineering — Concepts"
status: draft
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - idp
  - platform-engineering
  - golden-paths
  - self-service
  - developer-experience
sources:
  - url: "https://platformengineering.org/blog/what-is-platform-engineering"
    title: "Platform Engineering — What is platform engineering"
  - url: "https://tag-app-delivery.cncf.io/whitepapers/platforms/"
    title: "CNCF Platforms White Paper"
last_audit_date: 2026-06-15
---

# Internal Developer Platforms and Platform Engineering — Concepts

This note gives the vendor-neutral background needed to evaluate any IDP (including OpenChoreo) objectively. It is the conceptual baseline the research draws on so that product-specific claims can be measured against general expectations.

## What an Internal Developer Platform is

An **Internal Developer Platform (IDP)** is a self-service layer, built and maintained by a platform team, that lets application developers provision environments and deploy/operate applications on their own — without filing tickets or learning the full underlying infrastructure stack. It is the *product* that platform engineering builds for the internal "customer," the developer.

An IDP typically bundles several capability planes (the CNCF Platforms White Paper frames them as): application development, build/integration, deployment, monitoring/observability, security, and infrastructure orchestration — exposed through a unified interface (portal, CLI, API).

## Core concepts

- **Self-service** — developers perform common actions (create environment, deploy, view logs, roll back) without human hand-offs.
- **Golden paths / paved roads** — opinionated, pre-approved templates for the common case. They encode best practices so the easy path is also the compliant path. Developers can deviate, but the default is supported and secure.
- **Abstraction without lock-in** — the platform hides incidental complexity (YAML, networking, RBAC) while still running on standard primitives (e.g. Kubernetes), so teams are not trapped.
- **Standardization by default** — consistent build, deploy, and observability across teams reduces drift and operational surprises.
- **Platform as a product** — the IDP has users, a roadmap, and feedback loops; adoption is earned by developer experience, not mandated.

## Why teams adopt one

- Reduce cognitive load on application developers.
- Shorten lead time from commit to running software.
- Enforce security/compliance via the paved road rather than after-the-fact review.
- Reduce duplicated, divergent per-team tooling.

## The trade-off to watch

An IDP **relocates** complexity onto a small platform team rather than eliminating it. For a small cooperative, the key question is whether the maintenance burden of running the platform is *less* than the aggregate burden it removes from developers. Buying/adopting an integrated open-source IDP (like OpenChoreo) versus assembling one (Backstage + Argo CD + Crossplane) versus a SaaS IDP (Port, Humanitec) is fundamentally a build-vs-buy-vs-adopt decision — analysed in `research/openchoreo-idp-evaluation/06-alternatives-comparison.md`.
