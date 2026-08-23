---
title: "Kubernetes Ingress"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, networking, ingress]
sources:
  - url: "https://kubernetes.io/docs/concepts/services-networking/ingress/"
    title: "Kubernetes Ingress documentation"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/services.md"
---

# Kubernetes Ingress

## Overview

Ingress exposes HTTP/HTTPS routes from outside the cluster to Services inside
it. It is a set of routing rules; the actual proxy that enforces them is an
Ingress controller (in this homelab: Traefik, shipped by k3s). Ingress is how
`git.homelab.local` and other homelab hostnames reach their services.

## Details

### Ingress rules

An Ingress rule maps a host (and path) to a backend Service. Each rule can
have multiple paths; the controller merges rules into its routing table.

- `host`: the DNS name this rule applies to. Omit it to match all hosts.
- `path`: URL path matched on the host.
- `backend`: the Service name and port to forward matched traffic to.

### pathType

| pathType | Behaviour |
|---|---|
| `Prefix` | Matches the path and everything below it (`/` matches all paths) |
| `Exact` | Matches only the exact, case-sensitive URL path |
| `ImplementationSpecific` | Controller-defined; not portable — avoid for homelab portability |

### TLS

- `spec.tls` configures TLS termination: a `hosts` list and a `secretName`
  referencing a TLS Secret containing `tls.crt` and `tls.key`.
- Cert-manager (if deployed) auto-creates/rotates these secrets; otherwise
  supply your own cert Secret.

### IngressClass

- `spec.ingressClassName` selects which controller handles the Ingress
  (k3s ships the `traefik` IngressClass by default).
- An IngressClass object can declare `default: true` so resources without an
  explicit class use it.

Example — abstract:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  namespace: default
spec:
  ingressClassName: traefik
  rules:
    - host: example.com
      http:
        paths:
          - path: /app
            pathType: Prefix
            backend:
              service:
                name: app-service
                port:
                  number: 80
```

Example — real config:

```yaml
# actual running config, may drift
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: forgejo-ingress
  namespace: forgejo
spec:
  ingressClassName: traefik
  rules:
    - host: git.homelab.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: forgejo-http
                port:
                  number: 3000
```

### Homelab notes

- Traefik watches Ingress objects and also supports IngressRoute (CRD) for
  advanced routing; the standard Ingress resource works fine for most services.
- Hostnames like `*.homelab.local` must resolve to the cluster (./02_Knowledge/technologies/kubernetes/concepts/dns.md) and
  the controller must be reachable on ports 80/443.
- A Service (./02_Knowledge/technologies/kubernetes/concepts/services.md) must exist in the same namespace as the Ingress
  backend reference.

## Sources / Further Reading

- Kubernetes docs — Ingress: https://kubernetes.io/docs/concepts/services-networking/ingress/
- Kubernetes docs — Ingress controllers: https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/
