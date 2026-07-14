---
title: "OpenChoreo Multi-Plane Architecture"
status: draft
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - openchoreo
  - architecture
  - kubernetes
  - control-plane
  - data-plane
  - observability
sources:
  - url: "https://openchoreo.dev/docs/overview/architecture/"
    title: "OpenChoreo — Architecture"
  - url: "https://openchoreo.dev/docs/concepts/runtime-model/"
    title: "OpenChoreo — Runtime Model"
  - url: "https://github.com/openchoreo/openchoreo/blob/main/README.md"
    title: "openchoreo README"
last_audit_date: 2026-06-15
---

# OpenChoreo Multi-Plane Architecture

OpenChoreo uses a **modular multi-plane architecture** that separates the concerns of control, runtime, workflows, and observability. Each plane can be deployed independently, on a single cluster for small setups or across multiple clusters as scale grows.

## The planes

| Plane | Responsibility |
|---|---|
| **Control Plane** | The central orchestrator. Transforms and reconciles the desired state of platform and developer resources "as declared in its Developer API and Platform API." Runs OpenChoreo's Kubernetes controllers (CRDs). |
| **Data Plane(s)** | Runs application workloads. Provides isolated, observable runtime environments, project/tenant isolation, gateway topology, and runtime/network security. |
| **Workflow Plane(s)** | Executes workflows — CI workflows for building and testing components, and GitOps/automation workflows (e.g. IaC). Powered by Argo Workflows + cloud-native Buildpacks. |
| **Observability Plane(s)** | Collects and aggregates distributed container logs, metrics, and OpenTelemetry-based traces across the workflow and data planes. |
| **Experience Plane** | A uniform, access-controlled interface: CLI, the Backstage-based Internal Developer Portal, GitOps, and AI agents. |

## A naming caveat worth recording

OpenChoreo's own materials use **different names for the plane that runs builds/CI**:

- the **Architecture** docs call it the **Workflow Plane**;
- the project **README** calls it the **CI Plane**;
- some marketing/home-page material calls it the **Build Plane**.

They refer to the same thing. Issue #78 listed a "Workflow Plane," which matches the architecture documentation. When reading OpenChoreo docs, treat *Workflow Plane ≈ Build Plane ≈ CI Plane*. The underlying abstraction in the Platform API is `WorkflowPlane` (see [core-abstractions.md](core-abstractions.md)).

## Key runtime technologies

- **Cilium CNI + eBPF** — used by OpenChoreo's network "Guard" module to enforce zero-trust network policy and provide kernel-level observability across ingress/egress paths.
- **Envoy Gateway** — manages ingress traffic into the data plane.
- **Argo Workflows** — the default engine for the Workflow Plane's builds and automation.
- **OpenTelemetry / Prometheus / OpenSearch** — the observability data path.

## Cells: the runtime isolation boundary

At runtime, the resources of a project are isolated through **Cells** — "secure, isolated, and observable boundaries for all components belonging to a given namespace–project–environment combination." A Cell is the runtime boundary where policy enforcement (via Cilium) and observability are applied. This is how OpenChoreo achieves multi-tenant isolation on shared clusters.

## Deployment topology implication

Because the planes are decoupled, a **single-cluster** install (all planes co-located) is viable for evaluation and small teams, while larger organizations can split data planes per environment/region and run dedicated workflow and observability planes. This flexibility is central to assessing operational fit for a small cooperative — see `research/openchoreo-idp-evaluation/04-platform-operations.md`.
