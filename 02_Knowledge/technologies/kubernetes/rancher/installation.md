---
title: "Installing Rancher on k3s"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, rancher, installation, helm, cert-manager, tls]
sources:
  - url: "https://ranchermanager.docs.rancher.com/"
    title: "Rancher Manager documentation"
  - url: "https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/install-upgrade-on-a-kubernetes-cluster/"
    title: "Install/upgrade Rancher on a Kubernetes cluster"
  - url: "https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/installation-references/helm-chart-options"
    title: "Rancher Helm chart options"
  - url: "https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/installation-references/tls-settings"
    title: "TLS settings"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/k3s/installation.md"
---

# Installing Rancher on k3s

## Overview

The supported homelab-friendly path is Helm on an existing k3s cluster: install
cert-manager, then the `rancher` chart into `cattle-system`. Rancher needs a
stable hostname reachable by both browser and agents — for a homelab that is
usually an internal name like `rancher.local` with a self-signed or private-CA
certificate. Requirements: a working k3s cluster (see ./02_Knowledge/technologies/kubernetes/k3s/installation.md), a
DNS name, and Helm 3.

## Details

### Prerequisites

- k3s cluster with enough headroom for the Rancher control plane (about 1 CPU /
  1–2 GiB minimum for a small homelab).
- `rancher.local` (or similar) resolves to the k3s node / load balancer from
  both the browser machine and any downstream clusters that will register agents.
- Helm 3 CLI available on the admin machine.

### Step-by-step

1. Add the Rancher Helm repository and create the target namespace.
2. Install cert-manager (Rancher uses it to issue and rotate its serving cert).
3. Install the `rancher` chart with `hostname` set and `ingress.tls.source=rancher`
   so cert-manager issues a self-signed cert for the ingress.
4. Wait for the rollout, then open `https://rancher.local` and set the bootstrap
   password (default admin user, first-run screen).

Example — abstract helm bootstrap:

```bash
# 1. repo + namespace
helm repo add rancher-latest https://charts.rancher.com/server/stable
kubectl create namespace cattle-system

# 2. cert-manager (must be installed before Rancher)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.21.1/cert-manager.yaml

# 3. rancher chart
helm install rancher rancher-latest/rancher \
  --namespace cattle-system \
  --set hostname=rancher.local \
  --set bootstrapPassword=ChangeMe_Strong \
  --set ingress.tls.source=rancher \
  --set replicas=1
```

### TLS choices

| `ingress.tls.source` | Certificate source | Homelab fit |
|---|---|---|
| `rancher` (default) | cert-manager self-signed, auto-rotated | Easiest; browsers warn unless CA is trusted |
| `secret` | Bring your own TLS secret (e.g. private CA / Let's Encrypt) | Cleaner; import a Secret before install |
| `letsEncrypt` | cert-manager + Let's Encrypt HTTP-01 | Needs a publicly resolvable hostname — rare in homelab |

### Post-install checks

- `kubectl -n cattle-system rollout status deploy/rancher` completes.
- `kubectl -n cattle-system get pods` shows `rancher-*` Running and Ready.
- `https://rancher.local` shows the bootstrap screen; set a strong admin password.

### Notes

- The `bootstrapPassword` value only applies on first install.
- cert-manager must be installed **before** Rancher, or the webhook will fail.
- For a single k3s node, `replicas=1` is fine; bump to 3 only for HA.
- Keep the chart version pinned in GitOps manifests; Rancher upgrades are
  rolling and reversible via `helm rollback`.

## Sources / Further Reading

- Install/upgrade Rancher on a Kubernetes cluster: https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/install-upgrade-on-a-kubernetes-cluster/
- Rancher Helm chart options: https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/installation-references/helm-chart-options
- TLS settings: https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/installation-references/tls-settings
- Rancher Manager documentation: https://ranchermanager.docs.rancher.com/
