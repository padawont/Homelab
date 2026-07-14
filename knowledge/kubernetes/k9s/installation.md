---
title: "k9s Installation"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k9s
  - kubernetes
  - tooling
  - installation
  - rbac
sources:
  - url: "https://k9scli.io/topics/install"
    title: "k9s — Installation"
  - url: "https://github.com/derailed/k9s#readme"
    title: "k9s GitHub README"
  - url: "https://k9scli.io/topics/config"
    title: "k9s — Configuration"
  - url: "https://k9scli.io/topics/rbac"
    title: "k9s — RBAC"
last_audit_date: 2026-07-10
---

# k9s Installation

Install [k9s](https://k9scli.io/) — a terminal-based Kubernetes cluster UI. k9s is available on Linux, macOS, and Windows. Build artifacts are distributed via the [GitHub releases page](https://github.com/derailed/k9s/releases).

## Prerequisites

- **kubectl** installed and configured with a valid KubeConfig
- **KUBECONFIG** environment variable pointing to the correct config file (k9s reads the same kubeconfig as kubectl)
- **KUBE_EDITOR** or **EDITOR** environment variable set for edit commands (`export KUBE_EDITOR=vim` or `export EDITOR=code --wait`)
- **TERM** set to `xterm-256color` for full color support: `export TERM=xterm-256color`

Source: [k9s Install — PreFlight Check](https://k9scli.io/topics/install)

## macOS

### Homebrew (tap)
```bash
brew install derailed/k9s/k9s
```
The official tap maintained by the k9s project.

### MacPorts
```bash
sudo port install k9s
```

Source: [k9s Install — macOS](https://k9scli.io/topics/install)

## Linux

### Homebrew (Linuxbrew)
```bash
brew install derailed/k9s/k9s
```

### PacMan (Arch Linux)
```bash
pacman -S k9s
```

### Install Script (curl)
```bash
curl -sS https://webinstall.dev/k9s | bash
```

Source: [k9s Install — Linux](https://k9scli.io/topics/install)

## Windows

### Scoop
```bash
scoop install k9s
```

### Chocolatey
```bash
choco install k9s
```

Source: [k9s Install — Windows](https://k9scli.io/topics/install)

## Other Methods

### GitHub Release Binary
Download the latest tarball for your platform from the [GitHub releases page](https://github.com/derailed/k9s/releases), extract it, and place the binary in your `PATH`.

### Go Install
```bash
go install github.com/derailed/k9s@latest
```
Installs from source. Requires Go 1.14+.

### Krew (kubectl plugin)
```bash
kubectl krew install k9s
```
Then launch via `kubectl k9s` or directly as `k9s`.

### Build from Source
```bash
git clone https://github.com/derailed/k9s.git
cd k9s
make build && ./execs/k9s
```
Requires Go 1.14+.

Source: [k9s Install — Building From Source](https://k9scli.io/topics/install)

## Verify Installation

```bash
k9s info
```
Displays runtime information: config directory, log location, KubeConfig path, and active context. Use this to confirm k9s sees your cluster correctly.

```bash
k9s version
```
Shows the installed k9s version.

Source: [k9s Install — PreFlight Check](https://k9scli.io/topics/install)

## Configuration Directory

k9s follows XDG Base Directory conventions. Default locations:

| OS | Config Path |
|---|---|
| Unix/Linux | `~/.config/k9s` |
| macOS | `~/Library/Application Support/k9s` |
| Windows | `%LOCALAPPDATA%\k9s` |

Override with `K9S_CONFIG_DIR` environment variable. Use `k9s info` to see which directory is active.

Source: [k9s Config — Overview](https://k9scli.io/topics/config)

## RBAC Setup

On clusters with RBAC enabled, users need explicit permissions to browse resources in k9s. Without these, views appear blank with `Forbidden` errors.

### ClusterRole (cluster-wide read access)

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: k9s
rules:
  # Nodes, namespaces, persistent volumes
  - apiGroups: [""]
    resources: ["nodes", "namespaces", "persistentvolumes"]
    verbs: ["get", "list", "watch"]
  # RBAC resources
  - apiGroups: ["rbac.authorization.k8s.io"]
    resources: ["clusterroles", "roles", "clusterrolebindings", "rolebindings"]
    verbs: ["get", "list", "watch"]
  # Custom Resource Definitions
  - apiGroups: ["apiextensions.k8s.io"]
    resources: ["customresourcedefinitions"]
    verbs: ["get", "list", "watch"]
  # Metrics (if metrics-server is installed)
  - apiGroups: ["metrics.k8s.io"]
    resources: ["nodes", "pods"]
    verbs: ["get", "list", "watch"]
```

### ClusterRoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: k9s
subjects:
  - kind: User
    name: <username>
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: k9s
  apiGroup: rbac.authorization.k8s.io
```

### Namespaced Role (for namespace-scoped users)

```yaml
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: k9s
  namespace: default
rules:
  - apiGroups: ["", "apps", "autoscaling", "batch", "extensions"]
    resources: ["*"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["metrics.k8s.io"]
    resources: ["pods", "nodes"]
    verbs: ["get", "list", "watch"]
```

### RoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: k9s
  namespace: default
subjects:
  - kind: User
    name: <username>
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: k9s
  apiGroup: rbac.authorization.k8s.io
```

Source: [k9s RBAC page](https://k9scli.io/topics/rbac)
