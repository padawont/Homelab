---
title: "OpenChoreo Integration and Ecosystem — Evaluation"
status: exploring
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - openchoreo
  - integration
  - backstage
  - argocd
  - identity
  - api-management
sources:
  - knowledge: "knowledge/operations/internal-developer-platforms/openchoreo/core-abstractions.md"
  - knowledge: "knowledge/operations/internal-developer-platforms/openchoreo/architecture-planes.md"
references:
  - url: "https://openchoreo.dev/docs/"
    title: "What is OpenChoreo"
  - url: "https://github.com/openchoreo/openchoreo"
    title: "openchoreo/openchoreo GitHub repository"
last_audit_date: 2026-06-15
---

# OpenChoreo Integration and Ecosystem — Evaluation

## Context

Assess compatibility with existing Kubernetes clusters and tooling: Argo CD, Backstage, observability stacks, identity providers, API management, and alignment with platform-engineering best practices.

## Findings

- **Existing clusters.** A DataPlane is a Kubernetes cluster, so OpenChoreo can in principle adopt existing clusters — subject to the data plane's CNI requirement (Cilium) for full network-policy/Cell isolation. This is the key compatibility constraint.
- **Backstage.** Backstage is the built-in portal, so we inherit a Backstage IDP without assembling one ourselves.
- **Argo.** Argo Workflows is the built-in build/CI engine; Argo CD/Flux interoperate at the GitOps delivery layer.
- **Observability.** Built on OpenTelemetry with Prometheus/OpenSearch-style backends — standard, swappable components.
- **Identity / API management.** Multi-tenant RBAC and access control via the Experience plane; OpenChoreo's WSO2 lineage brings API-gateway/management concepts (Envoy Gateway, and gateway abstractions for endpoints).
- **Ecosystem maturity.** Single-vendor-origin (WSO2), CNCF Sandbox, modest but active community (~1.1k stars at audit). Third-party integrations and community modules are still nascent compared to Backstage/Argo CD on their own.

## Analysis

Integration-wise OpenChoreo is built from mainstream CNCF components (Kubernetes, Cilium, Envoy, Argo, OpenTelemetry), which lowers lock-in and keeps us on technologies that are individually well-supported. The Backstage + Argo integration is a genuine head-start versus building those connections ourselves.

The notable constraint is the **Cilium dependency** for data planes — adopting an existing cluster that uses a different CNI may require re-platforming the cluster networking, which is non-trivial. The thin ecosystem also means we should expect to read source and file issues rather than find a pre-built integration for everything.

## Recommendations

- For the pilot, use a **fresh cluster with Cilium** rather than retrofitting an existing one, to isolate the evaluation from CNI-migration risk.
- Confirm identity-provider integration (our chosen SSO/OIDC) early — it gates real multi-developer use.
- Favour the standard OTel/Prometheus backends so observability data stays portable if we later reject OpenChoreo.
