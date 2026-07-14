---
title: "Cilium eBPF Fundamentals"
status: draft
author: padawont
date: 2026-07-11
tags:
  - cilium
  - ebpf
  - kernel
  - networking
  - kubernetes
sources:
  - url: "https://docs.cilium.io/en/stable/internals/hooks/"
    title: "eBPF Program Types"
  - url: "https://docs.cilium.io/en/stable/network/ebpf/"
    title: "eBPF Datapath"
  - url: "https://docs.cilium.io/en/stable/network/ebpf/maps/"
    title: "eBPF Maps"
  - url: "https://docs.cilium.io/en/stable/operations/system_requirements/"
    title: "System Requirements (kernel config)"
  - url: "https://docs.cilium.io/en/stable/reference-guides/bpf/"
    title: "BPF and XDP Reference Guide"
last_audit_date: 2026-07-11
---

# Cilium eBPF Fundamentals

This note covers the eBPF fundamentals that underpin Cilium's datapath. It describes the BPF program types Cilium uses, the maps it manages, datapath modes, and kernel configuration requirements.

## BPF Program Types Used by Cilium

Cilium attaches eBPF programs at three hook points in the Linux kernel:

### XDP (BPF_PROG_TYPE_XDP)

- **Hook:** Earliest possible point, runs in the network driver before the kernel networking stack
- **Used for:** NodePort XDP acceleration, DSR (Direct Server Return), load-balancer traffic steering
- **Benefit:** Highest performance — packets processed before SKB allocation, minimal overhead
- **Requires:** Driver support (ena, mlx5, i40e, bnxt, etc.) and kernel ≥ 5.10

```bash
# Check if XDP is enabled
kubectl -n kube-system exec ds/cilium -- cilium-dbg status --verbose | grep XDP
```

Expected: `XDP Acceleration: Native` (if enabled and supported) or `Disabled`.

### TC (BPF_PROG_TYPE_SCHED_ACT)

- **Hook:** Traffic Control (TC) ingress/egress — runs after the kernel networking stack classifies the packet
- **Used for:** Pod networking (veth pair egress/ingress), VXLAN/Geneve encapsulation/decapsulation, network policy enforcement (L3/L4 allow/deny), service load-balancing (non-accelerated path)
- **Benefit:** Most versatile — works on any interface type, no special driver required
- **Note:** This is the default datapath for pod-to-pod traffic. Every pod's veth pair has TC BPF programs attached

The TC hook handles:
- Packet filtering based on security identity
- VXLAN/Geneve tunnel encapsulation for cross-node traffic
- Policy map lookups for L3/L4 enforcement
- Connection tracking updates

### cgroup Socket Address (BPF_PROG_TYPE_CGROUP_SOCK_ADDR)

- **Hook:** cgroup v2 socket layer — intercepts `connect()`, `sendmsg()`, `recvmsg()`, `bind()` system calls
- **Used for:** kube-proxy replacement (socket-level load-balancing), host firewall
- **Benefit:** Service backend selected before packet leaves the socket — no intermediate NAT or iptables traversal

When kube-proxy replacement is enabled, this program type intercepts `connect()` calls to ClusterIP addresses and redirects them directly to a backend pod IP, bypassing iptables entirely.

## eBPF Maps

Cilium uses several kernel eBPF maps to share state between BPF programs and the userspace agent:

| Map Name | Purpose |
|---|---|
| `cilium_ct4` / `cilium_ct6` | Connection tracking entries for IPv4/IPv6 |
| `cilium_policy_v2` | Per-endpoint security policy maps |
| `cilium_lb*` | Service load-balancer backend tables (services, backends, reverse NAT) |
| `cilium_ipcache` | IP-to-security-identity mappings |
| `cilium_metrics` | Drop/forward counters per endpoint (Prometheus-based, not a BPF map) |

