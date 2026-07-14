---
title: "Network Policies (NetworkPolicies)"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - networking
  - network-policies
  - security
sources:
  - url: "https://kubernetes.io/docs/concepts/services-networking/network-policies/"
    title: "Network Policies — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# Network Policies (NetworkPolicies)

## Overview

A NetworkPolicy specifies how groups of pods are allowed to communicate with each other and network endpoints. It uses pod selectors and namespace selectors to define traffic rules. By default, pods are non-isolated — they accept traffic from any source. Adding a NetworkPolicy that selects a pod isolates that pod (only allowed traffic passes).

## Spec

Key fields: `podSelector` (selects pods to apply policy to; empty selects all pods in namespace), `policyTypes` (Ingress, Egress — defaults to Ingress if not specified), `ingress` (list of allowed inbound rules), `egress` (list of allowed outbound rules).

## podSelector and namespaceSelector

`podSelector` targets pods by labels. `namespaceSelector` in ingress/egress rules targets namespaces by labels. `ipBlock` targets external CIDR ranges (outside the cluster). Combined: `namespaceSelector` and `podSelector` together = "pods with those labels in namespaces with those labels".

## Ingress and Egress Rules

Rules specify `from` (for ingress) or `to` (for egress) sources/destinations. Each entry can include `podSelector`, `namespaceSelector`, and `ipBlock`. `ports` limits allowed ports and protocols.

## Default Deny Patterns

Common patterns: deny all ingress (only allow what is explicitly permitted), allow specific pod on specific port, allow egress only to DNS (port 53 UDP/TCP).

Default deny all ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

Allow specific ingress on port 80:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-nginx
spec:
  podSelector:
    matchLabels:
      app: nginx
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 80
```

---

**Cross-links:** [Pods](./pods.md), [Services](./services.md)
