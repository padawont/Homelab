---
title: "Kubernetes Nodes"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - architecture
  - nodes
sources:
  - url: "https://kubernetes.io/docs/concepts/architecture/nodes/"
    title: "Nodes — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# Kubernetes Nodes

## Overview

A **Node** is a worker machine in Kubernetes — it can be a virtual or physical machine. Each node is managed by the control plane and runs the pods that make up an application workload. Every node runs at minimum a kubelet (the node agent), a container runtime (e.g., containerd, CRI-O), and kube-proxy for networking. For the broader picture of how nodes fit into the cluster, see [Kubernetes Architecture](./architecture.md).

Nodes can register themselves or be created as Node objects manually. **Self-registration** is the default: the kubelet registers itself with the API server on startup, providing its name, labels, and taints. The `--register-node` flag controls this behavior. **Manual registration** requires an administrator to create a Node object via the API, after which the kubelet can be pointed at it with `--register-node=false`. Self-registration is the dominant approach in automated cluster provisioning (kubeadm, cloud providers, etc.).

## Node Object

A Node is represented as a Kubernetes API object with the typical metadata, spec, and status sections.

**Metadata** includes the node name, labels (e.g., `kubernetes.io/hostname`, `topology.kubernetes.io/zone`), and annotations. Labels are critical for scheduling — pods use `nodeSelector` or `nodeAffinity` to target specific labels.

**Spec** fields include:

- `podCIDR` — the CIDR block assigned to the node for pod IP allocation.
- `taints` — a list of taints that repel pods unless the pod has a matching toleration. This is the primary mechanism to reserve nodes for specific workloads.
- `providerID` — an identifier set by cloud-controller-manager to associate the node with a cloud instance.

**Status** captures the runtime state of the node. It includes conditions, addresses, capacity, allocatable resources, and node info (OS, kernel, kubelet version, container runtime). Status is continuously updated by the kubelet and the node controller.

## Node Conditions

Node conditions are a set of signals that reflect the node's health. Each condition has a `type`, `status` (`True`, `False`, `Unknown`), `reason`, `message`, and timestamps.

| Condition | Meaning |
|---|---|
| `Ready` | The node is healthy and accepts pods. `Unknown` means the kubelet has not reported within `--node-monitor-grace-period` (default 50s). |
| `DiskPressure` | Disk capacity is low on the node. The kubelet may evict pods to reclaim space. |
| `MemoryPressure` | Memory is low on the node. The kubelet may evict best-effort pods. |
| `PIDPressure` | Too many processes are running on the node. The kubelet may evict pods. |
| `NetworkUnavailable` | The node's network is not correctly configured (typically set by a network provider). |

The kubelet reports conditions periodically. The node controller interprets `Ready` to make scheduling and eviction decisions.

## Node Management

Administrators use `kubectl` to manage node availability during maintenance.

**Cordon** marks a node as unschedulable with `kubectl cordon <node>`. No new pods will be scheduled on it, but existing pods continue running. The `spec.unschedulable` field (also exposed via the `node.kubernetes.io/unschedulable` taint) is set to `true`.

**Drain** evicts all pods from a node gracefully: `kubectl drain <node> --ignore-daemonsets`. It cordons the node first, then evicts pods one by one, respecting `PodDisruptionBudget` and `terminationGracePeriodSeconds`. DaemonSet pods are excluded by default and must be handled separately or ignored with `--ignore-daemonsets`.

**Taints and tolerations** determine which pods can be scheduled on which nodes. A **taint** on a node repels pods that do not have a matching **toleration** on the pod spec. Taints have an effect: `NoSchedule` (don't schedule), `PreferNoSchedule` (soft preference), or `NoExecute` (evict existing pods). This is the foundational mechanism for dedicated nodes, node-level resource reservation, and handling node problems. See [Pods](./pods.md) for how tolerations are defined in the pod spec.

## Node Status

**Capacity** reports the total resources of the node (CPU, memory, ephemeral storage, max pods, etc.). **Allocatable** is the amount available for pods after reserving resources for system daemons (kubelet, container runtime, OS, kernel). The kubelet computes allocatable as `capacity - reserved` and uses it for pod admission decisions and resource accounting.

The difference between capacity and allocatable accounts for:

- `--system-reserved` — resources reserved for OS and system daemons (e.g., sshd, udev).
- `--kube-reserved` — resources reserved for Kubernetes daemons (kubelet, container runtime).
- `--eviction-hard` thresholds — a buffer to avoid resource exhaustion before eviction triggers.

**Node addresses** are listed in the status and used by the API server and kubelet for communication:

- `InternalIP` — the node's internal IP (reachable within the cluster).
- `ExternalIP` — the node's external IP (reachable from outside, if applicable).
- `Hostname` — the hostname reported by the kernel or kubelet.

Node addresses vary by provider — cloud controllers typically populate them, while self-managed clusters may have only `InternalIP` and `Hostname`.

## Node Controller

The **node controller** is a control plane component responsible for managing node lifecycle. It runs in `kube-controller-manager` and performs several functions:

- **Node monitor period** (`--node-monitor-period`, default 5s): the interval at which the node controller checks node status.
- **Node monitor grace period** (`--node-monitor-grace-period`, default 50s): if the node controller has not received a `Ready` status update within this period, it marks the node's `Ready` condition as `Unknown`. If the condition persists beyond a hardcoded 5-minute timeout, the node controller evicts all pods from the node. Pods on an unreachable node enter `Terminating` status.
- **CIDR assignment**: assigns `podCIDR` to nodes if non-overlapping CIDR allocation is enabled.
- **Cloud provider interaction**: when using a cloud provider, the node controller queries the cloud provider to determine if a node has been deleted (e.g., VM termination). If so, it deletes the Node object from the API.

The node lifecycle — from registration through health checks to eviction and deletion — is managed entirely by the node controller in combination with the kubelet and (optionally) the cloud-controller-manager.

## References

- [Nodes — Kubernetes Documentation](https://kubernetes.io/docs/concepts/architecture/nodes/)
- [Node Status](https://kubernetes.io/docs/reference/kubernetes-api/cluster-resources/node-v1/)
- [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
- [Node Controller](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/)
- [Kubernetes Architecture](./architecture.md)
- [Pods](./pods.md)
