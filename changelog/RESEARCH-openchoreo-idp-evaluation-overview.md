---
title: "OpenChoreo IDP Evaluation — Overview"
status: exploring
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - openchoreo
  - idp
  - evaluation
  - recommendation
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

# OpenChoreo IDP Evaluation — Overview

This is the single-page summary of the evaluation; the detail lives in the atomic notes listed in [README.md](README.md).

## Context

Per issue [#78](https://github.com/RunicEngines/knowledge-base/issues/78), we evaluated [OpenChoreo](https://openchoreo.dev/) — an open-source, Kubernetes-native Internal Developer Platform (Apache 2.0, CNCF Sandbox, originally from WSO2) — as a potential IDP for RunicEngines, against our current approach and the main alternatives.

## Findings (by dimension)

| Dimension | Verdict |
|---|---|
| Architecture (01) | 🟢 Genuinely K8s-native (CRDs), decoupled multi-plane, GitOps-friendly, Cilium-based isolation. |
| Developer experience (02) | 🟢 Component/Endpoint model + Backstage portal directly fit "strong devs, light on K8s". |
| CI/CD & delivery (03) | 🟢 Coexists with our GitHub Actions; declarative promotion via DeploymentPipeline. |
| Platform operations (04) | 🔴/🟡 Decisive risk — heavy dependency surface + v1.x upgrade exposure on a tiny ops team. |
| Integration & ecosystem (05) | 🟡 Mainstream CNCF components (low lock-in) but thin community + Cilium constraint. |
| Strategic fit (06–07) | 🟡 Good vendor neutrality; single-vendor origin and early maturity add risk. |

## Analysis

OpenChoreo is **strong on the value (technical fit + DX)** and **uncertain on the cost (day-2 operability for a small team)**. The realistic alternative is a self-assembled Backstage + Argo CD stack; building our own is not viable for a cooperative our size. The one genuinely unknown factor — whether a tiny team can operate and upgrade it — cannot be settled on paper.

## Recommendation: **Pilot**

Run a time-boxed, low-footprint pilot (single cluster, no built-in build plane, one real service) to measure day-2 operability and developer self-service, behind an explicit go/no-go gate. See [07-evaluation-and-recommendation.md](07-evaluation-and-recommendation.md) for the full reasoning, the pilot plan in [`proposals/openchoreo-idp-pilot/`](../../proposals/openchoreo-idp-pilot/), and the decision in [`adr/0008-pilot-openchoreo-idp/`](../../adr/0008-pilot-openchoreo-idp/).
