---
title: "OpenChoreo IDP Pilot Plan"
status: draft
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - openchoreo
  - idp
  - platform-engineering
  - kubernetes
  - pilot
version: 1
toc: false
related_research:
  - "research/openchoreo-idp-evaluation/"
related_adrs:
  - "adr/0008-pilot-openchoreo-idp/"
  - "adr/0002-github-etiquettes/"
---

# Motivation

RunicEngines developers need a consistent, self-service path from code to a running application without each person mastering the full Kubernetes, networking, and CI/CD stack. The research in `research/openchoreo-idp-evaluation/` found that [OpenChoreo](https://openchoreo.dev/) — an open-source, Kubernetes-native Internal Developer Platform (Apache 2.0, CNCF Sandbox) — is **strong on technical fit and developer experience** but carries **uncertain day-2 operational cost** for a small cooperative, and is an early-maturity (v1.x, CNCF Sandbox) project.

That uncertainty is the whole decision. The research recommendation is therefore **Pilot**, not Adopt or Reject: run a small, time-boxed, low-footprint evaluation that directly measures the single genuinely unknown dimension — *can a tiny team install, operate, and upgrade OpenChoreo while a non-expert developer self-services a real deployment?* — at low cost and with a clean exit.

This proposal defines **how** we run that pilot: scope, architecture, phases, success/exit criteria, who runs it, and the go/no-go gate. It deliberately does **not** commit RunicEngines to adopting OpenChoreo; adoption would be a separate decision recorded in a future ADR after the pilot.

\clearpage

# Proposed Changes

We will stand up a **minimal OpenChoreo installation on a single throwaway cluster** and use it to deploy and operate one real sample service. The pilot is intentionally narrow:

**In scope**

- A single Kubernetes cluster (local `k3d` or a small managed cluster) with the **Cilium CNI**.
- The **Control, Data, Observability, and Experience planes** co-located on that one cluster.
- One real **sample service** (a Python/FastAPI service consistent with `knowledge/technology/python/`) modelled as an OpenChoreo `Component` with an `Endpoint`.
- One platform-authored **`ComponentType`** golden path matching our stack.
- A `DeploymentPipeline` promoting the service across two environments (e.g. `dev` → `staging`).
- **Image builds stay in GitHub Actions** (per `knowledge/operations/ci-cd/github-actions/`); OpenChoreo handles deploy + promote.

**Out of scope (deliberately deferred)**

- The built-in **Workflow/Build Plane** (Argo Workflows) — we keep building in GitHub Actions.
- Multi-cluster / multi-region topology.
- Production traffic, real user data, or any migration of existing services.

![OpenChoreo pilot architecture (single cluster, build plane out of scope)](diagrams/pilot-architecture.svg)

\clearpage

# Implementation Plan

The pilot runs in four short phases with an explicit gate at the end. Each phase produces written evidence captured back into the research folder.

![Pilot phases and the go/no-go gate](diagrams/pilot-phases.svg)

## Phase 1 — Stand up the platform (single cluster)

- Provision a cluster with Cilium; install OpenChoreo via Helm following the Quick Start.
- **Evidence:** record install time, every required dependency actually pulled in, and any friction. A failed/over-budget install here is itself a No-Go signal.

## Phase 2 — Author a golden path

- Write one `ComponentType` (and any `Trait`) representing how we want our services deployed.
- **Evidence:** the template, and notes on how hard it was to express our conventions.

## Phase 3 — Self-service deploy + promote

- A developer **with no prior OpenChoreo experience** deploys the sample service via the Backstage portal/CLI and promotes it `dev` → `staging` through the `DeploymentPipeline`.
- **Evidence:** can they do it from docs alone? Time-to-first-deploy; where they got stuck.

## Phase 4 — Day-2 operations

- Perform one full **version upgrade** of the OpenChoreo install.
- Induce one failure (e.g. a broken reconciliation) and recover it.
- Confirm self-service **observability** (logs/metrics/traces) for the sample service.
- **Evidence:** upgrade outcome, recovery steps, and a candid day-2 burden assessment.

## Go / No-Go gate

Proceed toward adoption (via a new ADR) only if **both** hold:

1. A **single maintainer** can comfortably install, operate, and upgrade the stack.
2. A **non-expert developer** can self-service deploy + promote a real service.

If the gate is not met, **stop** and pursue the fallback: a self-assembled **Backstage + Argo CD** stack (`research/openchoreo-idp-evaluation/06-alternatives-comparison.md`). Either way, the throwaway cluster is torn down at the end.

# Timeline

| Phase | Duration (part-time) | Owner |
|---|---|---|
| Phase 1 — Stand up | ~3–5 days | Pilot maintainer (1 person) |
| Phase 2 — Golden path | ~2–3 days | Pilot maintainer |
| Phase 3 — Self-service deploy | ~2–3 days | Maintainer + 1 non-expert developer |
| Phase 4 — Day-2 ops | ~3–5 days | Pilot maintainer |
| Decision write-up | ~1 day | Pilot maintainer |

**Total:** roughly **2–4 weeks of part-time effort** by 1–2 people. At the end, the pilot maintainer writes up the evidence, and the go/no-go decision is recorded as a follow-up ADR that either supersedes or builds on `adr/0008-pilot-openchoreo-idp/`.

> This proposal implements the recommendation in `research/openchoreo-idp-evaluation/07-evaluation-and-recommendation.md` and is governed by `adr/0008-pilot-openchoreo-idp/`.
