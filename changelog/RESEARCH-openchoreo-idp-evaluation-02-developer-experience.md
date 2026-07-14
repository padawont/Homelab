---
title: "OpenChoreo Developer Experience — Evaluation"
status: exploring
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - openchoreo
  - developer-experience
  - backstage
  - self-service
  - cli
sources:
  - knowledge: "knowledge/operations/internal-developer-platforms/openchoreo/core-abstractions.md"
  - knowledge: "knowledge/operations/internal-developer-platforms/openchoreo/idp-platform-engineering-concepts.md"
references:
  - url: "https://openchoreo.dev/docs/"
    title: "What is OpenChoreo"
  - url: "https://openchoreo.dev/docs/getting-started/quick-start-guide/"
    title: "OpenChoreo — Quick Start Guide"
last_audit_date: 2026-06-15
---

# OpenChoreo Developer Experience — Evaluation

## Context

Evaluate the day-to-day developer experience: self-service deployment, the Backstage portal, application lifecycle management, the service catalogue, onboarding, and CLI/API access.

## Findings

- **Self-service deployment.** Developers declare a Component (service / web app / scheduled task) and an Endpoint; the control plane reconciles it into a running workload on the target Environment. No hand-written Deployment/Service/Ingress YAML.
- **Backstage developer portal.** OpenChoreo ships a Backstage-powered Internal Developer Portal as the primary self-service surface — service catalogue, environments, and operations in one place.
- **Lifecycle management.** Promotion across environments is modelled by `DeploymentPipeline` (promotion rules + quality gates), giving a declarative dev → staging → prod path.
- **CLI and API.** A CLI is provided in the Experience plane, and the Platform API (CRDs) is directly usable for scripting/GitOps. AI-assisted operations are offered via MCP servers/skills and SRE/FinOps agent concepts.
- **Onboarding.** Quick Start uses a local k3d cluster and provisions sample abstractions (namespaces, dataplanes, environments, projects, componenttypes) so a developer can deploy a first app quickly.

## Analysis

For our use case — developers who are strong programmers but not Kubernetes experts — the DX value proposition is the strongest single argument for OpenChoreo. The Component/Endpoint model is close to how developers already think ("I have a service that exposes an API"), and the Backstage portal is a familiar, well-adopted catalogue.

The caveats are maturity-related: as a CNCF Sandbox project the portal/CLI polish, documentation depth, and edge-case behavior are less battle-tested than commercial IDPs. Golden paths are only as good as the `ComponentType`/`Trait` templates **we** author — so DX quality partly depends on our own platform investment, not just the product.

## Recommendations

- The DX justifies a pilot. The single most important pilot success metric should be **"a developer with no OpenChoreo experience deploys and promotes a real service using only the portal/CLI"** (see `proposals/openchoreo-idp-pilot/`).
- Budget pilot time to author at least one solid `ComponentType` matching our stack (e.g. a Python/FastAPI service per `knowledge/technology/python/`), since DX hinges on it.
