---
title: "Rancher Architecture"
status: draft
author: padawont
date: 2026-07-11
tags:
  - rancher
  - architecture
  - kubernetes
  - cluster-management
sources:
  - url: "https://ranchermanager.docs.rancher.com/reference-guides/rancher-manager-architecture"
    title: "Rancher Architecture Overview"
  - url: "https://ranchermanager.docs.rancher.com/"
    title: "Rancher Documentation"
  - url: "https://github.com/rancher/rancher"
    title: "Rancher GitHub Repository"
last_audit_date: 2026-07-11
---

# Rancher Architecture

## Prerequisites

- [Kubernetes Fundamentals](../) — basic understanding of K8s control plane components, workloads, and networking
- [ADR 0008 — Pilot OpenChoreo](../../../adr/0008-pilot-openchoreo-idp/) — context for why Rancher is being evaluated

## Overview

Rancher is a Kubernetes multi-cluster management platform. It is not itself a Kubernetes distribution — it sits on top of existing clusters (including k3s, RKE, RKE2, EKS, AKS, GKE, and any conformant K8s distribution) and provides a unified control plane for managing them.

Key capabilities:
- Centralised cluster lifecycle (create, import, upgrade, delete)
- Unified RBAC across all clusters via Projects and RoleTemplates
- Built-in monitoring, logging, and alerting
- Helm chart management via the Apps Marketplace
- GitOps-at-scale via Fleet

## Rancher Management Server

The Rancher Management Server is the control plane. It can be installed in three modes:

| Mode | Use case | Notes |
|---|---|---|
| Docker single-node | Quick evaluation, dev/test | `docker run -d --restart=unless-stopped -p 80:80 -p 443:443 rancher/rancher` |
| Helm on existing K8s cluster | Production, HA | Installed via Helm chart on a dedicated management cluster (k3s, RKE, or any K8s) |
| Embedded in RKE/RKE2 | Integrated setup | Rancher is deployed automatically during RKE/RKE2 cluster creation |

The server runs these key components:
- **API Server** — manages Rancher CRDs (clusters, projects, role templates, etc.), proxies requests to downstream K8s API servers
- **Controllers** — Cluster Controller, Node Controller, User Controller, Auth Controller, Fleet Controller
- **Webhook** — validates Rancher resource mutations, enforces policies
- **CAPI integration** — uses Cluster API under the hood for provisioning downstream clusters

## Downstream Clusters

Downstream clusters are the clusters that Rancher manages. Two types:

| Type | Description |
|---|---|
| **Imported** | Cluster was created independently (via k3d, EKS, AKS, etc.) and registered with Rancher by applying an agent manifest |
| **Provisioned** | Cluster is created by Rancher itself using CAPI providers (RKE2, K3s, EKS, GKE, AKS node driver) |

Rancher stores cluster state in the management cluster's `fleet-default` namespace as CAPI Cluster objects.

## Agent Communication Flow

Each downstream cluster runs a `cattle-cluster-agent` pod that connects back to the Rancher Management Server:

```
Downstream Cluster                    Rancher Management Server
┌───────────────────┐                 ┌──────────────────────┐
│ cattle-cluster-agent│ ──HTTPS──►    │ Rancher API Server   │
│ (agent)           │                 │                      │
│                   │                 │ Proxy/impersonation │
│ kubectl exec/logs │ ◄──WebSocket── │ (authentication)     │
│ port-forward      │   tunnel       │                      │
└───────────────────┘                 └──────────────────────┘
```

- Agent connects to `https://<rancher-server-url>/v3/connect`
- Registration uses a cluster registration token (validated by the management server)
- All K8s API operations (list pods, apply manifests) are proxied through Rancher's auth layer
- `kubectl exec`, logs, and port-forward use a WebSocket tunnel for bidirectional streaming

## Fleet Architecture

Fleet is Rancher's GitOps-at-scale engine. Term definitions:

| Term | Description |
|---|---|
| **Workspace** | A Fleet workspace (e.g., `fleet-local` for local resources, `fleet-default` for downstream clusters) |
| **GitRepo** | A CRD that points to a Git repository containing Kubernetes manifests or Helm charts |
| **Bundle** | A set of resources generated from a GitRepo (one per target cluster or group) |
| **ClusterGroup** | A selector-based grouping of downstream clusters for targeting bundles |

Flow:
```
GitRepo CRD ──► Fleet Manager (management cluster) ──► Fleet Agent (downstream cluster)
                                                              │
                                                              ▼
                                                         Apply resources
```

Each downstream cluster runs a Fleet agent that polls for assigned bundles and applies them locally.

## Authentication Proxy

Rancher authenticates K8s API calls through an authenticating proxy pattern:

1. User authenticates with Rancher (local auth, OIDC, LDAP, SAML, GitHub)
2. Rancher validates permissions via its RBAC engine (Global Roles + RoleTemplates + Project membership)
3. Rancher proxies the request to the downstream cluster API using a service account or impersonation
4. The downstream cluster sees requests coming from the Rancher service account, not the end user

This is implemented via the `extensions.k8s.io` API aggregation layer — Rancher registers an APIService that intercepts requests.

## References

- [Rancher Architecture](https://ranchermanager.docs.rancher.com/reference-guides/rancher-manager-architecture)
- [Rancher GitHub Repository](https://github.com/rancher/rancher)
- [Fleet Documentation](https://fleet.rancher.io/)
- [Cluster API Documentation](https://cluster-api.sigs.k8s.io/)
