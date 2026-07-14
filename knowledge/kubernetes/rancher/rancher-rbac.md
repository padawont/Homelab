---
title: "Rancher RBAC"
status: draft
author: padawont
date: 2026-07-11
tags:
  - rancher
  - rbac
  - security
  - kubernetes
  - projects
sources:
  - url: "https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac"
    title: "Rancher — RBAC"
  - url: "https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac/cluster-and-project-roles"
    title: "Rancher — Cluster and Project Roles"
  - url: "https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac/global-permissions"
    title: "Rancher — Global Permissions"
last_audit_date: 2026-07-11
---

# Rancher RBAC

## Prerequisites

- [Rancher instance](../rancher-install-k3d.md) — running and accessible
- [Kubernetes Fundamentals](../) — basic K8s concepts (Pods, Services, RBAC)
- [Kubernetes RBAC](../rbac.md) — Roles, ClusterRoles, RoleBindings, ClusterRoleBindings
- [Rancher Architecture](../rancher-architecture.md) — understanding of management vs downstream clusters

## Overview

Rancher RBAC extends Kubernetes RBAC with three additional layers: Global Roles (cross-cluster), RoleTemplates (reusable per-cluster or per-project roles), and Projects (grouping of Namespaces). Permissions are evaluated from most specific to least specific — the highest privilege wins.

## Users and Authentication

Rancher supports multiple authentication backends:

| Provider | Setup Notes |
|---|---|
| **Local** | Built-in, always available. Use for bootstrap and break-glass access |
| **OIDC** | Keycloak, Okta, Dex, Google Workspace — Rancher acts as an OIDC Relying Party |
| **LDAP / Active Directory** | OpenLDAP, FreeIPA, Microsoft AD — direct bind or search-and-bind |
| **SAML** | Okta, OneLogin, ADFS — IdP-initiated and SP-initiated flows |
| **GitHub** | Org/team membership mapped to Rancher groups |

Authentication is handled by the Rancher API Server before proxying requests to downstream clusters. Users never authenticate directly to downstream clusters — all traffic flows through Rancher's auth proxy.

## Global Roles

Global Roles apply across **all clusters** managed by this Rancher installation. They are defined by the `globalrole` CRD.

| Built-in Global Role | Privileges |
|---|---|
| **Administrator** | Full admin access — manage clusters, projects, users, settings, roles |
| **Standard User** | Create clusters, manage own projects, use assigned clusters |
| **User Base** | Minimum role — can log in and view assigned resources only |

Custom Global Roles can be created to grant specific permissions (e.g., "View all clusters but cannot modify"). These are defined as `GlobalRole` YAML resources:

```yaml
apiVersion: management.cattle.io/v3
kind: GlobalRole
metadata:
  name: custom-cluster-viewer
rules:
  - apiGroups: ["management.cattle.io"]
    resources: ["clusters"]
    verbs: ["get", "list", "watch"]
```

## RoleTemplates

RoleTemplates are reusable role definitions that can be applied at the **cluster** or **project** level. They are defined by the `roletemplate` CRD.

Built-in RoleTemplates include:

| RoleTemplate | Scope | Privileges |
|---|---|---|
| **Cluster Owner** | Cluster | Full control over the cluster and its projects |
| **Cluster Member** | Cluster | View cluster, manage assigned projects |
| **Project Owner** | Project | Full control over the project's Namespaces and resources |
| **Project Member** | Project | View and manage workloads in the project's Namespaces |

You can create custom RoleTemplates by defining rules in the same format as K8s RBAC rules:

```yaml
apiVersion: management.cattle.io/v3
kind: RoleTemplate
metadata:
  name: custom-pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
roleTemplateNames:
  - "project-member"
```

The `roleTemplateNames` field enables inheritance — a custom template can build on an existing one.

## Cluster Roles

When a RoleTemplate is assigned to a user on a cluster, Rancher creates a corresponding K8s `ClusterRole` and `ClusterRoleBinding` in the downstream cluster. This is the mechanism by which Rancher RBAC maps to actual K8s RBAC on managed clusters.

## Projects

A Project is a Rancher abstraction that groups one or more Kubernetes Namespaces into a logical unit. Use cases:

- Team isolation — each team gets a Project with its own set of Namespaces
- Resource quotas — set CPU/memory limits at the Project level that apply to all Namespaces inside it
- Network policy — default deny-all or allow-all rules scoped to Project members
- RBAC boundaries — grant "Project Owner" or "Project Member" access scoped to the Project

Projects are defined by the `project` CRD:

```yaml
apiVersion: management.cattle.io/v3
kind: Project
metadata:
  name: team-alpha
  namespace: fleet-default
spec:
  displayName: Team Alpha
  clusterName: downstream-cluster-1
  resourceQuota:
    limit:
      limitsCpu: "10"
      limitsMemory: 20Gi
  namespaceDefaultResourceQuota:
    limit:
      limitsCpu: "2"
      limitsMemory: 4Gi
```

## Project-Scoped RBAC

When a user is granted a role on a Project, Rancher creates:

1. A K8s `Role` in each Namespace belonging to the Project
2. A K8s `RoleBinding` binding the user (or group) to that Role

This means Project permissions are enforced by the downstream cluster's native K8s RBAC, not by Rancher itself. If you remove the Namespace from the Project, the Role and RoleBinding are automatically cleaned up.

## RBAC Evaluation Order

Rancher evaluates permissions from most specific to least specific:

1. **Project role** — highest specificity, wins over everything
2. **Cluster role** — applies across all Namespaces in the cluster
3. **Global role** — applies across all clusters

If a user has both "Cluster Owner" (full cluster access) and "Project Member" (limited access on a specific project), the Cluster Owner role grants the broader privileges because it is evaluated separately — there is no deny override.

## Best Practices

- Use Projects for team isolation rather than individual Namespace assignments
- Define custom RoleTemplates instead of assigning raw K8s ClusterRoles
- Prefer OIDC auth with group mapping over local users for teams
- Audit RBAC regularly using `rancher-user-monitoring` or the Permissions report in the UI
- Grant the minimum necessary Global Role — most users should be "Standard User" with cluster/project roles assigned individually

## References

- [Rancher RBAC](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac)
- [Rancher Cluster and Project Roles](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac/cluster-and-project-roles)
- [Kubernetes RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
