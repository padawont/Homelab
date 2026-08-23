---
title: "Kubernetes DNS and CoreDNS"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, networking, dns]
sources:
  - url: "https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/"
    title: "Kubernetes DNS for Services and Pods"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/services.md"
---

# Kubernetes DNS and CoreDNS

## Overview

Every Kubernetes cluster runs an in-cluster DNS service (k3s ships CoreDNS) at
`kube-dns.kube-system.svc.cluster.local`. Pods use it automatically to resolve
Service names, Pod names, and external hostnames, so workloads can talk to each
other by name instead of hard-coded IPs.

## Details

### Service DNS records

A Service gets a DNS name of the form:

```
<service>.<namespace>.svc.<cluster-domain>
```

- Default cluster domain: `cluster.local` (k3s default).
- Within the same namespace, a Pod can use the short name (`forgejo-http`).
- Headless Services return multiple A records (one per backing Pod).

### Pod DNS records

- Pods get A records when hostname and subdomain are set (commonly via a
  headless Service): `<hostname>.<subdomain>.<namespace>.svc.<cluster-domain>`.
- Pod IPs also get PTR records for reverse lookups.
- Pod `hostname` defaults to the Pod name; `subdomain` must match a headless
  Service in the same namespace for the record to exist.

### dnsPolicy

Controls how a Pod populates `/etc/resolv.conf`:

| Policy | Behaviour |
|---|---|
| `ClusterFirst` (default) | Uses the cluster DNS (CoreDNS) as primary resolver |
| `Default` | Inherits the node's `/etc/resolv.conf` — no cluster DNS |
| `None` | Ignores k8s DNS; you supply `dnsConfig` manually |
| `ClusterFirstWithHostNet` | Cluster DNS even for host-network Pods |

`dnsConfig` can add options/nameservers/search domains on top of the policy.

Example — abstract:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tools
spec:
  dnsPolicy: ClusterFirst
  dnsConfig:
    nameservers:
      - 1.1.1.1
    searches:
      - homelab.local
```

### Homelab notes

- CoreDNS runs as a Deployment in `kube-system`; edit its ConfigMap
  (`coredns`) to add custom zones or forwarders.
- For `*.homelab.local` names to work, add a forward/rewrite in CoreDNS or
  point your router/DNS at the cluster (e.g. Pi-hole → CoreDNS).
- External DNS names are resolved via CoreDNS upstream forwarders to the
  node's resolvers.

## Sources / Further Reading

- Kubernetes docs — DNS for Services and Pods: https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/
- CoreDNS documentation: https://coredns.io/
