---
title: "Helm"
status: draft
author: padawont
date: 2026-07-11
tags:
  - kubernetes
  - helm
  - package-management
  - templating
sources:
  - url: "https://helm.sh/docs/"
    title: "Helm Documentation"
  - url: "https://helm.sh/docs/topics/charts/"
    title: "Helm Chart Structure"
last_audit_date: 2026-07-11
---

# Helm

Reference notes on [Helm](https://helm.sh/) — the package manager for Kubernetes. Helm uses a packaging format called charts to define, install, and upgrade Kubernetes applications.

Prerequisites: Kubernetes fundamentals (see [Kubernetes notes](../)) covering Pods, Services, Deployments, ConfigMaps, and Secrets. A running Kubernetes cluster or [k3d](../k3d/) cluster for local testing.

## Getting Started

| File | Description |
|---|---|
| [chart-structure.md](chart-structure.md) | Anatomy of a Helm chart — Chart.yaml, values.yaml, templates/, _helpers.tpl |
| [cli-commands.md](cli-commands.md) | Essential Helm CLI commands — install, upgrade, rollback, uninstall, list, get |
| [templating.md](templating.md) | Go template engine, Sprig functions, directives, named templates |

## Values & Configuration

| File | Description |
|---|---|
| [values-customization.md](values-customization.md) | Values —values, --set, --set-string, --set-file, precedence order |

## Repository Management

| File | Description |
|---|---|
| [repository-management.md](repository-management.md) | Adding, updating, listing, removing repos; OCI registries |

## Hooks & Lifecycle

| File | Description |
|---|---|
| [hooks.md](hooks.md) | Helm hook types, weights, deletion policies, and lifecycle management |

## Complementary Tools

| File | Description |
|---|---|
| [complementary-tools.md](complementary-tools.md) | Helmfile, helm-diff, and other tools that extend Helm |

---

See the [Helm Documentation](https://helm.sh/docs/) for the official reference.
