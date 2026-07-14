---
title: "Secrets"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - configuration
  - secrets
sources:
  - url: "https://kubernetes.io/docs/concepts/configuration/secret/"
    title: "Secrets — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# Secrets

## Overview

A Secret is an API object that stores sensitive data such as passwords, OAuth tokens, SSH keys, and TLS certificates. Secrets are similar to ConfigMaps but designed for confidential data. Values are base64-encoded in the API (not encrypted by default — encryption at rest is a separate configuration).

## Secret Types

- **Opaque** (default): arbitrary key-value pairs for passwords, API keys, and tokens
- **kubernetes.io/tls**: TLS certificate and key (`tls.crt`, `tls.key`)
- **kubernetes.io/dockerconfigjson**: Docker registry credentials (`.dockerconfigjson`)
- **kubernetes.io/basic-auth**: username and password for basic authentication
- **kubernetes.io/ssh-auth**: SSH private keys (`ssh-privatekey`)
- **bootstrap.kubernetes.io/token**: bootstrap tokens for cluster join

## Data Encoding

Secret values are base64-encoded, not encrypted. Anyone with API access can decode them. For production, configure encryption at rest using `kube-apiserver --encryption-provider-config` with AES-CBC, AES-GCM, or KMS providers.

## Injection

Same patterns as ConfigMaps: environment variables via `valueFrom.secretKeyRef` and volume mounts via `secret.volumeSource`. Volume mount updates propagate when the Secret changes (with propagation delay). SubPath mounts do not auto-update.

## Immutable Secrets

Setting `immutable: true` prevents changes after creation, improving performance (no watch needed) and preventing accidental mutation. An immutable Secret must be deleted and recreated to change values.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: YWRtaW4=
  password: MWYyZDFlMmU2N2Rm
---
apiVersion: v1
kind: Secret
metadata:
  name: tls-secret
type: kubernetes.io/tls
data:
  tls.crt: <base64-cert>
  tls.key: <base64-key>
```

## References

- [Secrets — Kubernetes Documentation](https://kubernetes.io/docs/concepts/configuration/secret/)
- [ConfigMaps](./configmaps.md)
- [Service Accounts](./service-accounts.md)
- [Pods](./pods.md)
