---
title: "Rancher Installation on k3d"
status: draft
author: padawont
date: 2026-07-11
tags:
  - rancher
  - installation
  - k3d
  - kubernetes
  - helm
  - cert-manager
  - bootstrap
sources:
  - url: "https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/install-upgrade-on-a-kubernetes-cluster"
    title: "Rancher — Installing on Kubernetes"
  - url: "https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/installation-references/helm-chart-options"
    title: "Rancher Helm Chart Options"
  - url: "https://artifacthub.io/packages/helm/rancher-stable/rancher"
    title: "Rancher Helm Chart on ArtifactHub"
  - url: "https://cert-manager.io/docs/"
    title: "cert-manager Documentation"
last_audit_date: 2026-07-11
---

# Rancher Installation on k3d

This guide walks through bootstrapping Rancher on a local k3d cluster. The result is a single-node Rancher Management Server running on your local machine, suitable for development, evaluation, and the OpenChoreo POC.

## Prerequisites

- [k3d](../k3d/cluster-lifecycle.md) — installed and functional (`k3d version`)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) — configured (`kubectl version --client`)
- [Helm](https://helm.sh/docs/intro/install/) v3 — installed (`helm version`)
- [Docker](https://docs.docker.com/engine/install/) — running (`docker ps`)
- [Kubernetes Fundamentals](../) — Helm, Ingress, and basic K8s concepts

## Step 1 — Create a k3d Cluster

Create a k3d cluster with port mappings so Rancher's ingress is reachable on the host:

```bash
k3d cluster create rancher \
  --api-port 6443 \
  --servers 1 \
  --agents 1 \
  --port "80:80@loadbalancer" \
  --port "443:443@loadbalancer"
```

Verify the cluster is ready:

```bash
k3d cluster list
kubectl cluster-info
kubectl get nodes
```

The `--port` flags map host ports 80 and 443 to the k3d load balancer, which forwards to the Rancher ingress controller.

## Step 2 — Install cert-manager

Rancher requires cert-manager to issue TLS certificates for the ingress.

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true
```

Wait for cert-manager to be ready:

```bash
kubectl -n cert-manager rollout status deploy/cert-manager --timeout=180s
```

## Step 3 — Add the Rancher Helm Repository

```bash
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo update
```

For the latest pre-stable releases (not recommended for production-like setups), use `rancher-latest` instead:

```bash
helm repo add rancher-latest https://releases.rancher.com/server-charts/latest
```

## Step 4 — Create the cattle-system Namespace

```bash
kubectl create namespace cattle-system
```

## Step 5 — Configure TLS

Rancher needs a TLS certificate for its ingress. Two options:

### Option A: Self-Signed Certificate (Recommended for Local)

Rancher generates and signs its own CA. This is the simplest option for local development.

```bash
helm install rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname=rancher.127.0.0.1.nip.io \
  --set bootstrapPassword=RancherAdmin123 \
  --set replicas=1 \
  --set ingress.tls.source=rancher
```

The hostname `rancher.127.0.0.1.nip.io` resolves to `127.0.0.1` via the [nip.io](https://nip.io/) wildcard DNS service, so the browser can reach it on localhost.

### Option B: Let's Encrypt (Public Hostname)

If you have a publicly resolvable domain pointed at your machine, use Let's Encrypt for a trusted certificate. Requires a cert-manager `ClusterIssuer` to be configured first.

```bash
helm install rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname=rancher.example.com \
  --set bootstrapPassword=RancherAdmin123 \
  --set replicas=1 \
  --set ingress.tls.source=letsEncrypt \
  --set letsEncrypt.email=admin@example.com
```

This requires that a `ClusterIssuer` named `rancher` exists in cert-manager. The cert-manager `http01` solver must be able to reach port 80 on the host from the internet.

## Step 6 — Wait for the Rancher Rollout

```bash
kubectl -n cattle-system rollout status deploy/rancher --timeout=300s
```

Verify all pods are running:

```bash
kubectl -n cattle-system get pods
```

You should see the `rancher-xxxxx-xxxxx` pod in `Running` state.

## Step 7 — Retrieve the Bootstrap Password

```bash
kubectl get secret --namespace cattle-system bootstrap-secret \
  -o jsonpath='{.data.bootstrapPassword}' | base64 -d
```

The output is the one-time bootstrap password for the first login.

## Step 8 — Log In and Set the Server URL

Open `https://rancher.127.0.0.1.nip.io` in a browser. Since the certificate is self-signed, you will need to accept the browser warning (or add the Rancher CA to your trust store).

1. Log in with username `admin` and the bootstrap password from Step 7
2. Rancher will prompt you to set a new admin password — choose a secure password
3. Set the Rancher Server URL to `https://rancher.127.0.0.1.nip.io`

After setting the server URL, Rancher will restart. Wait for the rollout to complete again (`kubectl -n cattle-system rollout status deploy/rancher`).

## Step 9 — Verify the Installation

```bash
curl -sk https://rancher.127.0.0.1.nip.io/ping
```

Expected response: `{"status":"pong"}`

Navigate the Rancher UI at `https://rancher.127.0.0.1.nip.io`. The management cluster (the k3d cluster running Rancher) should appear as `local` in the cluster list.

## References

- [Rancher — Installing on Kubernetes](https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/install-upgrade-on-a-kubernetes-cluster)
- [Rancher Helm Chart Options](https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/installation-references/helm-chart-options)
- [Rancher Helm Chart on ArtifactHub](https://artifacthub.io/packages/helm/rancher-stable/rancher)
- [cert-manager Documentation](https://cert-manager.io/docs/)
- [nip.io — Wildcard DNS for localhost](https://nip.io/)
