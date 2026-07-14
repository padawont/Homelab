# Rancher

Reference notes on [Rancher](https://rancher.com/) — a Kubernetes multi-cluster management platform maintained by SUSE. Rancher provides a unified UI for cluster operations, workload management, RBAC, monitoring, and application lifecycle across local and cloud-provisioned clusters. These notes cover the architecture, installation, configuration, and operational workflows needed to bootstrap Rancher for the OpenChoreo POC.

## Prerequisites

- [Kubernetes Fundamentals](../) — basic K8s concepts (Pods, Services, Deployments, Ingress, RBAC, Helm)
- [k3d](../k3d/) — local k3s clusters in Docker, used as the management cluster for bootstrap
- [ADR 0008 — Pilot OpenChoreo](../../../adr/0008-pilot-openchoreo-idp/) — context for why Rancher is needed in the POC

## Architecture

| File | Description |
|---|---|
| [rancher-architecture.md](rancher-architecture.md) | Rancher Management Server, downstream clusters, agent communication, Fleet, authentication proxy |

## Installation & Bootstrap

| File | Description |
|---|---|
| [rancher-install-k3d.md](rancher-install-k3d.md) | Step-by-step bootstrap on k3d with Helm, cert-manager, and self-signed TLS |

## Configuration & Security

| File | Description |
|---|---|
| [rancher-rbac.md](rancher-rbac.md) | Users, groups, RoleTemplates, Projects, and Namespace scoping |

## Operations

| File | Description |
|---|---|
| [rancher-monitoring-logging.md](rancher-monitoring-logging.md) | Monitoring (rancher-monitoring / Prometheus + Grafana) and logging (rancher-logging / Fluentd) integrations |
| [rancher-apps-marketplace.md](rancher-apps-marketplace.md) | Helm chart deployment via Rancher UI, catalog management, multi-cluster apps |
| [rancher-upgrade.md](rancher-upgrade.md) | Server upgrades and downstream cluster version bumps |

## Troubleshooting

| File | Description |
|---|---|
| [rancher-troubleshooting.md](rancher-troubleshooting.md) | Common issues — certificates, agent connectivity, stuck clusters, webhooks, Fleet |
