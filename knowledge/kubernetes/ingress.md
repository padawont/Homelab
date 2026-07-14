---
title: "Ingress"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - networking
  - ingress
sources:
  - url: "https://kubernetes.io/docs/concepts/services-networking/ingress/"
    title: "Ingress — Kubernetes Documentation"
  - url: "https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/"
    title: "Ingress Controllers — Kubernetes Documentation"
last_audit_date: 2026-06-18
---
# Ingress

## Overview

Ingress exposes HTTP and HTTPS routes from outside the cluster to Services within the cluster. It provides host-based and path-based routing, TLS termination, and virtual hosting — all in a single API object. Ingress requires an Ingress Controller to function (the API object is just a spec).

## Ingress vs Service

Services (NodePort/LoadBalancer) expose a single Service. Ingress can route to multiple Services based on rules, consolidate TLS termination, and reduce the number of load balancers needed.

## Ingress Spec

Key fields: `spec.rules` (list of host + http paths), `spec.tls` (TLS certificates), `spec.defaultBackend` (fallback if no rules match). `pathType` supports `Prefix` (match on path prefix) and `Exact` (match exact path).

## Host-Based and Path-Based Routing

Host-based: routes to different backends based on the `Host` header. Path-based: routes based on URL path. Both can be combined.

## TLS Termination

`spec.tls[].hosts` lists the hostnames, `spec.tls[].secretName` references a TLS Secret containing `tls.crt` and `tls.key`.

## IngressClass

IngressClass defines which Ingress Controller serves a given Ingress via `spec.ingressClassName`. This allows multiple controllers in the same cluster.

## Example

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - example.com
    secretName: example-tls
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

## Cross-Links

- [Services](./services.md)
- [Network Policies](./network-policies.md)
