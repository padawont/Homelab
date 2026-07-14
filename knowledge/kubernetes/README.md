# Kubernetes

Foundational concepts covering Kubernetes architecture, workloads, networking, storage, configuration, and RBAC. These notes serve as the authoritative reference for all Kubernetes tool-specific topics in the knowledge base (k3d, k9s, Rancher, Helm, Cilium, DevSpace, hcloud CLI).

## Architecture

- [architecture.md](./architecture.md) — Control plane components (etcd, API Server, Scheduler, Controller Manager) and node components (kubelet, container runtime, kube-proxy)
- [nodes.md](./nodes.md) — Node objects, conditions (Ready, DiskPressure, MemoryPressure), cordon and drain, node status
- [node-1 cluster config](../../configs/kubernetes/node-1/) — Live cluster state, nodes, and kubeconfig from the homelab's K3s node

## Workloads

- [pods.md](./pods.md) — Pod lifecycle phases, init containers, probes (liveness, readiness, startup), QoS classes, restart policies
- [replicasets.md](./replicasets.md) — ReplicaSet selector matching, scaling, ownership by Deployments
- [deployments.md](./deployments.md) — Deployment strategies (Recreate, RollingUpdate), rollbacks, revision history, paused deployments
- [statefulsets.md](./statefulsets.md) — StatefulSet ordinal identity, headless Services, PVC templates, ordered pod management
- [daemonsets.md](./daemonsets.md) — DaemonSet node-level scheduling, rolling update strategy
- [jobs.md](./jobs.md) — Job completions and parallelism, backoff limits, TTL, CronJob schedule syntax

## Networking

- [services.md](./services.md) — Service types (ClusterIP, NodePort, LoadBalancer, ExternalName), EndpointSlices, headless Services
- [ingress.md](./ingress.md) — Ingress rules, TLS termination, path-based and host-based routing, IngressClass
- [network-policies.md](./network-policies.md) — NetworkPolicy pod and namespace selectors, ingress and egress rules, default deny patterns
- [dns.md](./dns.md) — CoreDNS, Service and Pod DNS records, dnsPolicy, custom DNS configuration

## Storage

- [storage.md](./storage.md) — PersistentVolumes, PersistentVolumeClaims, StorageClasses, access modes, reclaim policies, dynamic provisioning

## Configuration & Secrets

- [configmaps.md](./configmaps.md) — ConfigMap creation, environment injection, volume mounts, immutability
- [secrets.md](./secrets.md) — Secret types (Opaque, TLS, registry), data encoding, etcd encryption, immutability
- [service-accounts.md](./service-accounts.md) — ServiceAccount creation, automount, TokenRequest API, projected volumes

## RBAC

- [rbac.md](./rbac.md) — Roles, ClusterRoles, RoleBindings, ClusterRoleBindings, aggregated ClusterRoles, RBAC good practices

## Tooling

- [k3d](k3d/) — Lightweight local Kubernetes clusters using k3s and Docker containers
- [k9s](k9s/) — Terminal-based Kubernetes cluster UI for navigating and debugging clusters
- [Rancher](rancher/) — Kubernetes multi-cluster management platform with RBAC, monitoring, and application lifecycle
- [cilium](cilium/) — eBPF-based CNI, network policy enforcement, and Hubble observability
- [Helm](helm/) — Kubernetes package management with charts, templating, releases, and repository management
- [DevSpace](devspace/) — Kubernetes-native development tool for hot reloading, file synchronization, and in-cluster development workflows

---

See the [Kubernetes Documentation](https://kubernetes.io/docs/home/) for the official reference.
