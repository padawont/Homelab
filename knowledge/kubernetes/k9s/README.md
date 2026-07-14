# k9s

Reference notes on [k9s](https://k9scli.io/) — a terminal-based Kubernetes cluster UI (TUI) for navigating, observing, and debugging clusters efficiently. k9s continually watches Kubernetes for changes and provides keyboard-driven commands to interact with observed resources.

Prerequisites: [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl) and a Kubernetes cluster with [RBAC](../rbac.md) configured. See the [Kubernetes notes](../) for prerequisite concepts (Pods, Services, Deployments, namespaces, contexts).

## Getting Started

| File | Description |
|---|---|
| [installation.md](installation.md) | Install k9s via Homebrew, curl, krew, go install; configure KUBECONFIG, EDITOR, TERM; set up RBAC permissions |
| [usage-basics.md](usage-basics.md) | CLI arguments, keyboard shortcuts, resource filtering, namespace/context switching, XRay and Pulses views |

## Debugging & Workflows

| File | Description |
|---|---|
| [debugging-workflows.md](debugging-workflows.md) | Tail logs, exec into pods, port-forward, node shell, error drill-down, benchmarking HTTP endpoints |

## Customization

| File | Description |
|---|---|
| [plugins.md](plugins.md) | Define custom commands via plugins.yaml, env variables, context-specific plugins |
| [skins-themes.md](skins-themes.md) | Skins/themes, color customization, custom column views with JSON parse expressions |
