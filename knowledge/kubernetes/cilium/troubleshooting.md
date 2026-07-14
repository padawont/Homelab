---
title: "Cilium Troubleshooting"
status: draft
author: padawont
date: 2026-07-11
tags:
  - cilium
  - troubleshooting
  - debugging
  - kubernetes
sources:
  - url: "https://docs.cilium.io/en/stable/operations/troubleshooting/"
    title: "Cilium Troubleshooting Guide"
  - url: "https://docs.cilium.io/en/stable/network/kubernetes/troubleshooting/"
    title: "Kubernetes Networking Troubleshooting"
  - url: "https://docs.cilium.io/en/stable/operations/system_requirements/"
    title: "System Requirements (BPF fs, cgroupv2)"
  - url: "https://docs.cilium.io/en/stable/observability/hubble/setup/"
    title: "Setting up Hubble Observability (troubleshooting section)"
  - url: "https://docs.cilium.io/en/stable/security/policy/troubleshooting/"
    title: "Policy Troubleshooting"
last_audit_date: 2026-07-11
---

# Cilium Troubleshooting

This note covers debugging and troubleshooting Cilium in a k3d/k3s cluster. It covers cluster health checks, connectivity tests, sysdump collection, policy debugging, and common failure modes.

## Prerequisites

Before troubleshooting, ensure:
- Cilium is installed and running (see [installation.md](installation.md))
- `cilium` CLI and `kubectl` are available
- You have access to the cluster's kubeconfig

## Cluster Health

### Pod Status

Verify all Cilium components are running:

```bash
kubectl -n kube-system get pods -l k8s-app=cilium
kubectl -n kube-system get pods -l io.cilium/app=operator
kubectl -n kube-system get pods -l k8s-app=hubble-relay
```

Expected: all pods in `Running` state. If any pod is in `CrashLoopBackoff`, proceed to detailed status.

### Detailed Agent Status

Within a Cilium pod, run the full status check:

```bash
kubectl -n kube-system exec ds/cilium -- cilium-dbg status --verbose
```

Key sections in verbose output:
- **KVStore:** etcd connection status (only relevant in kvstore mode)
- **Kubernetes:** API server connectivity
- **Cilium:** Overall agent health
- **KubeProxyReplacement:** Shows `True` or `False` and which devices are used
- **Hubble:** Flow capacity and current usage
- **IPAM:** Address allocation (allocated/total)

### Quick Status via CLI

```bash
cilium status
```

Shows a high-level dashboard with component health, desired vs ready pod counts, and managed pod count.

## Connectivity Test

The connectivity test deploys a test namespace with echo servers and client pods that exercise various connectivity paths (pod-to-pod, pod-to-service, pod-to-external, with and without policies).

```bash
# Run the full test suite
cilium connectivity test
```

Expected output:
```
---------------------------------------------------------------------------------------------------------------------
📋 Test Report
---------------------------------------------------------------------------------------------------------------------
✅ 69/69 tests successful (0 warnings)
```

### Manual Connectivity Check

To deploy the test manifests manually:

```bash
kubectl create ns cilium-test
kubectl apply -n cilium-test -f https://raw.githubusercontent.com/cilium/cilium/1.19.5/examples/kubernetes/connectivity-check/connectivity-check.yaml
kubectl get pods -n cilium-test
```

All pods should show `READY 1/1`. The pod names indicate the connectivity variant:
- `pod-to-a` — tests pod-to-pod within same node
- `pod-to-b-multi-node-clusterip` — tests cross-node through ClusterIP
- `pod-to-external-1111` — tests egress to external IPs
- `pod-to-a-allowed-cnp` — tests CiliumNetworkPolicy allow rules
- `pod-to-a-denied-cnp` — tests CiliumNetworkPolicy deny rules

Clean up:
```bash
kubectl delete ns cilium-test
```

## cilium sysdump

The sysdump collects all relevant diagnostic data from the cluster:

```bash
cilium sysdump --output-filename cilium-dump
```

### What Is Captured

| Artifact | What It Contains |
|---|---|
| `cilium-dbg-status-*.txt` | `cilium-dbg status --verbose` from each node |
| `cilium-dbg-endpoint-*.txt` | Endpoint list and details per node |
| `hubble-status-*.txt` | Hubble status per node |
| `cilium-configmap.yaml` | Current ConfigMap values |
| `cilium-bpf-*.txt` | BPF map dumps (ipcache, CT, policy) |
| `cilium-logs/` | Agent and operator logs |
| `kubernetes-*/` | Pod, Service, Node, Endpoint, and CRD YAML exports |

When reporting an issue, share the `cilium-dump.tar.gz` file and mention which artifacts are most relevant.

## Per-Node Debugging

### List Endpoints

```bash
kubectl -n kube-system exec ds/cilium -- cilium-dbg endpoint list
```

Columns: endpoint ID, pod name, IP, security identity, labels, and policy enforcement status (ingress/egress).

### Inspect a Specific Endpoint

