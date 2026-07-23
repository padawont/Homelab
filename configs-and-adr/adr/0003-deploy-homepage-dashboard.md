---
adr: 3
title: Deploy Homepage Dashboard
author: padawont
status: proposed
topic: deployment
date: 2026-07-23
date-proposed: 2026-07-23
history: "2026-07-23: Created for issue #13"
related_knowledge:
  - knowledge/technology/homepage/
related_configs:
  - configs-and-adr/node-main/kubernetes/homepage.yaml
---

# ADR 0003 — Deploy Homepage Dashboard

## Context

The K3s cluster on node-1 runs multiple services (Bookstack, Kiwix, Longhorn, Rancher) but lacks a centralized service discovery dashboard. Currently, service URLs are tracked ad-hoc via bookmarks and cluster state tools (k9s, Rancher). As the cluster grows, a unified dashboard becomes necessary for:

- Quick navigation to all cluster services from a single page
- Displaying cluster health metrics (resource usage, pod status)
- Integrating with Kubernetes API for dynamic service discovery
- Providing a customisable landing page accessible to all homelab users

## Decision

Deploy [Homepage](https://gethomepage.dev) as the cluster dashboard, installed via raw Kubernetes manifests on node-1 in the `homepage` namespace.

Key technical choices:
- **Raw manifests** over Helm chart — consistent with existing homelab deployment pattern (Bookstack, Kiwix)
- **Traefik IngressRoute** for ingress — uses the cluster's existing Traefik CRD (the bundled K3s Traefik instance is disabled per `k3s.io/node-args: --disable traefik`; a separate Traefik ingress controller must be installed for IngressRoute CRDs to function)
- **ConfigMap-based configuration** — all YAML config files (services, bookmarks, widgets, etc.) mounted as subPath volumes per upstream best practice
- **ClusterRole** with read-only access to pods, nodes, ingresses, ingressroutes, and metrics — sufficient for the dashboard without excessive permissions
- **`:latest` image tag** — consistent with existing pattern; accept the trade-off of potentially unexpected updates

## Consequences

**Easier:**
- Centralised service discovery via a single URL
- K8s-native widget integration (resource usage, pod status, Longhorn metrics)
- Configuration as code — all settings are version-controlled in the repo
- Sticky sessions enabled via Traefik cookie for smooth multi-replica operation

**Harder:**
- `:latest` image tag risks unexpected upstream changes on pod restart
- No Helm chart used — updates require manual manifest edits
- Traefik IngressRoute CRD dependency — if Traefik is replaced, the ingress must be migrated
- Dashboard is exposed on local network without TLS (TLS is out of scope for this initial deployment)
- Service discovery is manual (must add each service to `services.yaml`) — no automatic service discovery

## Considered Options

| Option | Why Rejected |
|---|---|
| **Homer** | Static YAML dashboard; no K8s API integration, no built-in cluster health widgets |
| **Flame** | Docker-focused; limited Kubernetes support, no RBAC integration |
| **Hesk** | Helpdesk/ticketing system; wrong category of tool entirely |