Map sizing can be adjusted via the Helm value `bpf.mapDynamicSizeRatio` (default: 0, meaning static sizing). Setting this to a decimal ratio (e.g., 0.0025 = 0.25% of total system memory) enables dynamic BPF map sizing:

```bash
helm upgrade cilium cilium/cilium --version 1.19.5 \
  --namespace kube-system \
  --reuse-values \
  --set bpf.mapDynamicSizeRatio=0.0025
```

## Datapath Modes

Cilium supports two datapath modes for cross-node pod communication:

### Tunneling (Encapsulation)

**Default mode.** Pod packets are encapsulated in VXLAN (UDP 8472) or Geneve (UDP 6081) and routed between nodes. The pod IP is hidden inside the tunnel — the underlay network only sees node IPs.

| Pros | Cons |
|---|---|
| Works on any network fabric | MTU overhead (VXLAN: 50 bytes; Geneve adds 50+ bytes depending on options) |
| No need to route pod IPs in underlay | Slightly higher CPU for encap/decap |
| Pod IPs can overlap across clusters | |

```yaml
# Helm values for tunneling (default)
routingMode: tunnel
tunnelProtocol: vxlan  # or geneve
```

### Native Routing (Direct Routing)

Pod IPs are directly routed on the underlay network. The node routes pod traffic using the kernel routing table without encapsulation.

| Pros | Cons |
|---|---|
| No MTU overhead | Underlay network must route pod CIDRs |
| Lower latency, higher throughput | IPAM integration required (e.g., AWS ENI, Azure) |
| Better performance | Harder to use with overlapping pod CIDRs |

```yaml
# Helm values for native routing
routingMode: native
autoDirectNodeRoutes: true
ipam.mode: kubernetes
```

## Kernel Configuration Flags

The following kernel config options are required for Cilium to function (all typically enabled in modern distribution kernels):

```
# Core eBPF
CONFIG_BPF=y
CONFIG_BPF_SYSCALL=y
CONFIG_BPF_JIT=y
CONFIG_NET_CLS_BPF=y
CONFIG_NET_CLS_ACT=y
CONFIG_NET_SCH_INGRESS=y
CONFIG_BPF_EVENTS=y
CONFIG_DEBUG_INFO_BTF=y

# cgroup / cgroup BPF
CONFIG_CGROUPS=y
CONFIG_CGROUP_BPF=y

# Tunneling
CONFIG_VXLAN=y
CONFIG_GENEVE=y
CONFIG_FIB_RULES=y

# Networking (iptables fallback)
CONFIG_NETFILTER_XT_TARGET_TPROXY=m
CONFIG_NETFILTER_XT_MATCH_SOCKET=m

# Misc
CONFIG_PERF_EVENTS=y
CONFIG_SCHEDSTATS=y
CONFIG_CRYPTO_SHA1=y
CONFIG_CRYPTO_USER_API_HASH=y
```

> `CONFIG_DEBUG_INFO_BTF=y` is especially important. BTF (BPF Type Format) enables CO-RE (Compile Once, Run Everywhere), allowing Cilium to ship pre-compiled eBPF binaries that work across different kernel versions without needing kernel headers on each node.

## BTF (BPF Type Format)

BTF is a metadata format that describes kernel data structures. Cilium uses BTF for:

1. **CO-RE portability** — one eBPF binary runs on kernel 5.10, 6.1, 6.8, etc.
2. **Kernel config introspection** — Cilium checks which CONFIG flags are enabled at runtime
3. **Better debugging** — `bpftool` can display BTF-enriched information

Check if BTF is available:

```bash
ls /sys/kernel/btf/vmlinux 2>/dev/null && echo "BTF available" || echo "BTF not available"
```

## See Also

- [installation.md](installation.md) — kernel requirements checking during setup
- [network-policies.md](network-policies.md) — how policies are enforced via TC BPF programs
- [troubleshooting.md](troubleshooting.md) — debugging BTF and kernel config issues
