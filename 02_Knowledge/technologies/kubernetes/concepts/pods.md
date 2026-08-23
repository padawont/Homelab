---
title: "Pods in Kubernetes"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, pods, workloads, probes, qos]
sources:
  - url: "https://kubernetes.io/docs/concepts/workloads/pods/"
    title: "Kubernetes Pods"
  - url: "https://kubernetes.io/docs/concepts/workloads/pods/probes/"
    title: "Liveness, Readiness, and Startup Probes"
  - url: "https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/"
    title: "Pod Quality of Service Classes"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/deployments.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/statefulsets.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/services.md"
---

# Pods in Kubernetes

## Overview

A Pod is the smallest deployable unit in Kubernetes: one or more containers that share a network namespace, IP address, and storage volumes. Containers in a pod are co-located and co-scheduled — use multiple containers for tight coupling (sidecars), not for unrelated services. In a homelab you rarely create pods directly; Deployments and StatefulSets manage them for you.

## Details

### Lifecycle phases

| Phase | Meaning |
|---|---|
| Pending | Accepted, but containers not all running (scheduling, image pull) |
| Running | At least one container running |
| Succeeded | All containers exited 0 and will not restart |
| Failed | All containers exited non-zero |
| Unknown | Node lost contact with the pod |

Containers also have states: Waiting, Running, Terminated. CrashLoopBackOff means a container keeps starting and dying.

### Init containers

Init containers run to completion before the main container starts. Use them to wait for dependencies, seed config, or set permissions. If an init container fails, the pod restarts it until success.

### Probes

| Probe | Purpose | Action on failure |
|---|---|---|
| liveness | Is the app alive (not deadlocked)? | Restart the container |
| readiness | Is it ready to serve traffic? | Remove from Service endpoints |
| startup | Slow-starting apps? | Delay liveness checks until ready |

Prefer readiness for most homelab apps; liveness restarts can mask real problems.

### QoS classes

Request/limit combinations classify pods:

| Class | Request vs limit | Eviction priority (lowest first) |
|---|---|---|
| Guaranteed | requests == limits (all containers) | Never evicted for resource pressure |
| Burstable | at least one container has a request | Evicted after Guaranteed |
| BestEffort | no requests or limits | Evicted first |

Example — abstract:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
spec:
  initContainers:
    - name: wait-for-db
      image: busybox
      command: ["sh", "-c", "until nc -z db 5432; do sleep 1; done"]
  containers:
    - name: web
      image: nginx:1.27
      ports:
        - containerPort: 80
      readinessProbe:
        httpGet:
          path: /healthz
          port: 80
      resources:
        requests: {cpu: 100m, memory: 128Mi}
        limits: {cpu: 200m, memory: 256Mi}
```

## Sources / Further Reading

- [Kubernetes Pods](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Liveness, Readiness, and Startup Probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/)
- [Pod Quality of Service Classes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Deployments note](./02_Knowledge/technologies/kubernetes/concepts/deployments.md)
- [StatefulSets note](./02_Knowledge/technologies/kubernetes/concepts/statefulsets.md)
- [Services note](./02_Knowledge/technologies/kubernetes/concepts/services.md)
