---
title: "OpenChoreo Platform Operations — Evaluation"
status: exploring
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - openchoreo
  - operations
  - day-2
  - rbac
  - observability
  - cilium
sources:
  - knowledge: "knowledge/operations/internal-developer-platforms/openchoreo/architecture-planes.md"
  - knowledge: "knowledge/operations/internal-developer-platforms/openchoreo/idp-platform-engineering-concepts.md"
references:
  - url: "https://openchoreo.dev/docs/getting-started/quick-start-guide/"
    title: "OpenChoreo — Quick Start Guide"
  - url: "https://openchoreo.dev/docs/overview/architecture/"
    title: "OpenChoreo — Architecture"
last_audit_date: 2026-06-15
---

# OpenChoreo Platform Operations — Evaluation

## Context

Assess the operational reality: installation and maintenance complexity, infrastructure requirements, scaling, security/RBAC, observability, and day-2 overhead. This is the decisive dimension for a small cooperative.

## Findings

- **Installation.** Helm-based, with a local quick start on k3d and a dev-container option. The install provisions OpenChoreo CRDs/controllers and sample abstractions.
- **Required dependencies.** A working data plane brings in **Cilium CNI + eBPF** (network policy / Guard), **Envoy Gateway** (ingress), and — if the build plane is enabled — **Argo Workflows**. The Observability Plane adds an OpenTelemetry/Prometheus/OpenSearch-style stack.
- **Infrastructure footprint.** Single-cluster all-planes is feasible for a pilot; production multi-plane/multi-cluster increases footprint materially.
- **Security / RBAC.** Multi-tenancy via Organization isolation; zero-trust network policy enforced at the Cell boundary via Cilium/eBPF. RBAC + least-privilege access through the Experience plane.
- **Observability.** First-class plane for logs/metrics/OTel traces across data and workflow planes, surfaced self-service in the portal.

## Analysis

This is where the small-COOP risk concentrates. OpenChoreo is **not a lightweight tool** — adopting it means operating Cilium, a gateway, an observability stack, and OpenChoreo's own controllers. For an organization already running Kubernetes with Cilium, the incremental burden is modest. For a team **not** already deep in this stack, the day-2 burden (upgrades across a v1.x Sandbox project, controller debugging, CNI operations) is significant and falls on a very small number of people.

Two mitigating factors: (1) the planes are decoupled, so a pilot can stay single-cluster and skip the optional build plane; (2) CNCF Sandbox status means active development but also **less operational track record** and potential breaking changes between versions — upgrade testing must be deliberate.

The core build-vs-adopt question reduces to: *does the per-developer cognitive load removed exceed the platform-team load added?* For a small COOP this is genuinely uncertain and is exactly what a time-boxed pilot must measure — not decide upfront.

## Recommendations

- Operations is the **primary risk** and the reason to **Pilot rather than Adopt** outright.
- Scope the pilot to a **single cluster, no built-in build plane** to minimize the dependency surface.
- Make day-2 cost explicit pilot evidence: record install time, one full version upgrade, and an induced-failure recovery (e.g. a broken reconciliation) during the pilot window.
- Decision gate: if a single maintainer cannot comfortably run + upgrade the pilot stack, lean Reject.
