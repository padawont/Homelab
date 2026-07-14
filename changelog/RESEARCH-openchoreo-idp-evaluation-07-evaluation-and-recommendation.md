---
title: "OpenChoreo Evaluation Summary and Recommendation"
status: exploring
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - openchoreo
  - recommendation
  - evaluation
  - adopt-pilot-reject
sources:
  - knowledge: "knowledge/operations/internal-developer-platforms/openchoreo/what-is-openchoreo.md"
  - knowledge: "knowledge/operations/internal-developer-platforms/openchoreo/idp-platform-engineering-concepts.md"
references:
  - url: "https://openchoreo.dev/"
    title: "OpenChoreo — home"
  - url: "https://github.com/openchoreo/openchoreo"
    title: "openchoreo/openchoreo GitHub repository"
last_audit_date: 2026-06-15
---

# OpenChoreo Evaluation Summary and Recommendation

## Context

This note consolidates the per-dimension analysis (notes 01–06) into scores against issue #78's evaluation criteria, an adoption-effort estimate, risks, and a final **Adopt / Pilot / Reject** recommendation.

## Scoring against the evaluation criteria

Scale: 🟢 strong · 🟡 mixed/uncertain · 🔴 weak. (For a small developer cooperative.)

| Criterion | Score | Rationale |
|---|---|---|
| **Technical fit** — K8s-native, GitOps, multi-env, security | 🟢 | Genuinely K8s-native (CRDs), GitOps-friendly, decoupled planes, Cilium zero-trust isolation (note 01). |
| **Developer experience** — ease, self-service, reduced K8s load, learning curve | 🟢 | Component/Endpoint model + Backstage portal directly target our "strong devs, light on K8s" profile (note 02). |
| **CI/CD & delivery** | 🟢 | Coexists with our GitHub Actions; declarative promotion via DeploymentPipeline (note 03). |
| **Operational fit** — team size, maintenance, infra cost, upgrades | 🔴/🟡 | The decisive risk: heavy dependency surface (Cilium, gateway, Argo, obs) and v1.x Sandbox upgrade exposure on a tiny ops team (note 04). |
| **Integration & ecosystem** | 🟡 | Mainstream CNCF components (low lock-in), but thin community and a Cilium constraint for existing clusters (note 05). |
| **Strategic fit** — OSS sustainability, community, vendor neutrality, extensibility | 🟡 | Apache 2.0 + CNCF Sandbox + standard components = good neutrality, but single-vendor origin and early maturity add sustainability risk (note 06, note "what-is-openchoreo"). |

**Net:** strong on technical fit and DX (the *value*), uncertain on operations and maturity (the *cost/risk*).

## Estimated adoption effort

- **Pilot (recommended):** ~2–4 weeks of part-time effort by 1–2 people — single cluster (Cilium), no built-in build plane, one real service deployed and promoted, one upgrade exercised.
- **Full adoption:** materially larger — multi-plane/multi-cluster, SSO/OIDC integration, authored golden paths for our stack, an on-call/upgrade runbook, and ongoing day-2 ownership.

## Risks and limitations

- **Maturity:** CNCF Sandbox, v1.x — expect breaking changes and gaps; smaller operational track record.
- **Day-2 burden** concentrated on very few maintainers (the dominant risk).
- **Cilium dependency** complicates adopting existing non-Cilium clusters.
- **Single-vendor origin** (WSO2) — community-sustainability risk if vendor focus shifts.
- **Abstraction-vs-relocation:** value depends on the quality of golden paths *we* author.

## Recommendation: **Pilot**

Neither Adopt (operational risk unproven for our size) nor Reject (technical/DX value is real and the alternatives are not clearly better). A **time-boxed, low-footprint pilot** is the correct next step: it directly measures the one genuinely uncertain dimension — day-2 operability for a small team — at low cost and with a clean exit.

- **Go/no-go:** proceed to broader adoption only if a single maintainer can comfortably install, operate, and upgrade the pilot stack, *and* a non-expert developer can self-service deploy + promote a real service.
- **Fallback if no-go:** a self-assembled Backstage + Argo CD stack (note 06).

This recommendation is implemented as a concrete plan in [`proposals/openchoreo-idp-pilot/`](../../proposals/openchoreo-idp-pilot/) and recorded as a decision in [`adr/0008-pilot-openchoreo-idp/`](../../adr/0008-pilot-openchoreo-idp/).
