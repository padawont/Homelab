---
title: "Cilium Network Policies"
status: draft
author: padawont
date: 2026-07-11
tags:
  - cilium
  - network-policies
  - security
  - kubernetes
  - ebpf
sources:
  - url: "https://docs.cilium.io/en/stable/security/policy/"
    title: "Overview of Network Policy"
  - url: "https://docs.cilium.io/en/stable/security/policy/layer3/"
    title: "Layer 3 Policies"
  - url: "https://docs.cilium.io/en/stable/security/policy/layer4/"
    title: "Layer 4 Policies"
  - url: "https://docs.cilium.io/en/stable/security/policy/layer7/"
    title: "Layer 7 Policies"
  - url: "https://docs.cilium.io/en/stable/security/policy/deny/"
    title: "Deny Policies"
  - url: "https://docs.cilium.io/en/stable/network/kubernetes/policy/"
    title: "Kubernetes Network Policy"
  - url: "https://docs.cilium.io/en/stable/security/policy/lifecycle/"
    title: "Endpoint Lifecycle"
  - url: "https://docs.cilium.io/en/stable/security/policy/caveats/"
    title: "Policy Caveats"
last_audit_date: 2026-07-11
---

# Cilium Network Policies

This note covers CiliumNetworkPolicy and CiliumClusterwideNetworkPolicy CRDs. Prerequisite: understand Kubernetes [NetworkPolicy](../network-policies.md) basics.

## CRD Overview

Cilium provides two custom resource definitions (CRDs) for network policy:

| CRD | Scope | Use Case |
|---|---|---|
| `CiliumNetworkPolicy` | Namespaced | Applies to pods within a single namespace |
| `CiliumClusterwideNetworkPolicy` | Cluster-wide | Applies across all namespaces, or to nodes/hosts |

Both use `apiVersion: cilium.io/v2` and support the same rule structure. The key difference is that `CiliumClusterwideNetworkPolicy` can select pods across any namespace using namespace labels.

### Default Deny Model

When any policy selects an endpoint, that endpoint enters default-deny mode for the traffic direction covered by the policy section (ingress or egress). To explicitly deny all ingress:

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "default-deny-ingress"
spec:
  endpointSelector: {}
  ingress:
  - {}
```

The empty `endpointSelector: {}` selects all endpoints. The presence of the `ingress` section triggers default-deny on ingress. The empty rule `{}` within ingress means "allow nothing" (since an empty endpoint selector under ingress would otherwise allow all).

To deny all egress:

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "default-deny-egress"
spec:
  endpointSelector: {}
  egress:
  - {}
```

## Layer 3 Policies

Layer 3 rules define which endpoints can communicate based on identity, entity, CIDR, DNS name, or service.

### Endpoint Selectors

The fundamental building block is the endpoint selector using Kubernetes labels:

```yaml
endpointSelector:
  matchLabels:
    app: backend
```

An empty selector `{}` matches all endpoints.

### Entities

Pre-defined entity groups for common peer categories:

| Entity | Description |
|---|---|
| `host` | The local host node (including host-networking pods) |
| `remote-node` | Any node in connected clusters other than the local host |
| `kube-apiserver` | The Kubernetes API server |
| `cluster` | All endpoints inside the local cluster |
| `world` | All endpoints outside the cluster (equivalent to `0.0.0.0/0`) |
| `all` | Combination of all clusters + world |

**Allow ingress from outside the cluster:**

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "from-world"
spec:
  endpointSelector:
    matchLabels:
      role: public
  ingress:
  - fromEntities:
    - world
```

### CIDR-Based

Use when the remote peer is not managed by Cilium (external services, VMs):

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "cidr-rule"
spec:
  endpointSelector:
    matchLabels:
      app: myService
  egress:
  - toCIDR:
    - 20.1.1.1/32
  - toCIDRSet:
    - cidr: 10.0.0.0/8
      except:
      - 10.96.0.0/12
```

CIDR rules only apply when one side of the connection is not managed by Cilium. For in-cluster traffic, use endpoint selectors instead.

### DNS-Based (toFQDNs)

Allow egress to external domains by DNS name. Requires a DNS proxy rule to intercept DNS traffic:

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "to-fqdn"
spec:
  endpointSelector:
    matchLabels:
      app: test-app
  egress:
  - toEndpoints:
    - matchLabels:
        "k8s:io.kubernetes.pod.namespace": kube-system
        "k8s:k8s-app": kube-dns
    toPorts:
    - ports:
       - port: "53"
         protocol: ANY
      rules:
        dns:
        - matchPattern: "*"
  - toFQDNs:
    - matchName: "my-remote-service.com"
