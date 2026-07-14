---
title: "Role-Based Access Control (RBAC)"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - security
  - rbac
sources:
  - url: "https://kubernetes.io/docs/reference/access-authn-authz/rbac/"
    title: "Using RBAC Authorization — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# Role-Based Access Control (RBAC)

## Overview

RBAC regulates access to Kubernetes API resources based on the roles of individual users and ServiceAccounts. It uses four API objects: Role, ClusterRole, RoleBinding, and ClusterRoleBinding.

## Role vs ClusterRole

A Role grants permissions within a specific namespace. A ClusterRole grants cluster-wide permissions (cluster-scoped resources, non-resource endpoints) and can also be bound in a specific namespace via RoleBinding.

## RoleBinding vs ClusterRoleBinding

A RoleBinding grants permissions within a specific namespace. It can reference a Role (same namespace) or a ClusterRole (to reuse cluster-wide templates). A ClusterRoleBinding grants cluster-wide permissions and ignores namespaces.

## Verbs and Resources

Verbs: `get`, `list`, `watch`, `create`, `update`, `patch`, `delete`, `deletecollection`. Resources: `pods`, `services`, `deployments`, `configmaps`, `secrets`, `nodes` (cluster-scoped). Subresources use `resource/subresource` format (e.g., `pods/status`, `pods/log`). `resourceNames` restricts access to specific named instances.

## Aggregated ClusterRoles

`aggregationRule` with `clusterRoleSelectors` merges rules from ClusterRoles matching the label selectors. Useful for dynamically composing permissions — add a label to a ClusterRole and it is automatically included.

## Good Practices

Use least privilege (start deny, grant only what is needed). Prefer RoleBindings over ClusterRoleBindings. Use ServiceAccounts for application identities, not user accounts. Use `resourceNames` for fine-grained access control.

### Role + RoleBinding

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
  name: my-sa
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### ClusterRole + ClusterRoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-secrets-global
subjects:
- kind: User
  name: admin
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

## Related

- [Service Accounts](./service-accounts.md)
- [Secrets](./secrets.md)
