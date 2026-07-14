---
title: "OpenChoreo Platform Architecture — Evaluation"
status: exploring
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - openchoreo
  - architecture
  - kubernetes
  - gitops
  - multi-cluster
sources:
  - knowledge: "knowledge/operations/internal-developer-platforms/openchoreo/architecture-planes.md"
  - knowledge: "knowledge/operations/internal-developer-platforms/openchoreo/core-abstractions.md"
references:
  - url: "https://openchoreo.dev/docs/overview/architecture/"
    title: "OpenChoreo — Architecture"
  - url: "https://openchoreo.dev/docs/concepts/runtime-model/"
    title: "OpenChoreo — Runtime Model"
last_audit_date: 2026-06-15
---

# OpenChoreo Platform Architecture — Evaluation

## Context

Issue #78 asks us to assess OpenChoreo's platform architecture: its multi-plane design, Kubernetes-native model, multi-cluster/environment support, GitOps capabilities, and extensibility. This note evaluates each against the needs of a small cooperative.

## Findings

- **Multi-plane design.** OpenChoreo separates Control, Data, Workflow, and Observability planes, plus an Experience plane (portal/CLI/GitOps/agents). The planes are decoupled and independently deployable. See [architecture-planes.md](../../knowledge/operations/internal-developer-platforms/openchoreo/architecture-planes.md).
  - *Naming caveat (issue #78):* the issue's "Workflow Plane" is the OpenChoreo docs' term for the build/CI plane (README calls it "CI Plane"; marketing "Build Plane"). All three refer to the same plane. No discrepancy in substance.
- **Kubernetes-native.** Every abstraction is a CRD reconciled by OpenChoreo controllers in the control plane. It augments rather than hides Kubernetes — operators retain `kubectl` access and standard primitives underneath.
- **Multi-cluster / multi-environment.** Environments map to DataPlanes; DataPlanes are clusters. A single cluster can host all planes (good for a pilot); production can split data planes per environment/region. Cells provide per-(namespace–project–environment) runtime isolation.
- **GitOps.** State is declarative CRDs, so it is Git-storable and reconciled. The Workflow Plane explicitly supports "GitOps workflows for declaratively managing platform and application state." Argo CD/Flux interoperate at the delivery layer.
- **Extensibility.** `ComponentType`, `Trait`, `Workflow/ClusterWorkflow`, and `ResourceType` are platform-team-authored templates — the supported extension surface for golden paths and infrastructure provisioning.

## Analysis

The architecture is sound and genuinely Kubernetes-native, which is a strong fit for a team that wants to keep standard tooling while reducing per-developer cognitive load. The decoupled planes are a real advantage for **graduated adoption**: we can start single-cluster and grow.

The main architectural risk for a small COOP is **surface area**: even a single-cluster install pulls in a meaningful dependency set (Cilium CNI, Envoy Gateway, Argo Workflows, an observability stack). The CRD-everything model is powerful but means our team must become comfortable debugging controller reconciliation when things go wrong — that is the relocated complexity discussed in [idp-platform-engineering-concepts.md](../../knowledge/operations/internal-developer-platforms/openchoreo/idp-platform-engineering-concepts.md).

## Recommendations

- Architecture is **not a blocker**. It supports a low-footprint single-cluster pilot.
- During the pilot, explicitly exercise the GitOps path (store CRDs in Git, reconcile) to confirm it matches our ADR 0002 conventions.
- Treat the Cilium/eBPF dependency as the highest-risk architectural component to validate operationally (see `04-platform-operations.md`).