```

- `matchName` matches exact domain names
- `matchPattern` supports `*` wildcards (e.g., `*.cilium.io` matches `sub.cilium.io`)
- The DNS proxy intercepts egress DNS traffic and learns IPs from responses

### Service-Based

Allow traffic to Kubernetes services:

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "service-rule"
spec:
  endpointSelector:
    matchLabels:
      id: app2
  egress:
  - toServices:
    - k8sService:
        serviceName: myservice
        namespace: default
```

## Layer 4 Policies

Restrict traffic by port and protocol within L3 rules:

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "l4-rule"
spec:
  endpointSelector:
    matchLabels:
      app: myService
  ingress:
  - fromEndpoints:
    - matchLabels:
        role: frontend
    toPorts:
    - ports:
      - port: "80"
        protocol: TCP
      - port: "443"
        protocol: TCP
```

Port ranges are supported using the `port` + `endPort` fields (e.g., `port: "10000"` with `endPort: 20000`). Port ranges are not supported for DNS L7 rules.

## Layer 7 Policies

L7 rules are embedded within L4 `toPorts` rules and apply to specific protocols (HTTP, DNS, Kafka). Only one L7 protocol type per `toPorts` entry.

### HTTP

Match on method, path (POSIX regex), host, and headers:

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "l7-http-rule"
spec:
  endpointSelector:
    matchLabels:
      app: myService
  ingress:
  - toPorts:
    - ports:
      - port: "80"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/public"
        - method: "PUT"
          path: "/api/.*"
          headers:
          - "X-My-Header: true"
```

L7 HTTP violations return an HTTP 403 response (not a packet drop).

### DNS

Control which DNS queries are allowed. Requires a DNS proxy rule:

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "dns-rule"
spec:
  endpointSelector:
    matchLabels:
      any:org: alliance
  egress:
  - toEndpoints:
    - matchLabels:
       "k8s:io.kubernetes.pod.namespace": kube-system
       "k8s:k8s-app": kube-dns
    toPorts:
    - ports:
       - port: "53"
         protocol: ANY
      rules:
        dns:
        - matchName: "cilium.io"
        - matchPattern: "*.cilium.io"
```

**Alpine/musl caveat:** Some container images (Alpine) treat DNS `REFUSED` as a terminal failure and stop traversing the search list. Mitigate with `--tofqdns-dns-reject-response-code=nameError` on the Cilium agent, or configure `ndots` appropriately.

## Deny Policies

Deny policies take precedence over ALL allow policies, regardless of order or CRD type. Available since Cilium 1.9.

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: "external-lockdown"
spec:
  endpointSelector: {}
  ingressDeny:
  - fromEntities:
    - "world"
  ingress:
  - fromEntities:
    - "all"
```

This denies all ingress from outside the cluster while allowing all internal ingress.

**Deny policy limitations:**
- L7 deny (denying a specific URL) is NOT supported
- `toFQDNs` deny is NOT supported

### Deny Precedence Rules

| Scenario | Result |
|---|---|
| Allow L3 + Deny L4 (same port) | Denied |
| Allow L4 (port 80) + Deny L3 (pod selector) | Denied |
| Allow L4 (port 81) + Deny L4 (port 80) | Port 81 allowed, port 80 denied |
| Allow only (no deny) | Normal enforcement |

## CiliumClusterwideNetworkPolicy

For policies that must span namespaces:

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: "allow-cross-ns"
spec:
  endpointSelector:
    matchLabels:
      app: shared-service
  ingress:
  - fromEndpoints:
    - matchLabels:
        "k8s:io.kubernetes.pod.namespace": tenant-a
```

Cilium automatically adds labels prefixed with `k8s:` to each pod, including `k8s:io.kubernetes.pod.namespace` for the pod's namespace and `k8s:app`-style labels for Kubernetes app labels.

For installation instructions, see [installation.md](installation.md). For debugging policy issues, see [troubleshooting.md](troubleshooting.md).

## Good Example: Lock Down a Default Namespace

This policy allows egress only to `kube-dns` on UDP 53 and denies all ingress in the `default` namespace:

```yaml
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "default-deny-with-dns"
  namespace: default
spec:
  endpointSelector: {}
  ingress:
  - {}
  egress:
  - toEndpoints:
    - matchLabels:
        "k8s:io.kubernetes.pod.namespace": kube-system
        "k8s:k8s-app": kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
      rules:
        dns:
        - matchPattern: "*"
```
