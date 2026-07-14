---
title: "Kubernetes Architecture"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - architecture
  - control-plane
sources:
  - url: "https://kubernetes.io/docs/concepts/overview/components/"
    title: "Kubernetes Components — Official Documentation"
  - url: "https://kubernetes.io/docs/concepts/architecture/"
    title: "Cluster Architecture — Official Documentation"
last_audit_date: 2026-06-18
---

# Kubernetes Architecture

## Overview

Kubernetes architecture follows a flat network model where every pod gets its own IP address and communicates directly with other pods without NAT. The system is split into a **control plane** (brain of the cluster) and **worker nodes** (where workloads run). The control plane makes global decisions about the cluster (scheduling, scaling, responding to failures), while nodes execute those decisions by running containers.

The control plane components can run on any node but are typically isolated to dedicated control plane machines for reliability. Nodes are the workers that run containerized applications via pods. Understanding this boundary is essential to operating Kubernetes --- see [Nodes](./nodes.md) and [Pods](./pods.md) for deeper dives into each.

## Control Plane Components

### etcd

etcd is a consistent, distributed key-value store that serves as Kubernetes' backing store for all cluster data. It uses the **Raft consensus algorithm** to maintain consistency across replicas. Every cluster state --- pods, secrets, configmaps, services, and namespace metadata --- is stored in etcd.

Operators must back up etcd regularly (snapshots via `etcdctl snapshot save` or automated tooling). Loss of etcd data means loss of the cluster state. etcd can run on the same machines as other control plane components or on dedicated hosts. A typical high-availability setup uses three or five etcd members.

### kube-apiserver

The kube-apiserver exposes the Kubernetes API as a RESTful interface over HTTPS. It is the front-end for the control plane, designed to scale horizontally --- deploy more instances to handle more traffic. Every operation (kubectl, internal controllers, external automation) goes through the API server.

Requests pass through a pipeline: **authentication** (who is making the request), **authorization** (is that identity allowed), and **admission controllers** (mutating or validating webhooks that enforce policies before persistence). The API server validates and persists data to etcd, then responds to the client. It is the only component that communicates with etcd.

### kube-scheduler

The kube-scheduler watches for newly created pods that have no node assigned and selects a suitable node for them to run on. Scheduling decisions account for individual and collective resource requirements, hardware/software constraints, affinity and anti-affinity specifications, taints and tolerations, and data locality.

Predicates filter out nodes that cannot run the pod (e.g., insufficient CPU or memory). Priorities rank the remaining nodes to find the best fit. The scheduler does not actually place pods --- it merely assigns a node binding; the kubelet on that node handles the actual pod creation.

### kube-controller-manager

The kube-controller-manager runs controller processes as a single binary. Each controller is a loop that watches the shared state (via the API server) and makes changes to move the current state toward the desired state.

Key controllers include:

- **Node Controller**: monitors node health via kubelet heartbeats; marks the node's `Ready` condition as `Unknown` after `--node-monitor-grace-period` (default 50s), and evicts pods after a hardcoded 5-minute timeout.
- **Replication Controller**: ensures the correct number of pod replicas are running for a ReplicationController or ReplicaSet object.
- **Endpoints Controller**: populates Endpoints objects (the bridge between Services and Pods).
- **Service Account & Token Controllers**: create default accounts and API access tokens for namespaces.

## Node Components

### kubelet

The kubelet is the primary node agent that runs on every node. It registers the node with the cluster (using hostname, flags, or cloud provider metadata) and watches for pod assignments from the API server. When a pod is scheduled to its node, the kubelet creates or destroys containers to match the pod spec.

The kubelet uses the **PodSync** loop to regularly compare the desired state (from the API server) with the actual state (from the container runtime). If a container crashes, the kubelet restarts it according to the pod's restart policy. It also reports node and pod status back to the API server and runs liveness, readiness, and startup probes.

### Container Runtime

The container runtime is the software responsible for running containers. Kubernetes supports any runtime that implements the **Container Runtime Interface (CRI)**. The most common runtimes are **containerd** (the default in most distributions) and **CRI-O** (optimized for Kubernetes).

The kubelet delegates all container lifecycle operations (pull images, start/stop containers, manage filesystem mounts) to the runtime via CRI. This abstraction means the kubelet does not need to know the specifics of any runtime; it just calls CRI methods.

### kube-proxy

kube-proxy is a network proxy that runs on each node. It watches the API server for Service and EndpointSlice changes and maintains network rules that allow pods to communicate with services. It implements service routing through one of several modes:

- **iptables mode** (default): creates iptables rules to redirect service traffic to backend pods. Simple and stable but with O(n) rule chain performance as services scale.
- **IPVS mode**: uses Linux IPVS (IP Virtual Server) for more efficient round-robin and O(1) performance, at the cost of requiring the `ipvsadm` kernel module and tools.

kube-proxy is not required for all use cases --- projects like Cilium and other CNI plugins often replace it entirely.

## Container Runtime Interface (CRI)

CRI is a **protocol buffer** and **gRPC** API that defines how the kubelet communicates with container runtimes. It includes two main services: `RuntimeService` (managing pods and containers lifecycle) and `ImageService` (managing images).

The CRI abstraction allows Kubernetes to support multiple container runtimes without changing the kubelet code. Any runtime that implements the CRI gRPC server can run pods. The most widely used implementations are **containerd** (which ships its own CRI plugin) and **CRI-O**. Docker Engine was supported via the `dockershim` adapter, which was removed in Kubernetes 1.24.

## Add-ons

Add-ons are cluster features implemented as pods and services. They are not part of the core Kubernetes binaries but are essential for a functional cluster:

- **DNS (CoreDNS)**: every cluster should have cluster DNS. It assigns DNS names to Services and pods, enabling service discovery within the cluster.
- **Web UI (Dashboard)**: a general-purpose web UI for managing cluster resources.
- **Monitoring**: solutions like Prometheus and Metrics Server collect resource usage and performance data.
- **Logging**: cluster-level log aggregation (e.g., Fluentd + Elasticsearch, Loki) centralizes container logs.
- **Network Plugins (CNI)**: Calico, Flannel, Weave, Cilium --- each implements the Container Network Interface for pod networking.

## References

- [Kubernetes Components — Official Documentation](https://kubernetes.io/docs/concepts/overview/components/)
- [Cluster Architecture — Official Documentation](https://kubernetes.io/docs/concepts/architecture/)
- [Container Runtime Interface (CRI) — Kubernetes Documentation](https://kubernetes.io/docs/concepts/architecture/cri/)
- [etcd Overview](https://etcd.io/docs/)
