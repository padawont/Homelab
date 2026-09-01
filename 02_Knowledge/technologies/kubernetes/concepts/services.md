---
title: "Kubernetes Services"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, networking, services]
sources:
  - url: "https://kubernetes.io/docs/concepts/services-networking/service/"
    title: "Kubernetes Service documentation"
last_audit_date: 2026-08-25
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/ingress.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/dns.md"
---

# Kubernetes Services

## Overview

A Service is a stable network endpoint in front of a set of Pods. Pods are
ephemeral and get new IPs when recreated; the Service gives workloads a stable
DNS name and IP, and load-balances traffic to the matching Pods via label
selectors. Homelab services (forgejo, homepage, etc.) are almost always reached
through a Service that an Ingress then exposes.

## Details

### Service types

| Type | Scope | Use case |
|---|---|---|
| ClusterIP (default) | Cluster-internal | Default; reachable only inside the cluster |
| NodePort | `<node-IP>:<port>` | Fixed port on every node; superset of ClusterIP |
| LoadBalancer | External LB | Provisions an external load balancer (MetalLB, cloud LB); superset of NodePort |
| ExternalName | DNS CNAME | Maps the Service name to an external DNS name; no selector, no Pods |

### Selectors and EndpointSlices

- A Service with a `selector` automatically manages EndpointSlices — the
  objects that track the actual Pod IPs and ports backing the Service.
- Each EndpointSlice covers a set of endpoints for a Service, keyed by port.
  The legacy `Endpoints` API is derived from EndpointSlices.
- A Service without a selector (e.g. pointing at an external database) does not
  create EndpointSlices; you create them manually to route to arbitrary IPs.

### Headless Services

- Set `clusterIP: None` to create a headless Service: no ClusterIP and no
  load balancing.
- DNS returns the individual backing Pod IPs (A/AAAA records) instead of one
  virtual IP — useful for stateful workloads that need per-Pod identity or
  client-side discovery.

Example — abstract:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```

Example — abstract headless:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db-headless
spec:
  clusterIP: None
  selector:
    app: db
  ports:
    - port: 5432
```

### Homelab notes

- k3s ships kube-proxy (iptables/ipvs) which implements Service load balancing
  — no extra component needed for ClusterIP/NodePort.
- k3s bundles ServiceLB (klipper-lb) as the default LoadBalancer — LoadBalancer
  Services get a host-port-backed external address automatically. Install MetalLB
  only if you disable ServiceLB (`--disable=servicelb`) or need a real VIP/anycast LB.
- Ingress rules reference Services by name; see `./02_Knowledge/technologies/kubernetes/concepts/ingress.md` for the other half of external traffic.

## Sources / Further Reading

- Kubernetes docs — Service: https://kubernetes.io/docs/concepts/services-networking/service/
- Kubernetes docs — EndpointSlices: https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/
