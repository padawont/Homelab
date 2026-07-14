---
title: "Kubernetes Pods"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - workloads
  - pods
sources:
  - url: "https://kubernetes.io/docs/concepts/workloads/pods/"
    title: "Pods — Kubernetes Documentation"
  - url: "https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/"
    title: "Pod Lifecycle — Kubernetes Documentation"
  - url: "https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/"
    title: "Pod Quality of Service — Kubernetes Documentation"
  - url: "https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/"
    title: "Managing Resources for Containers — Kubernetes Documentation"
last_audit_date: 2026-06-18
---
# Kubernetes Pods

## Overview

A Pod is the smallest deployable unit in Kubernetes — one or more containers with shared storage, network, and a specification for how to run them. Containers in a pod share an IP address, port space, and can communicate via localhost. Pods are ephemeral: they are created, assigned to a node, run until termination or failure, and are not automatically restarted (that is the job of controllers like Deployments).

## Pod Lifecycle

Pods progress through five phases. **Pending** means the pod has been accepted by the cluster but one or more containers are not yet running (still downloading images, waiting for scheduling). **Running** indicates at least one container is running or in the process of starting. **Succeeded** means all containers terminated with exit code 0. **Failed** means any container terminated with a non-zero exit code. **Unknown** indicates the node has lost contact with the pod (e.g. network partition). Pods move forward through this lifecycle — once terminal (Succeeded or Failed), the phase does not revert unless the pod is recreated by a controller.

## Init Containers

Init containers run before any app containers in the pod, always run to completion, and execute sequentially in the order defined. They can contain utilities or setup scripts not present in the app image, reducing image size and surface area. If an init container fails, Kubernetes restarts the pod (subject to `restartPolicy`) until it succeeds. Init containers support resource limits, volumes, and security contexts, but do not support lifecycle hooks, liveness probes, readiness probes, or startup probes.

## Sidecar Containers

Sidecar containers run alongside the main app container for the full pod lifetime, supporting their own startup, liveness, and readiness probes independently. Unlike init containers, they do not block the start of app containers. Common use cases include log shipping (Fluentd, Filebeat), network proxies (Envoy, Istio sidecars), and config reload watchers that tail ConfigMap or Secret changes. Sidecar containers share the pod's network namespace and volumes with the main container.

## Probes

Kubernetes provides three probe types to manage container health. **Liveness probes** determine if a container is still running; if the probe fails, the kubelet kills and restarts the container. **Readiness probes** determine if a container is ready to accept traffic; if the probe fails, the pod is removed from Service endpoints. **Startup probes** are used for slow-starting applications — they run at startup and disable liveness checks until they succeed, preventing premature container restarts.

Each probe supports three handler types: `exec` (runs a command inside the container), `httpGet` (performs an HTTP GET request against a port and path), and `tcpSocket` (attempts a TCP connection to a specified port). All probes share configurable fields: `initialDelaySeconds`, `periodSeconds`, `timeoutSeconds`, `successThreshold`, and `failureThreshold`.

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 3
  periodSeconds: 3
readinessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy
  initialDelaySeconds: 5
  periodSeconds: 5
```

## QoS Classes

Quality of Service (QoS) classes determine pod priority under resource pressure and are derived from CPU and memory requests and limits. **Guaranteed** — every container in the pod has both CPU and memory requests and limits set, and they are equal. **Burstable** — at least one container has a CPU or memory request set, but limits exceed requests (or are unset). **BestEffort** — no container has any CPU or memory requests or limits set. Under node pressure, the kubelet evicts pods in order: BestEffort first, then Burstable, then Guaranteed.

## Restart Policies

The pod spec supports three restart policies controlling container restart behavior. `Always` (default for Deployments, StatefulSets, DaemonSets) restarts the container after any exit. `OnFailure` restarts only when the exit code is non-zero. `Never` never restarts the container. The restart policy applies to all containers in the pod, including init containers (with the caveat that init containers always restart on failure until success regardless of policy).

## Pod Conditions

Pod conditions are a set of True/False/Unknown status signals that provide visibility into the pod's state. **PodScheduled** — the pod has been assigned to a node. **Initialized** — all init containers have completed successfully. **ContainersReady** — all containers in the pod are passing their readiness probes. **Ready** — the pod is ready to serve traffic (all containers ready and conditions met). Conditions are reported by the kubelet and consumed by controllers and scheduling components.

## Static Pods

Static pods are managed directly by the kubelet on a specific node, created from manifest files located in the node's manifest directory (typically `/etc/kubernetes/manifests`). They bypass the API server — the kubelet watches the manifest directory and creates or deletes pods as files change. The kubelet creates a mirror pod object in the API server for visibility, but these mirror pods cannot be edited or deleted through the API. Static pods are commonly used to bootstrap control-plane components like `kube-apiserver`, `kube-controller-manager`, and `etcd`.

## References

- [Pods — Kubernetes Documentation](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Pod Lifecycle — Kubernetes Documentation](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Pod Quality of Service — Kubernetes Documentation](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Managing Resources for Containers — Kubernetes Documentation](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Architecture](./architecture.md)
- [Nodes](./nodes.md)
