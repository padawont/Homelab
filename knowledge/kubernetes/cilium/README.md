# Cilium

Reference notes on [Cilium](https://cilium.io/) — an eBPF-based Container Network Interface (CNI) and network security solution for Kubernetes, providing high-performance networking, observability via Hubble, and identity-aware security policies.

Prerequisites: [Kubernetes](../) fundamentals — understand [Pods](../pods.md), [Services](../services.md), and [NetworkPolicy](../network-policies.md) concepts. See also [k3d](../k3d/) for cluster lifecycle and configuration.

## Getting Started

| File | Description |
|---|---|
| [installation.md](installation.md) | Install Cilium on k3d/k3s via CLI or Helm, kernel requirements, `cilium status` validation |

## Network Security

| File | Description |
|---|---|
| [network-policies.md](network-policies.md) | `CiliumNetworkPolicy` and `CiliumClusterwideNetworkPolicy` CRDs, L3/L4/L7 rules, deny policies |

## Observability

| File | Description |
|---|---|
| [hubble.md](hubble.md) | Hubble CLI, Hubble Relay, Hubble UI / Service Map, flow filtering |

## Operations

| File | Description |
|---|---|
| [troubleshooting.md](troubleshooting.md) | `cilium connectivity test`, `cilium sysdump`, `cilium-dbg` commands, common failure modes |

## Reference

| File | Description |
|---|---|
| [ebpf-basics.md](ebpf-basics.md) | BPF hook points (XDP, TC, cgroup), eBPF maps, datapath modes, kernel config flags, BTF requirements |
