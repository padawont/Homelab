---
title: "ServiceAccounts"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - security
  - service-accounts
sources:
  - url: "https://kubernetes.io/docs/concepts/security/service-accounts/"
    title: "Service Accounts — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# ServiceAccounts

## Overview
A ServiceAccount is an identity for processes running in a pod. Unlike user accounts (which are for humans), ServiceAccounts are Kubernetes resources that authenticate to the API server using tokens. Every namespace gets a default ServiceAccount.

## ServiceAccount vs User
Users are global, managed externally (OIDC, client certificates, static tokens). ServiceAccounts are namespace-scoped Kubernetes resources, managed through the API, with automatic token management.

## Default ServiceAccount
Each namespace has a `default` ServiceAccount. If a pod does not specify `serviceAccountName`, it uses the default. The default SA has no RBAC permissions beyond what is granted to unauthenticated users.

## automountServiceAccountToken
`automountServiceAccountToken: false` on a pod spec or ServiceAccount prevents the token from being mounted. Recommended for pods that do not need API access (reduces attack surface).

## TokenRequest API
The modern way to obtain a token. `kubectl create token <sa-name>` creates a time-bound, audience-scoped token. The TokenRequest API does not create a Secret — the token is ephemeral and rotates automatically.

## Projected Volumes for Tokens
The recommended way to mount a token into a pod is via a projected volume with `serviceAccountToken` source, specifying `path`, `audience`, and `expirationSeconds`. This replaces legacy token Secret mounting.

## Pod Spec
Set `spec.serviceAccountName: my-sa` in the pod spec to use a specific ServiceAccount.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
automountServiceAccountToken: false
```

Projected volume token example:
```yaml
spec:
  serviceAccountName: my-app-sa
  containers:
  - name: my-app
    image: my-app:latest
    volumeMounts:
    - mountPath: /var/run/secrets/tokens
      name: token
  volumes:
  - name: token
    projected:
      sources:
      - serviceAccountToken:
          path: token
          audience: api
          expirationSeconds: 3600
```

Cross-links: [Pods](./pods.md) | [RBAC](./rbac.md) | [Secrets](./secrets.md)
