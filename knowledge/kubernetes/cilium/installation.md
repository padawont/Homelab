---
title: "Cilium Installation"
status: draft
author: padawont
date: 2026-07-11
tags:
  - cilium
  - installation
  - k3d
  - k3s
  - kubernetes
  - ebpf
sources:
  - url: "https://docs.cilium.io/en/stable/overview/intro/"
    title: "Introduction to Cilium & Hubble"
  - url: "https://docs.cilium.io/en/stable/operations/system_requirements/"
    title: "Cilium System Requirements"
  - url: "https://docs.cilium.io/en/stable/installation/k3s/"
    title: "Installation Using K3s"
  - url: "https://docs.cilium.io/en/stable/installation/kind/"
    title: "Installation Using Kind"
  - url: "https://docs.cilium.io/en/stable/network/kubernetes/kubeproxy-free/"
    title: "Kubernetes Without kube-proxy"
  - url: "https://docs.cilium.io/en/stable/installation/k8s-install-helm/"
    title: "Installation using Helm"
  - url: "https://docs.cilium.io/en/stable/gettingstarted/k8s-install-default/"
    title: "Cilium Quick Installation"
  - url: "https://github.com/cilium/cilium-cli"
    title: "Cilium CLI — GitHub"
  - url: "https://docs.cilium.io/en/stable/helm-reference/"
    title: "Helm Reference"
  - url: "https://docs.cilium.io/en/stable/internals/cilium_operator/"
    title: "Cilium Operator"
last_audit_date: 2026-07-11
---

# Cilium Installation

This note covers installing Cilium on k3d and k3s clusters and validating the installation. The target environment is a k3d cluster using k3s as the Kubernetes distribution.

See the [Kubernetes](../) notes for prerequisite [Pod](../pods.md), [Service](../services.md), and [NetworkPolicy](../network-policies.md) concepts. See [k3d notes](../k3d/) for cluster lifecycle and configuration details.

## What Cilium Is

Cilium is an eBPF-based CNI plugin that provides:

- **High-performance networking** — pod-to-pod connectivity, service load-balancing, and network policy enforcement entirely in kernel-space eBPF, bypassing iptables
- **kube-proxy replacement** — Cilium can fully replace kube-proxy using eBPF socket-level load-balancing, eliminating a separate component and improving performance
- **Identity-based security** — instead of IP addresses, Cilium assigns a security identity to each pod based on its Kubernetes labels, and enforces policy on these identities. This means policies survive pod restarts and IP changes

### How It Replaces kube-proxy

In a standard Kubernetes cluster, `kube-proxy` implements Service ClusterIP/NodePort/LoadBalancer via iptables or IPVS. Cilium replaces this by attaching eBPF programs at the cgroup socket layer (`BPF_PROG_TYPE_CGROUP_SOCK_ADDR`) that intercept `connect()`, `sendmsg()`, and `recvmsg()` syscalls. The service backend is selected before the packet leaves the socket, eliminating the need for intermediate NAT hops.

When `kubeProxyReplacement=true`, Cilium handles:
- ClusterIP, NodePort, LoadBalancer, externalIPs
- HostPort (replaces `portmap` CNI plugin)
- Session affinity
- Graceful termination

## Kernel Requirements

Before installing Cilium, verify the host system meets these requirements.

### Base Requirements

Cilium requires Linux kernel >= 5.10 (or >= 4.18 on RHEL 8.10). The following kernel config options must be enabled (typical in distribution kernels):

```
CONFIG_BPF=y
CONFIG_BPF_EVENTS=y
CONFIG_BPF_SYSCALL=y
CONFIG_NET_CLS_BPF=y
CONFIG_BPF_JIT=y
CONFIG_NET_CLS_ACT=y
CONFIG_NET_SCH_INGRESS=y
CONFIG_DEBUG_INFO_BTF=y
CONFIG_CRYPTO_SHA1=y
CONFIG_CRYPTO_USER_API_HASH=y
CONFIG_CGROUPS=y
CONFIG_CGROUP_BPF=y
CONFIG_PERF_EVENTS=y
CONFIG_SCHEDSTATS=y
```

### Tunneling Requirements

Cilium uses VXLAN tunneling by default for cross-node pod communication:

```
CONFIG_VXLAN=y
CONFIG_GENEVE=y
CONFIG_FIB_RULES=y
```

### cgroup v2

Cilium requires the cgroup v2 filesystem for socket-level load-balancing and BPF cgroup program attachment. Verify with:

```bash
# Check if cgroup v2 is mounted
mount | grep cgroup2

# If not mounted, mount it:
mount -t cgroup2 none /sys/fs/cgroup
```

Most modern distributions (Ubuntu ≥20.04, Fedora, Arch) use cgroup v2 by default. For k3d, cgroup v2 is typically available inside Docker containers running recent kernels.

### BPF Filesystem

The BPF filesystem must be mounted at `/sys/fs/bpf`. Cilium auto-mounts it if not present, but you can pre-mount:

```bash
mount bpffs /sys/fs/bpf -t bpf
```

For persistent mounting, add to `/etc/fstab`:
```
bpffs  /sys/fs/bpf  bpf  defaults  0 0
```

### Architecture Support

Cilium supports AMD64 and AArch64 architectures.

## Install cilium-cli

The Cilium CLI is the recommended tool for installing and managing Cilium:

