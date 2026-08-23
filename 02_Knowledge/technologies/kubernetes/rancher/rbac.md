---
title: "Rancher RBAC"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, rancher, rbac, projects, security]
sources:
  - url: "https://ranchermanager.docs.rancher.com/"
    title: "Rancher Manager documentation"
  - url: "https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac/"
    title: "Managing RBAC in Rancher"
  - url: "https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac/cluster-and-project-roles"
    title: "Cluster and project roles"
  - url: "https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/manage-clusters/projects-and-namespaces"
    title: "Projects and namespaces"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/rbac.md"
---

# Rancher RBAC

## Overview

Rancher RBAC layers on top of native Kubernetes RBAC (see ./02_Knowledge/technologies/kubernetes/concepts/rbac.md). It
adds a human-friendly abstraction: **users/groups** (from local accounts or an
external IdP), **roles** (bundles of Kubernetes rules), and **scopes** (global,
cluster, project). Assignments translate automatically into RoleBindings /
ClusterRoleBindings on the target cluster, so the UI and kubectl agree on who
can do what.

## Details

### Identity: users and groups

- **Local auth**: users created in Rancher's internal database; simplest for a
  single-admin homelab.
- **External auth**: LDAP, Active Directory, GitHub, Keycloak/OIDC, SAML — users
  and groups come from the IdP and cannot be created locally.
- Groups let you grant a role once (e.g. `family`) and manage membership in the
  IdP instead of per-user in Rancher.

### RoleTemplates

A RoleTemplate is Rancher's named role definition — a set of Kubernetes rules
plus metadata. Built-ins include `Cluster Owner`, `Cluster Member`,
`Project Owner`, `Project Member`, and `Read-Only`. Custom RoleTemplates can be
created from the UI and are stored as CRDs on the management cluster.

Example — abstract custom cluster role granting read access to pods and nodes:

```yaml
apiVersion: management.cattle.io/v3
kind: RoleTemplate
metadata:
  name: cluster-pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods", "nodes"]
    verbs: ["get", "list", "watch"]
```

### Scopes and built-in roles

| Scope | Built-in roles | What they can do |
|---|---|---|
| Global | Administrator, Standard User | Manage clusters/users/settings (admin); use assigned clusters (standard) |
| Cluster | Cluster Owner, Cluster Member, Read-Only | Manage cluster resources; view cluster; read-only access |
| Project | Project Owner, Project Member, Read-Only | Manage project namespaces/workloads; deploy workloads; read-only |

### Projects and namespace scoping

A **Project** is a Rancher grouping of one or more namespaces within a single
cluster. Project roles apply to every namespace in the project. Typical homelab
pattern: one project per "tenant" (e.g. `media`, `infra`, `apps`), with a
Project Member who can deploy only into those namespaces.

- Project members never see cluster-scoped resources.
- Project resource quotas map to Kubernetes ResourceQuotas per namespace.
- Moving a namespace between projects re-creates its RoleBindings — do it rarely.

### Kubernetes RBAC integration

- Rancher does not replace Kubernetes RBAC; it generates it.
- Assigning a Cluster role creates a ClusterRoleBinding on the downstream
  cluster; Project roles create RoleBindings in each project namespace.
- The **authentication proxy** validates the Rancher session and impersonates
  the mapped identity, so kubectl requests go through the same RBAC.
- Existing hand-written RoleBindings on imported clusters remain valid and
  coexist with Rancher-managed ones — do not edit Rancher-created bindings
  (they are reconciled back).

### Homelab guidance

- Start with local auth + one Administrator; add Standard Users only when needed.
- Prefer group-based grants if you later connect an IdP (Keycloak) — less churn.
- Use Read-Only roles for "guest" access to show the dashboard without risk.
- Never grant `cluster-admin` via a custom RoleTemplate unless intentional.

## Sources / Further Reading

- Managing RBAC in Rancher: https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac/
- Cluster and project roles: https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac/cluster-and-project-roles
- Projects and namespaces: https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/manage-clusters/projects-and-namespaces
- Rancher Manager documentation: https://ranchermanager.docs.rancher.com/
