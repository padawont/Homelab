---
title: "Kubernetes ConfigMaps"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, configuration, configmaps]
sources:
  - url: "https://kubernetes.io/docs/concepts/configuration/configmap/"
    title: "Kubernetes ConfigMap documentation"
last_audit_date: 2026-08-22
related_docs: []
---

# Kubernetes ConfigMaps

## Overview

A ConfigMap decouples configuration from container images: non-sensitive
key/value data stored in the cluster and injected into Pods as environment
variables, command-line args, or files. Homelab manifests use ConfigMaps for
app settings, Caddy/Traefik fragments, and service defaults without rebuilding
images.

## Details

### Creation

Create from literal values, a file, or a directory of files:

```bash
kubectl create configmap app-config --from-literal=LOG_LEVEL=info
kubectl create configmap app-config --from-file=config.yaml=./config.yaml
```

Or declaratively in YAML (data must be strings; binary data goes in
`binaryData` as base64).

### Env injection

ConfigMap values become environment variables via `envFrom` (all keys) or
`valueFrom.configMapKeyRef` (a single key).

### Volume mounts

Mounting a ConfigMap as a volume creates one file per key. Updates to the
ConfigMap are reflected in mounted files (with a sync delay); env vars are
NOT updated after Pod start — restart the Pod to pick up changes.

Example — abstract:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  LOG_LEVEL: info
  config.yaml: |
    server:
      port: 8080
---
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: example/app:1.0
      envFrom:
        - configMapRef:
            name: app-config
      volumeMounts:
        - name: config
          mountPath: /etc/app
  volumes:
    - name: config
      configMap:
        name: app-config
```

### Immutability

Setting `immutable: true` on a ConfigMap prevents changes and deletion of the
data. Immutable ConfigMaps improve performance (no watch overhead) and make
deploys reproducible — flip a new ConfigMap instead of editing in place.

Example — abstract immutable:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
immutable: true
data:
  LOG_LEVEL: info
```

### Homelab notes

- Never store credentials in ConfigMaps — use Secrets for anything sensitive.
- For GitOps (Flux/ArgoCD), ConfigMaps are rendered from the repo; keep them
  declarative, not imperative.
- ConfigMap names must be DNS subdomains; max 1 MiB of data per ConfigMap.

## Sources / Further Reading

- Kubernetes docs — ConfigMap: https://kubernetes.io/docs/concepts/configuration/configmap/
- Kubernetes docs — ConfigMaps (tasks): https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/
