---
title: "Rancher architecture"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, rancher, architecture, fleet, agents]
sources:
  - url: "https://ranchermanager.docs.rancher.com/"
    title: "Rancher Manager documentation"
  - url: "https://ranchermanager.docs.rancher.com/reference-guides/rancher-manager-architecture/rancher-server-and-components"
    title: "Rancher Server and components"
  - url: "https://ranchermanager.docs.rancher.com/reference-guides/rancher-manager-architecture/communicating-with-downstream-user-clusters"
    title: "Communicating with downstream user clusters"
  - url: "https://fleet.rancher.io/explanations/architecture"
    title: "Fleet architecture"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/k3s/architecture.md"
---

# Rancher architecture

## Overview

Rancher has two planes: the **management server** (the Rancher workload itself)
and the **downstream clusters** it manages. The management server is the only
stateful control component; downstream clusters run lightweight agents that
connect back to it. Nothing requires inbound access to downstream clusters —
agents initiate the connections.

## Details

### Management server

- Runs as a Deployment in its own namespace (default `cattle-system`) on a
  Kubernetes cluster — in a homelab, usually the same k3s cluster or a small
  dedicated one.
- Stores state (users, clusters, projects, settings) in its own etcd.
- Serves the web UI, the Rancher API (`/v3`), and the authentication proxy.
- Bundles controllers for RBAC, projects, catalogs, and the embedded Fleet.

### Downstream clusters and agents

A downstream cluster is any Kubernetes cluster registered in Rancher. When a
cluster is imported, Rancher generates a registration command that installs
two Deployments in the downstream cluster:

- **cattle-cluster-agent** — connects back to the management server and relays
  cluster state (events, metrics, node status) and proxied API requests.
- **cattle-node-agent** — performs node-level operations during provisioning
  (e.g. k3s/RKE2 cluster creation); for imported existing clusters its role is
  smaller.

Communication is **outbound-only** from the agents: they open connections to
the management server's HTTPS endpoint. The management server proxies kubectl
requests to downstream clusters over these established tunnels, so no inbound
firewall rules are needed on the downstream side.

Example — abstract agent connection flow:

```
Browser/UI ──► Rancher management server (cattle-system)
                      │  HTTPS (wss/websocket tunnels)
                      ▼
         cattle-cluster-agent (downstream cluster)
                      │
                      ▼
         downstream Kubernetes API server (localhost)
```

### Authentication proxy

- When you access a downstream cluster through the UI, Rancher acts as an
  **authentication proxy**: it validates your Rancher session, maps it to a
  Kubernetes identity (via a generated kubeconfig / service account), and
  forwards the request.
- This is what makes per-user RBAC work on clusters Rancher does not directly
  control — users never need cluster-admin kubeconfigs.

### Fleet (continuous delivery)

Fleet is the GitOps engine embedded in Rancher:

- **fleet-controller** runs on the management server.
- **fleet-agent** runs in each downstream cluster and applies bundles.
- A `GitRepo` custom resource points at a Git repo; Fleet turns its contents
  (raw YAML, Helm, Kustomize) into **Bundles** and deploys them via Helm.
- Fleet tracks drift and reports state back per cluster.

Example — abstract GitRepo targeting a cluster group:

```yaml
apiVersion: fleet.cattle.io/v1alpha1
kind: GitRepo
metadata:
  name: homelab-apps
  namespace: fleet-default
spec:
  repo: https://github.com/example/homelab-apps.git
  branch: main
  targets:
    - clusterGroup: homelab
```

### Data flow summary

| Path | Direction | Protocol |
|---|---|---|
| UI/API → management server | inbound | HTTPS |
| Agent → management server | outbound (agent-initiated) | HTTPS / wss tunnel |
| Management → downstream API | via agent tunnel | kubectl proxied |
| Fleet controller → agents | via agent tunnel | GitRepo/Bundle CRs |

## Sources / Further Reading

- Rancher Server and components: https://ranchermanager.docs.rancher.com/reference-guides/rancher-manager-architecture/rancher-server-and-components
- Communicating with downstream user clusters: https://ranchermanager.docs.rancher.com/reference-guides/rancher-manager-architecture/communicating-with-downstream-user-clusters
- Fleet architecture: https://fleet.rancher.io/explanations/architecture
- Rancher Manager documentation: https://ranchermanager.docs.rancher.com/
