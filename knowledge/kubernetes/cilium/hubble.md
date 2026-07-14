---
title: "Hubble Observability"
status: draft
author: padawont
date: 2026-07-11
tags:
  - cilium
  - hubble
  - observability
  - kubernetes
sources:
  - url: "https://docs.cilium.io/en/stable/observability/hubble/"
    title: "Network Observability with Hubble"
  - url: "https://docs.cilium.io/en/stable/observability/hubble/setup/"
    title: "Setting up Hubble Observability"
  - url: "https://docs.cilium.io/en/stable/observability/hubble/hubble-cli/"
    title: "Inspecting Network Flows with the CLI"
  - url: "https://docs.cilium.io/en/stable/observability/hubble/hubble-ui/"
    title: "Service Map & Hubble UI"
last_audit_date: 2026-07-11
---

# Hubble Observability

Hubble is the observability layer of Cilium. It provides deep visibility into network traffic at L3/L4 and L7 layers, service dependency maps, and flow-level monitoring — all without requiring sidecars or application changes.

## Architecture

Hubble has three components:

| Component | Role | Network |
|---|---|---|
| **Hubble server** | Runs inside each Cilium agent pod. Exposes a local gRPC API on a Unix socket (`/var/run/cilium/hubble.sock`) and TCP 4244. | Per-node |
| **Hubble Relay** | Aggregates flow data from all Hubble servers in the cluster. Exposes a cluster-wide gRPC API on TCP 4245. | Cluster-wide |
| **Hubble UI** | Web UI that renders a Service Map (dependency graph) from Relay data. Accessed via port-forward or Ingress. | Cluster-wide |

Without Relay, the Hubble CLI can only query flows observed by a single node. With Relay, `hubble observe` returns flows from all nodes.

## Enable Hubble

### Via Cilium CLI

If Cilium was installed via `cilium install`:

```bash
cilium hubble enable
```

This patches the ConfigMap, restarts Cilium pods, generates TLS certificates for Relay, and deploys the Relay Deployment.

### Via Helm

```bash
helm upgrade cilium cilium/cilium --version 1.19.5 \
  --namespace kube-system \
  --reuse-values \
  --set hubble.relay.enabled=true
```

### Verify Hubble Is Running

```bash
cilium status
```

Expected output shows `Hubble Relay: OK`:

```
    /¯¯\
 /¯¯\__/¯¯\    Cilium:             OK
 \__/¯¯\__/    Operator:           OK
 /¯¯\__/¯¯\    Hubble Relay:       OK
    \__/       ClusterMesh:        disabled
```

## Install the Hubble CLI

The Hubble CLI is installed separately from the Cilium CLI:

```bash
HUBBLE_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/hubble/main/stable.txt)
HUBBLE_ARCH=amd64
if [ "$(uname -m)" = "aarch64" ]; then HUBBLE_ARCH=arm64; fi
curl -L --fail --remote-name-all https://github.com/cilium/hubble/releases/download/$HUBBLE_VERSION/hubble-linux-${HUBBLE_ARCH}.tar.gz{,.sha256sum}
sha256sum --check hubble-linux-${HUBBLE_ARCH}.tar.gz.sha256sum
sudo tar xzvfC hubble-linux-${HUBBLE_ARCH}.tar.gz /usr/local/bin
rm hubble-linux-${HUBBLE_ARCH}.tar.gz{,.sha256sum}
```

## Access Hubble Relay

The Hubble CLI connects to Relay on `localhost:4245`. Use port-forward for access:

**Via Cilium CLI:**
```bash
cilium hubble port-forward
```

**Via kubectl:**
```bash
kubectl -n kube-system port-forward service/hubble-relay 4245:80
```

## Flow Inspection

### Basic Flow Dump

```bash
hubble observe -P
```

Output shows timeline of flows with: timestamp, source pod:port, destination pod:port, verdict, protocol.

### Filter by Time

```bash
hubble observe -P --since 3m
hubble observe -P --since 1h
```

### Filter by Pod Labels

```bash
hubble observe -P --from-pod default/nginx --to-pod default/echo
hubble observe -P --pod default/nginx
```

The `--pod` flag matches either source or destination.

### Filter by Verdict

```bash
hubble observe -P --verdict DROPPED
hubble observe -P --verdict FORWARDED
```

### Filter by Protocol

```bash
hubble observe -P --protocol TCP
hubble observe -P --protocol UDP
hubble observe -P --protocol http
```

### JSON Output

```bash
hubble observe -P -o json
```

Returns detailed per-flow information including security identities, endpoint IDs, and trace details.

### Node-Level Observability (Without Relay)

Run `hubble` directly inside a Cilium pod on a specific node:

```bash
kubectl -n kube-system exec ds/cilium -- hubble observe --since 3m --pod default/tiefighter
```

This queries only the local Hubble server on that node.

## Hubble UI / Service Map

### Enable Hubble UI

```bash
# If Hubble is already enabled, disable it first:
cilium hubble disable

# Then enable with UI:
cilium hubble enable --ui
```

Or via Helm:

```bash
helm upgrade cilium cilium/cilium --version 1.19.5 \
  --namespace kube-system \
  --reuse-values \
  --set hubble.ui.enabled=true
```

### Access Hubble UI

```bash
cilium hubble ui
```

This opens a browser at `http://localhost:12000`. The UI renders a **Service Map** showing:
- All namespaces and their pods as nodes in a dependency graph
- L3/L4 and L7 flows between services
- Verdict status (allowed, dropped) color-coded on edges
- Filterable by namespace, labels, and time range

## Verdict and Identity in Flow Output

Each flow line in Hubble output contains:

```
<timestamp>: <src-namespace>/<src-pod>:<src-port> <dir> <dst-namespace>/<dst-pod>:<dst-port> <path> <verdict> (<protocol> <flags>)
```

- `dir`: `->` (egress from perspective), `<-` (ingress), `<>` (forwarded through node)
- `path`: `to-endpoint` (local), `to-overlay` (via tunnel), `to-stack` (host)
- `verdict`: `FORWARDED`, `DROPPED`, `ERROR`

## Hubble Relay Status

Check which nodes Hubble Relay is connected to:

```bash
hubble list nodes -P
```

Output:
```
NAME              STATUS      AGE     FLOWS/S   CURRENT/MAX-FLOWS
cluster/node-cp   Connected   2m30s   13.94     2227/4095 ( 54.38%)
cluster/node-w1   Connected   2m31s   51.37     5108/9840 ( 51.91%)
```

## Good Example: Validate a Policy

After applying a CiliumNetworkPolicy, run:

```bash
# Deploy test pods
kubectl run nginx --image=nginx
kubectl run echo --image=hashicorp/http-echo -- --text="hello"

# Watch flows between them
hubble observe -P --from-pod default/nginx --to-pod default/echo
```

If the policy allows the traffic, flows show `FORWARDED`. If denied, they show `DROPPED` with `(Policy denied)`.

For installation and troubleshooting context, see [installation.md](installation.md), [network-policies.md](network-policies.md), and [troubleshooting.md](troubleshooting.md).
