---
title: "kubectl Essentials"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, kubectl, cli]
sources:
  - url: "https://kubernetes.io/docs/reference/kubectl/"
    title: "kubectl reference documentation"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/k3s/operations.md"
---

# kubectl Essentials

## Overview

`kubectl` is the command-line client for the Kubernetes API. It is the primary
day-to-day tool for inspecting and changing cluster state in the homelab
(forgejo, traefik, longhorn, etc.). k3s also ships `k3s kubectl`, which wraps
the same binary with an auto-loaded kubeconfig.

## Details

### Common commands

| Command | Purpose |
|---|---|
| `kubectl get <res>` | List resources (`-A` all namespaces, `-w` watch) |
| `kubectl describe <res> <name>` | Detailed status and events |
| `kubectl apply -f <file>` | Create/update declaratively from YAML |
| `kubectl delete <res> <name>` | Remove a resource |
| `kubectl logs <pod> [-c <container>]` | Container logs (`-f` follow) |
| `kubectl exec -it <pod> -- <cmd>` | Run a command in a running container |
| `kubectl port-forward <pod|svc> <local>:<remote>` | Tunnel a port to a resource |

Common output flags: `-o wide` (extra fields), `-o yaml` (full manifest),
`--show-labels`, `-l app=web` (label selector).

### Contexts

A context bundles a cluster, user, and namespace. Commands run against the
current context:

```bash
kubectl config get-contexts
kubectl config use-context <name>
kubectl config current-context
kubectl config set-context --current --namespace=forgejo
```

### Namespaces

Namespaces partition a cluster (e.g. `forgejo`, `monitoring`). Apply a
namespace per command with `-n <ns>` or `--all-namespaces`/`-A` for cluster
-wide operations. The namespace in the current context is the default target.

### kubeconfig

- The kubeconfig file (`~/.kube/config` by default, or `KUBECONFIG` env var
  pointing at several merged files) holds clusters, users, and contexts.
- k3s writes `/etc/rancher/k3s/k3s.yaml` — copy it to the admin machine and
  adjust the server address for remote access.
- Merge configs with `kubectl config view --flatten`; prefer short-lived
  tokens/ServiceAccounts over copying the full admin kubeconfig.

Example — real command flow:

```bash
kubectl get pods -n forgejo
kubectl describe ingress forgejo-ingress -n forgejo
kubectl logs -f deploy/forgejo -n forgejo
kubectl exec -it deploy/forgejo -n forgejo -- /bin/sh
kubectl port-forward svc/forgejo-http 3000:3000 -n forgejo
```

### Homelab notes

- Shell completion (`kubectl completion bash` + `kubectl krew` plugins) makes
  long sessions faster.
- Prefer `kubectl apply` (declarative) over `kubectl create/edit` so the repo
  stays the source of truth.
- For k3s-specific operations (certs, secrets-encrypt), see the linked k3s
  operations note.

## Sources / Further Reading

- Kubernetes docs — kubectl reference: https://kubernetes.io/docs/reference/kubectl/
- Kubernetes docs — kubectl Quick Reference: https://kubernetes.io/docs/reference/kubectl/quick-reference/
- k3s — CLI Tools: https://docs.k3s.io/cli
