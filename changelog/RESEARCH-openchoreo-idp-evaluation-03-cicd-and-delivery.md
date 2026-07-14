---
title: "OpenChoreo CI/CD and Delivery — Evaluation"
status: exploring
author: "Noar Qerimi (noarqerimi)"
date: 2026-06-15
tags:
  - openchoreo
  - ci-cd
  - argo-workflows
  - gitops
  - buildpacks
sources:
  - knowledge: "knowledge/operations/internal-developer-platforms/openchoreo/architecture-planes.md"
  - knowledge: "knowledge/operations/ci-cd/devbox-ci/"
references:
  - url: "https://openchoreo.dev/docs/overview/architecture/"
    title: "OpenChoreo — Architecture"
  - url: "https://github.com/openchoreo/openchoreo/blob/main/README.md"
    title: "openchoreo README"
last_audit_date: 2026-06-15
---

# OpenChoreo CI/CD and Delivery — Evaluation

## Context

Assess the built-in workflow engine, integration with existing CI systems (GitHub Actions, GitLab CI, Jenkins), deployment automation, release/promotion workflows, and the GitOps operational model.

## Findings

- **Built-in workflow engine.** The Workflow Plane runs on **Argo Workflows** with **cloud-native Buildpacks** as the default builder — a Kubernetes-native build/CI execution environment. The build plane is described as **optional**, so the platform does not force us to abandon existing pipelines.
- **External CI integration.** Because builds produce container images and deployment is driven by declarative CRDs, existing CI (GitHub Actions — which we already document in `knowledge/operations/ci-cd/github-actions/`) can build/push images and then trigger OpenChoreo deployment via the Platform API/GitOps. OpenChoreo does not require us to replace GitHub Actions.
- **Promotion / release.** `DeploymentPipeline` encodes allowed environment progression with promotion rules and quality gates.
- **GitOps.** The Workflow Plane explicitly supports GitOps workflows for declaratively managing platform and application state; Argo CD/Flux interoperate.

## Analysis

This is a flexible position: OpenChoreo offers an integrated build path *but* coexists with our established GitHub Actions workflows. For a small team already invested in GitHub Actions, the pragmatic pattern is **"build in GitHub Actions, deploy/promote via OpenChoreo,"** avoiding a forced migration of CI while still gaining declarative promotion and golden-path deploys.

Risks: running Argo Workflows adds another stateful subsystem to operate if we adopt the built-in build plane; and the promotion model needs validation against how we actually cut releases (ADR 0002 conventions). Adopting the build plane is **deferrable** — we can pilot deploy-only first.

## Recommendations

- Pilot **deploy/promote via OpenChoreo while keeping image builds in GitHub Actions**. Treat the built-in Argo build plane as a later, optional step.
- Validate that `DeploymentPipeline` promotion maps cleanly to our branch/release conventions before committing.
