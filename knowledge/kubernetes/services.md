---
title: "Services (ClusterIP, NodePort, LoadBalancer, ExternalName)"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - networking
  - services
sources:
  - url: "https://kubernetes.io/docs/concepts/services-networking/service/"
    title: "Service — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# Services (ClusterIP, NodePort, LoadBalancer, ExternalName)

## Overview
A Service is an abstract way to expose an application running on a set of pods as a network service. Services provide a stable IP and DNS name that persists independent of pod churn. They use label selectors to identify target pods and load-balance traffic across them.

## Service Types

**ClusterIP** (default): exposes the Service on a cluster-internal IP. Only reachable within the cluster. Ideal for internal microservice communication. Example:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-svc
spec:
  selector:
    app: my-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

**NodePort**: exposes the Service on each node's IP at a static port (30000-32767). Traffic to `<nodeIP>:<nodePort>` is routed to the Service. The cluster automatically creates a ClusterIP Service as well.

**LoadBalancer**: exposes the Service externally using a cloud provider's load balancer. The cloud controller creates the LB and routes traffic to the NodePort (and ClusterIP) underneath. Specific to cloud environments (AWS ELB, GCP LB, Azure LB).

**ExternalName**: maps a Service to an external DNS name using CNAME. No selector, no port routing. Example: `spec.externalName: api.example.com`.

## Port Definitions
- `port`: the port the Service listens on
- `targetPort`: the port on the pod to forward to (defaults to `port` if unset)
- `nodePort`: the port on each node (for NodePort type, auto-assigned if unset)

## Headless Services
Set `clusterIP: None` to create a headless Service. No load balancing — DNS returns all pod IPs directly. Used by StatefulSets for stable pod identity DNS.

## EndpointSlices
EndpointSlices are the modern replacement for Endpoints, tracking which pods match a Service's selector. They scale better for large Services and can be managed independently.

## NodePort Example

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nodeport-svc
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080
```

## Cross-links
- [Pods](./pods.md)
- [Ingress](./ingress.md)
- [DNS](./dns.md)
- [Network Policies](./network-policies.md)
- [StatefulSets](./statefulsets.md)