```bash
kubectl -n kube-system exec ds/cilium -- cilium-dbg endpoint get <id>
```

This dumps the full endpoint state including:
- `spec` — desired policy state
- `status` — current realized state
- `status.policy.realized.l4` — rendered L4/L7 rules
- `status.identity` — assigned security identity

Use this to verify that your policy is being applied correctly.

### Monitor Packet Drops

```bash
kubectl -n kube-system exec ds/cilium -- cilium-dbg monitor --type drop
```

This shows real-time dropped packets with the reason:
```
xx drop (Policy denied) to endpoint 25729, identity 261->264: 10.11.13.37 -> 10.11.101.61 EchoRequest
```

Common drop reasons: `Policy denied`, `CT: Map insertion failed`, `Invalid destination mac`.

### Monitor All Traffic

```bash
kubectl -n kube-system exec ds/cilium -- cilium-dbg monitor --verbosity debug
```

## Policy Troubleshooting

### Check If a Pod Is Managed by Cilium

Pods not managed by Cilium will not have policy enforcement:

```bash
cilium status | grep "managed by Cilium"
```

Expected: `Cluster Pods: X/X managed by Cilium`

Pods in host networking or started before Cilium was deployed are unmanaged. Restart them:

```bash
kubectl rollout restart deployment <name>
```

### View Policy Selectors

```bash
kubectl -n kube-system exec ds/cilium -- cilium-dbg policy selectors
```

Shows how many identities each selector is matching. Selectors matching many identities can cause policymap pressure.

### Policymap Pressure

The metric `cilium_bpf_map_pressure{map_name="cilium_policy_v2_*"}` monitors endpoint policymap pressure. High pressure indicates too many identities selected by a single policy. Mitigations:

1. Broaden CIDR ranges (use `/30` instead of multiple `/32`)
2. Use `CiliumCIDRGroup` for large CIDR sets
3. Reduce permissiveness of label selectors

## Hubble Troubleshooting

### Check Hubble Status

```bash
hubble status -P
```

Expected:
```
Healthcheck (via 127.0.0.1:4245): Ok
Current/Max Flows: 11917/12288 (96.98%)
Flows/s: 11.74
Connected Nodes: 3/3
```

### Hubble Relay Connection Refused

If you see:
```
Error: connection error: desc = "transport: Error while dialing: dial tcp 127.0.0.1:4245: connect: connection refused"
```

The port-forward is not active. Run:
```bash
cilium hubble port-forward
```

### Hubble Relay Pod Not Ready

```bash
kubectl -n kube-system logs deployment/hubble-relay
```

Common issue: Relay cannot connect to `hubble-peer` service. Verify the service exists:
```bash
kubectl -n kube-system get svc hubble-peer
```

If Hubble is not enabled in Cilium, Relay will fail. Run `cilium status` and check for `Hubble: disabled`.

## Common Failure Modes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Nodes stuck `NotReady` after install | Flannel still enabled | Recreate cluster with `--flannel-backend=none` |
| Cilium pods in `CrashLoopBackoff` | BPF filesystem not mounted | `mount bpffs /sys/fs/bpf -t bpf` |
| `cgroupv2` errors in logs | Kernel using cgroup v1 | Boot with `systemd.unified_cgroup_hierarchy=1` |
| Policy not enforced on a pod | Pod started before Cilium | `kubectl rollout restart` the pod's Deployment |
| `CT: Map insertion failed` drops | Connection tracking full | Increase `bpf-ct-global-any-max` or reduce GC interval |
| `KubeProxyReplacement: False` | Missing kernel support | Check kernel ≥5.10, cgroupv2, BTF |
| Hubble Relay `connection refused` | Hubble not enabled in Cilium | `cilium hubble enable` |
| `cilium connectivity test` pods stuck `Pending` | Single-node cluster, multi-node tests can't schedule | Use at least 2 nodes (1 server + 1 agent) |
| `too many open files` during connectivity test | inotify limits too low | Increase `fs.inotify.max_user_instances` on host |

## Useful Scripts

Cilium provides helper scripts for troubleshooting:

```bash
# Run cilium-dbg status on all nodes
curl -sLO https://raw.githubusercontent.com/cilium/cilium/main/contrib/k8s/k8s-cilium-exec.sh
chmod +x k8s-cilium-exec.sh
./k8s-cilium-exec.sh cilium-dbg status

# List unmanaged pods
curl -sLO https://raw.githubusercontent.com/cilium/cilium/main/contrib/k8s/k8s-unmanaged.sh
chmod +x k8s-unmanaged.sh
./k8s-unmanaged.sh
```

Cilium agent logs on a specific node:

```bash
kubectl -n kube-system logs -l k8s-app=cilium --tail=100
kubectl -n kube-system logs -l k8s-app=cilium --tail=100 -p  # previous (crashed) pod logs
```

For Hubble observability details, see [hubble.md](hubble.md). For network policy reference, see [network-policies.md](network-policies.md).