```bash
CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
CLI_ARCH=amd64
if [ "$(uname -m)" = "aarch64" ]; then CLI_ARCH=arm64; fi
curl -L --fail --remote-name-all https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
sha256sum --check cilium-linux-${CLI_ARCH}.tar.gz.sha256sum
sudo tar xzvfC cilium-linux-${CLI_ARCH}.tar.gz /usr/local/bin
rm cilium-linux-${CLI_ARCH}.tar.gz{,.sha256sum}
```

Verify the installation:

```bash
cilium version
```

## Create a k3d Cluster

Create a k3d cluster with the default CNI (Flannel) and network policy controller disabled, since Cilium will provide both:

```bash
k3d cluster create cilium-demo \
  --k3s-arg "--flannel-backend=none@server:*" \
  --k3s-arg "--disable-network-policy@server:*" \
  --k3s-arg "--disable=servicelb@server:*" \
  --agents 2
```

Flag explanations:
- `--flannel-backend=none` — disables the default Flannel CNI so Cilium can install its own CNI chain
- `--disable-network-policy` — disables k3s' built-in network policy controller (Cilium provides its own via CRDs)
- `--disable=servicelb` — disables k3s' built-in Service LB (klipper) when using Cilium's kube-proxy replacement

The nodes will remain in `NotReady` state until Cilium is installed. This is expected.

## Install Cilium via CLI (Recommended for k3d/k3s)

Cilium uses the Helm chart internally when installed via the CLI. The key difference for k3s is that it uses pod CIDR `10.42.0.0/16`:

```bash
cilium install --version 1.19.5 \
  --set=ipam.operator.clusterPoolIPv4PodCIDRList="10.42.0.0/16"
```

> The `clusterPoolIPv4PodCIDRList` must match the k3s default pod CIDR (`10.42.0.0/16`). Without this override, Cilium will use its own default CIDR which will conflict with k3s' node pod CIDR allocation.

## Install Cilium via Helm (Alternative)

If you prefer Helm-based installation:

```bash
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium --version 1.19.5 \
  --namespace kube-system \
  --set image.pullPolicy=IfNotPresent \
  --set ipam.mode=kubernetes
```

For kube-proxy replacement:

```bash
API_SERVER_IP=$(kubectl get ep kubernetes -o jsonpath='{$.subsets[0].addresses[0].ip}')
API_SERVER_PORT=6443

helm install cilium cilium/cilium --version 1.19.5 \
  --namespace kube-system \
  --set kubeProxyReplacement=true \
  --set k8sServiceHost=${API_SERVER_IP} \
  --set k8sServicePort=${API_SERVER_PORT}
```

## Validate the Installation

### Pod Status

Check that all Cilium pods are running:

```bash
kubectl -n kube-system get pods -l k8s-app=cilium
kubectl -n kube-system get pods -l name=cilium-operator
```

Expected output: all pods in `Running` state.

### Cilium Status

```bash
cilium status --wait
```

Expected output:
```
    /¯¯\
 /¯¯\__/¯¯\    Cilium:         OK
 \__/¯¯\__/    Operator:       OK
 /¯¯\__/¯¯\    Hubble:         disabled
 \__/¯¯\__/    ClusterMesh:    disabled
    \__/

DaemonSet         cilium             Desired: 2, Ready: 2/2, Available: 2/2
Deployment        cilium-operator    Desired: 2, Ready: 2/2, Available: 2/2
```

### Node Readiness

```bash
kubectl get nodes
```

All nodes should now show `Ready` after Cilium networking is operational.

## Resource Overhead

In a 3-node k3d cluster, the Cilium components consume:

| Component | Approximate Memory | CPU |
|---|---|---|
| Cilium agent (per node) | 50-100 MB | 0.1-0.3 cores idle |
| Cilium operator | ~50 MB | ~0.1 cores |
| [Hubble](hubble.md) (if enabled, per node) | ~20-50 MB | Minimal |

These numbers scale with the number of pods, endpoints, and network policies. The operator runs as a Deployment (typically 1-2 replicas), while the Cilium agent runs as a DaemonSet on every node.

## Upgrading Cilium

### Via Helm

When upgrading from one minor release to another (e.g., 1.19.x to 1.20.x), do NOT use `--reuse-values` — it ignores newly introduced chart values and may cause rendering errors:

```bash
# ✗ BAD — do NOT use --reuse-values for minor version upgrades:
helm upgrade cilium cilium/cilium --version 1.20.0 \
  --namespace kube-system \
  --reuse-values
```

```bash
# ✓ GOOD — omit --reuse-values for minor version upgrades:
helm upgrade cilium cilium/cilium --version 1.20.0 \
  --namespace kube-system
```

Cilium supports rolling upgrades. The agent pods will restart one by one. During the upgrade, existing connections may be briefly interrupted but will be re-established.

### Pre-flight Check

Before upgrading to a new minor version, deploy the pre-flight check to validate that the new version's CRDs and configuration are compatible:

```bash
helm template cilium cilium/cilium --version 1.20.0 \
  --namespace kube-system \
  --set preflight.enabled=true \
  --set agent=false \
  --set operator.enabled=false > cilium-preflight.yaml

kubectl create -f cilium-preflight.yaml

# Wait for pre-flight DaemonSet to become ready
kubectl -n kube-system rollout status ds/cilium-preflight

# Remove pre-flight check
kubectl delete -f cilium-preflight.yaml
```

The pre-flight check deploys a validation-only DaemonSet that pre-pulls images and validates CiliumNetworkPolicy compatibility without replacing the running agents.
