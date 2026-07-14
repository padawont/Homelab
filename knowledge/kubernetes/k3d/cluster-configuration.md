---
title: "k3d Cluster Configuration"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k3d
  - configuration
  - multi-node
  - kubernetes
sources:
  - url: "https://k3d.io/v5.6.0/usage/configfile/"
    title: "k3d — Using Config Files"
  - url: "https://k3d.io/v5.6.0/usage/multiserver/"
    title: "k3d — Multi-Server Clusters"
  - url: "https://k3d.io/v5.6.0/usage/k3s/"
    title: "k3d — K3s Features"
  - url: "https://k3d.io/v5.6.0/design/defaults/"
    title: "k3d — Defaults"
  - url: "https://k3d.io/v5.6.0/design/concepts/"
    title: "k3d — Concepts (NodeFilters)"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_cluster_create/"
    title: "k3d cluster create command"
last_audit_date: 2026-07-10
---

# k3d Cluster Configuration

## Multi-Node Clusters

### Server Nodes

```bash
k3d cluster create multiserver --servers 3
```

Creates 3 server nodes using k3s' embedded etcd database. For best results, use 1, 3, or 5 servers (etcd quorum). At least 2 cores and 4 GiB of RAM are recommended per node.

The first server node (`server-0`) is the initializing node and uses the `--cluster-init` flag. Other server nodes connect to it via `--server https://<init-node>:6443`.

### Adding Server Nodes to a Running Cluster

```bash
k3d node create newserver --cluster multiserver --role server
```

**Trap**: If the cluster was initially created with a single server node, adding more will fail — the initial node was not started with `--cluster-init`.

### Agent Nodes

```bash
k3d cluster create mycluster --servers 1 --agents 2
```

Agents are worker nodes that run workloads but do not participate in the control plane.

---

## Port Mappings

### Syntax

```
[HOST:][HOSTPORT:]CONTAINERPORT[/PROTOCOL][@NODEFILTER]
```

### Examples

```bash
# Map host port 8081 to container port 80 on the load balancer
k3d cluster create -p "8081:80@loadbalancer"

# Map to a specific agent node
k3d cluster create -p "8082:30080@agent:0" --agents 2

# Map a range (NodePort range 30000-32767)
k3d cluster create -p "30000-32767:30000-32767@server:0"
```

**Warning**: Docker creates iptables entries per port mapping. Mapping large ranges may take a long time or freeze your system.

### Node Filters

Node filters control which nodes a setting applies to. Syntax: `@<group>:<subset>[:suffix]`

| Filter | Matches |
|---|---|
| `@server:0` | First server node |
| `@agent:*` | All agent nodes |
| `@all` | All nodes including load balancer |
| `@loadbalancer` | The ServersLB / proxy container |
| `@server:1,3` | Server nodes 1 and 3 |
| `@agent:2-4` | Agent nodes 2 through 4 |

---

## Load Balancer (ServersLB)

By default, k3d creates an Nginx load balancer in front of the server nodes. It handles:
- Port forwarding from host to cluster
- API server traffic (default port 6443)

```bash
# Disable the load balancer
k3d cluster create --no-lb

# Override Nginx settings
k3d cluster create --lb-config-override settings.workerConnections=2048
```

Default Nginx settings:

| Setting | Default |
|---|---|
| `proxy_timeout` (default) | 600s |
| `worker_connections` | 1024 |

---

## API Port

```bash
k3d cluster create --api-port 0.0.0.0:6443
```

Exposes the Kubernetes API server on a specific host IP and port. Without this flag, a random host port is used.

By default, the API port is exposed via the load balancer (not directly from the server node).

---

## K3s Arguments Passthrough

Pass additional arguments directly to the k3s process:

```bash
# Disable default Traefik ingress controller
k3d cluster create --k3s-arg "--disable=traefik@server:0"

# Disable default Flannel CNI (required for Cilium or Calico)
k3d cluster create --k3s-arg "--flannel-backend=none@server:*"

# Disable klipper ServiceLB (required when using Cilium kube-proxy replacement)
k3d cluster create --k3s-arg "--disable=servicelb@server:*"

# Pass flags to kube-apiserver
k3d cluster create --k3s-arg "--kube-apiserver-arg=feature-gates=EphemeralContainers=true@server:*"

# Set kubelet args on agents
k3d cluster create --k3s-arg "--kubelet-arg=eviction-hard=imagefs.available<1%,nodefs.available<1%@agent:*"
```

The `@server:0` node filter specifies which node the argument applies to. The argument is passed to the k3s `server` or `agent` command. See the [Calico guide](https://k3d.io/v5.6.0/usage/advanced/calico/) for a full CNI replacement example — the same pattern applies to Cilium.

---

## Image Selection

```bash
k3d cluster create --image rancher/k3s:v1.28.0-k3s1
```

Pin a specific k3s image version. Defaults to the latest stable k3s release.

---

## Environment Variables

```bash
k3d cluster create -e "HTTP_PROXY=my.proxy.com@server:0" -e "SOME_KEY=SOME_VAL@server:0"
```

Add environment variables to specific nodes using node filters.

---

## Config File (YAML)

Use a YAML config file for repeatable cluster definitions:

```bash
k3d cluster create --config /path/to/k3d-config.yaml
```

```yaml
# k3d-config.yaml
apiVersion: k3d.io/v1alpha5
kind: Simple
metadata:
  name: mycluster
servers: 1
agents: 2
kubeAPI:
  host: "myhost.my.domain"
  hostIP: "127.0.0.1"
  hostPort: "6445"
image: rancher/k3s:v1.20.4-k3s1
network: my-custom-net
volumes:
  - volume: /my/host/path:/path/in/node
    nodeFilters:
      - server:0
ports:
  - port: 8080:80
    nodeFilters:
      - loadbalancer
registries:
  create:
    name: registry.localhost
    host: "0.0.0.0"
    hostPort: "5000"
options:
  k3d:
    wait: true
    timeout: "60s"
    disableLoadbalancer: false
  kubeconfig:
    updateDefaultKubeconfig: true
    switchCurrentContext: true
```

### Scaffold a Config File

```bash
k3d config init
```

Generates a starter config file with all available options.

### Config Precedence

Internal Setting > CLI Flag > Environment Variable > Config File > Defaults

CLI flags override config file values, letting you share a base config across clusters and override specific fields per cluster.

---

## Subnet

```bash
k3d cluster create --subnet 172.28.0.0/16
```

[Experimental] Define a custom subnet for the cluster's Docker network.

---

## Host Aliases

```bash
k3d cluster create --host-alias "1.2.3.4:my.host.local,that.other.local"
```

Injects entries into `/etc/hosts` in node containers and into CoreDNS NodeHosts.
