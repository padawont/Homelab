---
title: "Kubernetes RBAC"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, security, rbac]
sources:
  - url: "https://kubernetes.io/docs/reference/access-authn-authz/rbac/"
    title: "Kubernetes RBAC documentation"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/rancher/rbac.md"
---

# Kubernetes RBAC

## Overview

RBAC (Role-Based Access Control) controls who can do what on cluster
resources. Kubernetes authorizes requests by matching the requester's identity
(User, Group, or ServiceAccount) against Roles that grant verbs on resources.
It is the default authorization mode in k3s and most distributions.

## Details

### Roles vs ClusterRoles

| Object | Scope | Use case |
|---|---|---|
| Role | One namespace | Grant access within a single namespace |
| ClusterRole | Whole cluster | Cluster-scoped resources, non-resource URLs, or namespaced access everywhere |

RBAC rules are `apiGroups` + `resources` + `verbs`. Common verbs: `get`,
`list`, `watch`, `create`, `update`, `patch`, `delete`.

### RoleBindings vs ClusterRoleBindings

Bindings attach a Role/ClusterRole to subjects (Users, Groups,
ServiceAccounts):

- **RoleBinding** grants a Role in its namespace, or a ClusterRole scoped to
  that namespace.
- **ClusterRoleBinding** grants a ClusterRole cluster-wide.

Example — abstract namespace-scoped access:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: default
  name: read-pods
subjects:
  - kind: ServiceAccount
    name: deployer
    namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### ServiceAccounts

- A ServiceAccount is the identity for Pods; each namespace has a `default`
  one. Pods use it via a mounted token to call the API server.
- Create dedicated ServiceAccounts per workload and bind only the permissions
  they need (least privilege).
- Workload identity (e.g. for external services) can be tied to
  ServiceAccounts via projected tokens (TokenRequest API).

Example — abstract ServiceAccount:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: deployer
  namespace: default
automountServiceAccountToken: true
```

### Aggregated ClusterRoles

An aggregated ClusterRole combines rules from other ClusterRoles matching
labels. Adding a label to a ClusterRole automatically extends the aggregate —
useful for layered permissions without editing the aggregate itself.

Example — abstract aggregated:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
aggregationRule:
  clusterRoleSelectors:
    - matchLabels:
        rbac.example.com/aggregate-to-monitoring: "true"
rules: []
```

### Homelab notes

- k3s default user is cluster-admin; the `admin.conf` kubeconfig is
  all-powerful — keep it off shared machines.
- Rancher (if used) manages user-facing RBAC on top of k8s RBAC — see the
  linked rancher rbac note.
- Audit with `kubectl auth can-i --list` and `--as` to verify permissions
  before granting.

## Sources / Further Reading

- Kubernetes docs — RBAC: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- Kubernetes docs — ServiceAccounts: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
