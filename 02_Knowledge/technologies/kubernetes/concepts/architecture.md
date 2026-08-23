---
title: "Kubernetes architecture"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, architecture, control-plane, etcd, kubelet, cri]
sources:
  - url: "https://kubernetes.io/docs/concepts/overview/components/"
    title: "Kubernetes Components"
  - url: "https://kubernetes.io/docs/concepts/containers/cri/"
    title: "Container Runtime Interface (CRI)"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/pods.md"
---

# Kubernetes architecture

## Overview

Kubernetes is split into a control plane (cluster-wide decisions) and worker nodes (running workloads). All control-plane components coordinate through the kube-apiserver; on nodes, the kubelet additionally talks directly to the container runtime via CRI. Understanding which component does what makes troubleshooting faster: etcd problems look like API instability, kubelet problems look like pods stuck on one node.

## Details

### Control plane components

- **etcd** — distributed key-value store holding all cluster state (objects, secrets, config). Source of truth. Back it up; if it is lost, the cluster is lost.
- **kube-apiserver** — front door for all reads/writes. Validates and persists objects to etcd, authenticates and authorizes requests. The only component that touches etcd.
- **kube-scheduler** — decides which node a new pod runs on, based on resource requests, affinity, taints/tolerations, and data locality.
- **kube-controller-manager** — runs controller loops that reconcile desired state: node controller, replica controller, endpoints controller, and more. Each controller watches the API and acts on drift.

### Worker node components

- **kubelet** — the node agent. Registers the node, receives pod specs, starts containers via the runtime, reports status and metrics.
- **kube-proxy** — maintains node networking rules so Services route to pods. Implements ClusterIP, NodePort, LoadBalancer traffic.
- **Container Runtime Interface (CRI)** — a plugin API that lets kubelet talk to any runtime (containerd, CRI-O). The runtime pulls images and runs containers with namespaces/cgroups.

### Data flow on pod creation

1. You POST a Deployment to kube-apiserver.
2. apiserver validates and stores it in etcd.
3. Deployment controller creates a ReplicaSet; ReplicaSet controller creates a Pod object.
4. Scheduler assigns the pod to a node and writes the binding.
5. kubelet on that node sees the assignment, asks the runtime (via CRI) to start containers.

Example — abstract:

```yaml
# kubelet asks the CRI runtime to run a container
# (simplified view — normal users never call CRI directly)
runtimeEndpoint: unix:///var/run/containerd/containerd.sock
image: nginx:1.27
command: ["/docker-entrypoint.sh"]
```

## Sources / Further Reading

- [Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/)
- [Container Runtime Interface (CRI)](https://kubernetes.io/docs/concepts/containers/cri/)
- [Pods note](./02_Knowledge/technologies/kubernetes/concepts/pods.md)
