---
title: "Kubernetes overview"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, architecture, control-plane, worker-node]
sources:
  - url: "https://kubernetes.io/docs/concepts/overview/"
    title: "Kubernetes Overview"
  - url: "https://kubernetes.io/docs/concepts/overview/components/"
    title: "Kubernetes Components"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/architecture.md"
  - "./02_Knowledge/technologies/kubernetes/k3s/overview.md"
---

# Kubernetes overview

## Overview

Kubernetes (k8s) is a container orchestration platform. It schedules containerized workloads across a cluster of machines, restarts failed containers, scales replicas, and routes traffic to healthy pods. It is declarative: you describe the desired state and Kubernetes converges toward it.

A cluster has two roles:

- **Control plane** — the brain. Runs the API server, scheduler, controller managers, and etcd. Makes global decisions about the cluster.
- **Worker nodes** — the muscle. Run kubelet, kube-proxy, and the container runtime. Execute pods.

### Why run it in a homelab

- One declarative source of truth for services — no SSH + docker run sprawl.
- Self-healing: restarts crashed pods, reschedules on node failure.
- Uniform rollout and rollback for every app via Deployments.
- Resource limits and namespaces isolate experiments from core services.
- K3s keeps the control plane light enough for small clusters.

## Details

Mental model: the control plane watches worker nodes; workers run pods; the scheduler picks which node runs each pod.

| Layer | Components | Responsibility |
|---|---|---|
| Control plane | kube-apiserver, etcd, kube-scheduler, kube-controller-manager | Cluster state, decisions, reconciliation |
| Worker node | kubelet, kube-proxy, container runtime | Run pods, local networking |

Example — abstract:

```yaml
# Declarative desired state: 3 replicas of nginx
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx:1.27
```

Applying this tells the control plane the cluster should have 3 nginx pods; controllers and the scheduler make it happen.

Kubernetes vs docker-compose: compose is single-host and imperative-friendly; Kubernetes is multi-node, self-healing, and API-driven. Once a homelab grows past one node — or you want git-ops style declarative management — Kubernetes wins.

For the component deep dive, see the architecture note; for the lightweight distribution used in this homelab, see the k3s overview.

## Sources / Further Reading

- [Kubernetes Overview](https://kubernetes.io/docs/concepts/overview/)
- [Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/)
- [Architecture note](./02_Knowledge/technologies/kubernetes/concepts/architecture.md)
- [K3s overview](./02_Knowledge/technologies/kubernetes/k3s/overview.md)
