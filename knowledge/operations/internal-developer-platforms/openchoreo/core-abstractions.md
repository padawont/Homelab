---
title: "OpenChoreo Core Abstractions"
status: draft
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - openchoreo
  - abstractions
  - crd
  - golden-paths
  - backstage
sources:
  - url: "https://openchoreo.dev/docs/concepts/platform-abstractions/"
    title: "OpenChoreo — Platform Abstractions"
  - url: "https://openchoreo.dev/docs/concepts/runtime-model/"
    title: "OpenChoreo — Runtime Model"
  - url: "https://github.com/openchoreo/openchoreo/blob/main/docs/choreo-concepts.md"
    title: "openchoreo — Choreo Concepts"
last_audit_date: 2026-06-15
---

# OpenChoreo Core Abstractions

OpenChoreo exposes a **Platform API** made of Kubernetes Custom Resources (CRDs) that the control plane reconciles. The model splits cleanly into two audiences: a **Developer API** (what application developers use) and a **Platform API** (what the platform team uses to define golden paths and infrastructure).

## Developer-facing abstractions

| Abstraction | Definition |
|---|---|
| **Organization** | The highest level of tenancy — the root container for all platform resources and the fundamental multi-tenant isolation boundary (per business unit, team, or customer). |
| **Project** | A logical grouping of related components that are deployed and isolated together. |
| **Component** | A developer-created workload — e.g. a service, web application, scheduled task, or worker. Deployed according to a `ComponentType`. |
| **Endpoint** | How a component exposes functionality (network-accessible APIs/interfaces); components also declare **dependencies** on other endpoints or resources. |
| **Environment** | A stage in the delivery lifecycle (development, staging, production) that defines *where* applications deploy (which DataPlane). A first-class abstraction. |

## Platform-team abstractions (golden paths)

| Abstraction | Definition |
|---|---|
| **ComponentType** | A platform-engineer-defined template governing how components of a given type are deployed and managed — "the bridge between developer intent and platform governance." This is the core golden-path mechanism. |
| **Trait** | A platform-engineer-defined template that augments components with operational behavior (e.g. autoscaling, ingress) without modifying the ComponentType — composable, reusable capabilities. |
| **Workflow / ClusterWorkflow** | A template for running automation tasks — both component builds and generic automation. |
| **DeploymentPipeline** | Defines the allowed progression paths for applications moving through environments, encoding promotion rules and quality gates. |
| **ResourceType** | Governs how managed infrastructure is provisioned — describes what Kubernetes manifests the platform emits onto the data plane. |

## Infrastructure abstractions

| Abstraction | Definition |
|---|---|
| **DataPlane** | A Kubernetes cluster where workloads run; abstracts cluster management into a unified deploy interface. |
| **WorkflowPlane** (a.k.a. BuildPlane/CI Plane) | Dedicated infrastructure for executing CI/build workloads, using Argo Workflows. |
| **Cell** | Runtime isolation boundary for all components in a namespace–project–environment combination (policy enforcement + observability). See [architecture-planes.md](architecture-planes.md). |

## How they relate

The hierarchy flows roughly: **Organization → Project → Component (+ Endpoints)**, deployed into **Environments** (each mapped to a **DataPlane**), progressed by a **DeploymentPipeline**, governed by platform-team **ComponentTypes/Traits**, and built by **Workflows** on a **WorkflowPlane**. Because everything is a CRD, the entire platform state is declarative and GitOps-friendly.

## The Experience layer

Developers interact through the **Backstage-based Internal Developer Portal**, a **CLI**, GitOps, and **AI agents** (OpenChoreo ships SRE and FinOps agent concepts plus MCP servers/skills for AI-assisted, guardrailed operations). These all sit in the Experience Plane and drive the same declarative Platform API underneath.
