---
title: "Kubernetes Secrets"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, security, secrets]
sources:
  - url: "https://kubernetes.io/docs/concepts/configuration/secret/"
    title: "Kubernetes Secret documentation"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/tools/nixos/services-secrets.md"
---

# Kubernetes Secrets

## Overview

A Secret stores small amounts of sensitive data (credentials, tokens, keys)
and injects them into Pods like a ConfigMap. Secrets are the native way to
avoid baking secrets into images or manifests. Note: Secrets are only
base64-obfuscated, not encrypted, unless etcd encryption is enabled — treat
them as a secure-enough-to-use, but not bulletproof, primitive.

## Details

### Secret types

| Type | Purpose |
|---|---|
| `Opaque` (default) | Arbitrary key/value data |
| `kubernetes.io/tls` | TLS cert + key (`tls.crt`, `tls.key`) — used by Ingress |
| `kubernetes.io/dockerconfigjson` | Container registry credentials (`.dockerconfigjson`) |
| `kubernetes.io/basic-auth` | Username/password pairs |
| `kubernetes.io/ssh-auth` | SSH private keys |

### Data encoding

- `data` values must be base64-encoded strings.
- `stringData` accepts plain strings and is encoded at write time — convenient
  for readability in manifests.
- Secrets are namespaced and limited to 1 MiB.

Example — abstract:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: default
type: Opaque
stringData:
  username: admin
  password: ChangeMe123
---
apiVersion: v1
kind: Secret
metadata:
  name: my-tls
  namespace: default
type: kubernetes.io/tls
stringData:
  tls.crt: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
  tls.key: |
    -----BEGIN PRIVATE KEY-----
    ...
    -----END PRIVATE KEY-----
```

### Injection patterns

- Env vars via `envFrom` or `valueFrom.secretKeyRef` (same shape as
  ConfigMaps).
- Volume mounts: one file per key; updates propagate on rotation.
- Registry pull: reference the dockerconfigjson Secret in the Pod
  `imagePullSecrets`.
- Ingress TLS: reference the tls Secret via `spec.tls[].secretName`.

### etcd encryption

By default Secret data is stored base64-encoded in etcd — anyone with etcd
access can decode it. Enable EncryptionConfiguration (AES-CBC/GCM or KMS
provider) so Secrets are encrypted at rest. k3s supports this via the
`secrets-encryption` flag and `k3s secrets-encrypt` commands.

### Homelab notes

- For GitOps, do not commit raw Secrets. Use Sealed Secrets, the k8s SOPS
  toolchain (via sops-nix on the host) or External Secrets Operator — see the
  linked nixos services-secrets note for how the homelab stores secrets.
- Enable etcd encryption on new clusters from day one; rotating later is
  possible but more work.

## Sources / Further Reading

- Kubernetes docs — Secrets: https://kubernetes.io/docs/concepts/configuration/secret/
- Kubernetes docs — Encrypting data at rest: https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/
- k3s — Secrets encryption: https://docs.k3s.io/security/secrets-encryption
