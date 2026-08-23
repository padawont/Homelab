---
title: "k9s — terminal Kubernetes UI"
status: accepted
author: "padawont"
date: 2026-08-23
tags: [kubernetes, k9s, tui, operations]
sources:
  - url: "https://k9scli.io/"
    title: "k9s documentation"
last_audit_date: 2026-08-23
related_docs:
  - "./05_Implementations/node-main/k9s/overview.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/kubectl.md"
---

# k9s — terminal Kubernetes UI

## Overview

k9s is a terminal UI for Kubernetes that watches the API and presents resources in a
TUI. It complements `kubectl` for quick inspection and day-2 operations: pods, nodes,
deployments, logs, describe, and shell access without leaving the terminal. It is not a
replacement for GitOps or declarative manifests — it is a read/operate view on top of
the same API `kubectl` uses.

For this homelab, k9s runs on node-main as the `runic` user, pointed at the local k3s
cluster via `/etc/rancher/k3s/k3s.yaml` (readable thanks to
`--write-kubeconfig-mode 644`).

## Details

### How it connects

- Reads a kubeconfig from `$KUBECONFIG` or `~/.kube/config`.
- No agent or daemon; direct API access. Cluster RBAC applies as usual.

### Common usage

| Task | Action |
|---|---|
| Open TUI | `KUBECONFIG=/etc/rancher/k3s/k3s.yaml k9s` |
| Switch view | `:` + resource (pods, nodes, deployments, svc, pvc…) |
| Describe | select → `d` |
| Logs | select pod → `l` |
| Exec shell | select pod → `s` |
| Delete | select → `ctrl-d` |
| Port forward | select pod → `shift-f` |
| Help | `?` |

### Key qualities

- **Fast**: watches via informers; filtered views per namespace/label.
- **Contexts**: multi-cluster via `k9s --context`; pairs with `kubectx`.
- **Read-only by default**: mutations require explicit confirm (`ctrl-d`), so mistakes
  are harder than with raw `kubectl delete`.

### Trade-offs

- Terminal-only (no web UI) — Rancher covers the browser-based ops view.
- Config/state in `~/.config/k9s` (skins, aliases, plugins) — trivially reproducible.

## Sources / Further Reading

- [k9s documentation](https://k9scli.io/)
- See `./05_Implementations/node-main/k9s/overview.md` for the homelab setup and
  `./02_Knowledge/technologies/kubernetes/concepts/kubectl.md` for the underlying CLI.
