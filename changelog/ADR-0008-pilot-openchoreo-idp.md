# ADR-0008: Pilot OpenChoreo IDP

## README.md

# ADR 0008: Pilot OpenChoreo as an Internal Developer Platform

Decision to run a time-boxed, low-footprint pilot of [OpenChoreo](https://openchoreo.dev/) — rather than adopt or reject it outright — to resolve the one decisive unknown: day-2 operability for a small cooperative.

[overview.md](./overview.md) contains the full decision record in MADR format.

Related: `research/openchoreo-idp-evaluation/` (evaluation), `proposals/openchoreo-idp-pilot/` (the pilot plan), issue [#78](https://github.com/RunicEngines/knowledge-base/issues/78).

## overview.md

---
adr: 0008
title: "Pilot OpenChoreo as an Internal Developer Platform"
author: "Noar Qerimi (noarqerimi)"
status: draft
topic: "internal-developer-platform"
technology: "Kubernetes"
date-proposed: 2026-06-15
history: "https://github.com/RunicEngines/knowledge-base/pull/79"
context: >
  RunicEngines developers need a consistent, self-service path from code to a
  running application without each person mastering the full Kubernetes,
  networking, and CI/CD stack. OpenChoreo is an open-source, Kubernetes-native
  Internal Developer Platform (Apache 2.0, CNCF Sandbox, originally from WSO2).
  Research (research/openchoreo-idp-evaluation/) found it strong on technical
  fit and developer experience but with uncertain day-2 operational cost for a
  small cooperative and early (v1.x, CNCF Sandbox) maturity. That operational
  uncertainty is the only thing blocking a confident decision.
decision: >
  Neither adopt nor reject OpenChoreo yet. Run a time-boxed, low-footprint
  pilot (single cluster, no built-in build plane, one real sample service)
  per proposals/openchoreo-idp-pilot/ to measure whether a tiny team can
  install, operate, and upgrade it while a non-expert developer self-services
  a deployment. A go/no-go gate decides next steps in a follow-up ADR.
consequences: >
  Low-cost, reversible way to resolve the one genuine unknown before any
  commitment; produces written day-2 evidence. Costs ~2-4 weeks part-time for
  1-2 people. Does not commit RunicEngines to OpenChoreo. If the gate fails,
  the documented fallback is a self-assembled Backstage + Argo CD stack.
sources:
  - "../../knowledge/operations/internal-developer-platforms/openchoreo/what-is-openchoreo.md"
  - "../../knowledge/operations/internal-developer-platforms/openchoreo/architecture-planes.md"
  - "../../knowledge/operations/internal-developer-platforms/openchoreo/core-abstractions.md"
  - "../../knowledge/operations/internal-developer-platforms/openchoreo/idp-platform-engineering-concepts.md"
references:
  - "https://github.com/RunicEngines/knowledge-base/issues/78"
  - "https://openchoreo.dev/"
  - "https://openchoreo.dev/docs/overview/architecture/"
  - "https://github.com/openchoreo/openchoreo"
---

# ADR 0008: Pilot OpenChoreo as an Internal Developer Platform

## Status

Draft (proposed 2026-06-15)

## Context and Problem Statement

As RunicEngines grows, more developers will deploy and operate more services across more repositories. Plain Kubernetes exposes a large surface area — Deployments, Services, Ingress, network policy, RBAC, CI pipelines, GitOps — and expecting every developer in the cooperative to master it does not scale. We want a self-service path from code to a running application that reduces this cognitive load while keeping us on open, vendor-neutral technology.

[OpenChoreo](https://openchoreo.dev/) is an open-source, Kubernetes-native Internal Developer Platform (Apache 2.0, CNCF Sandbox, originally from WSO2) that packages golden-path abstractions, a Backstage portal, CI/CD, GitOps, and observability on top of Kubernetes.

The research in `research/openchoreo-idp-evaluation/` evaluated it across architecture, developer experience, CI/CD, operations, integration, and alternatives. Its conclusion: OpenChoreo is **strong on technical fit and developer experience** (the value) but **uncertain on day-2 operability** for a team our size and is an **early-maturity project** (v1.x, CNCF Sandbox, single-vendor origin). The realistic alternative is a self-assembled Backstage + Argo CD stack.

The problem: we cannot responsibly **Adopt** (the operational cost is unproven for our scale) or **Reject** (the value is real and no alternative is clearly superior) on current evidence. The one decisive unknown — day-2 operability for a tiny team — can only be resolved by hands-on use.

## Decision

**Run a time-boxed, low-footprint pilot of OpenChoreo rather than adopting or rejecting it now.**

The pilot is specified in `proposals/openchoreo-idp-pilot/`:

- A single Kubernetes cluster (Cilium CNI) hosting the Control, Data, Observability, and Experience planes.
- One real sample service modelled as a `Component`/`Endpoint`, with one platform-authored `ComponentType` golden path and a two-environment `DeploymentPipeline`.
- Image builds remain in GitHub Actions; the built-in Workflow/Build Plane (Argo Workflows), multi-cluster topology, and production traffic are explicitly out of scope.
- Four phases — stand up, golden path, self-service deploy/promote, day-2 (upgrade + failure recovery) — ending at a **go/no-go gate**.

The gate passes only if **both**: (1) a single maintainer can comfortably install, operate, and upgrade the stack; and (2) a non-expert developer can self-service deploy and promote a real service. The outcome (Adopt or Reject) will be recorded in a follow-up ADR.

This is the right decision because it resolves the only genuine uncertainty at low, bounded cost and with a clean exit, instead of committing to (or dismissing) a platform on incomplete evidence.

## Consequences

**Easier**

- Resolves the day-2 operability question with real evidence before any commitment.
- Reversible and cheap (~2–4 weeks part-time, 1–2 people, throwaway cluster).
- Produces reusable artifacts (a `ComponentType` golden path, an install/upgrade runbook) even if we ultimately reject.
- Keeps GitHub Actions builds untouched, limiting blast radius.

**Harder / costs**

- Consumes scarce maintainer time during the pilot window.
- Requires standing up Cilium + gateway + observability even for a minimal install.
- A draft decision: the real adopt/reject call is deferred to a follow-up ADR, so this ADR is intentionally provisional.

## Considered Options

1. **Adopt OpenChoreo now** — rejected: day-2 operational cost is unproven for our size; committing to a v1.x Sandbox project without hands-on evidence is high risk.
2. **Reject OpenChoreo now** — rejected: technical fit and DX are strong and no alternative is clearly better; rejecting without trial discards real value.
3. **Pilot (chosen)** — bounded, reversible test of the one decisive unknown.
4. **Skip OpenChoreo; assemble Backstage + Argo CD instead** — deferred, not rejected: this is the explicit fallback if the pilot's go/no-go gate fails (`research/openchoreo-idp-evaluation/06-alternatives-comparison.md`).

## Compliance

- The pilot follows RunicEngines GitHub conventions (ADR 0002): branch naming, conventional commits, PR workflow.
- Pilot evidence (install time, upgrade outcome, failure recovery, self-service result) is captured back into `research/openchoreo-idp-evaluation/` and summarised in the follow-up ADR.
- This ADR moves from `draft` to `final` (or `cancelled`) once the pilot's go/no-go decision is made; `history` will reference the implementing PR.
