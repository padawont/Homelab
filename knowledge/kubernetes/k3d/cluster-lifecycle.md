---
title: "k3d Cluster Lifecycle"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k3d
  - cluster
  - lifecycle
  - kubernetes
sources:
  - url: "https://k3d.io/v5.6.0/#quick-start"
    title: "k3d — Quick Start"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_cluster_create/"
    title: "k3d cluster create command"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_cluster_delete/"
    title: "k3d cluster delete command"
  - url: "https://k3d.io/v5.6.0/usage/kubeconfig/"
    title: "k3d — Handling Kubeconfigs"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_kubeconfig_merge/"
    title: "k3d kubeconfig merge command"
last_audit_date: 2026-07-10
---

# k3d Cluster Lifecycle

Every k3d cluster consists of one or more Docker containers: server nodes (running k3s), optionally agent nodes, and optionally an Nginx load balancer container (ServersLB) as the entry point.

## Create a Cluster

### Single-Node (Default)

```bash
k3d cluster create mycluster
```

Creates a cluster named `mycluster` with 1 server node and 0 agents. The cluster name is prefixed with `k3d-` internally (e.g. `k3d-mycluster`).

### Multi-Node

```bash
k3d cluster create mycluster --servers 1 --agents 2
```

### Named vs Default

When no name is given, the cluster defaults to `k3s-default`.

```bash
k3d cluster create
```

---

## Start, Stop, Delete

### Start a Stopped Cluster

```bash
k3d cluster start mycluster
```

Resumes all node containers for the cluster.

### Stop a Cluster

```bash
k3d cluster stop mycluster
```

Pauses the cluster without deleting any resources. Containers are stopped, not removed.

### Delete a Cluster

```bash
k3d cluster delete mycluster
```

Fully tears down the cluster, removing all node containers and the load balancer. The entry for this cluster is also removed from the default kubeconfig.

### Delete All Clusters

```bash
k3d cluster delete --all
```

### List Clusters

```bash
k3d cluster list
```

Displays all clusters with their status, node count, and mapped ports. Use JSON output for scripting:

```bash
k3d cluster list -o json | jq
```

---

## Edit a Running Cluster

```bash
k3d cluster edit mycluster --port-add "8080:80@loadbalancer"
```

Adds a new port mapping to an existing cluster without recreating it.

---

## Kubeconfig Management

By default, `k3d cluster create` updates your default kubeconfig and switches the current context (both can be disabled with `--kubeconfig-update-default=false` and `--kubeconfig-switch-context=false`).

### Merge into Default Kubeconfig

```bash
k3d kubeconfig merge mycluster --kubeconfig-merge-default
```

### Merge and Switch Context

```bash
k3d kubeconfig merge mycluster --kubeconfig-merge-default --kubeconfig-switch-context
```

### Write to Separate File

```bash
k3d kubeconfig get mycluster > ~/.k3d/kubeconfig-mycluster.yaml
```

Use it via:

```bash
export KUBECONFIG=~/.k3d/kubeconfig-mycluster.yaml
```

### Print to stdout

```bash
k3d kubeconfig get mycluster
```

### Remove Cluster from Kubeconfig

`k3d cluster delete mycluster` automatically removes the cluster entry from the default kubeconfig.

---

## Node-Level Operations

### Create a New Node

```bash
k3d node create newserver --cluster mycluster --role server
```

### List Nodes

```bash
k3d node list
```

Nodes follow the naming convention `k3d-<clustername>-<role>-<index>`, e.g. `k3d-mycluster-server-0`, `k3d-mycluster-agent-0`.

---

## Node Naming Convention

| Pattern | Example |
|---|---|
| `k3d-<name>-server-<N>` | `k3d-mycluster-server-0` |
| `k3d-<name>-agent-<N>` | `k3d-mycluster-agent-0` |
| `k3d-<name>-serverlb` | `k3d-mycluster-serverlb` (load balancer) |
