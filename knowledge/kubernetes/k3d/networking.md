---
title: "k3d Networking"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k3d
  - networking
  - kubernetes
  - ingress
sources:
  - url: "https://k3d.io/v5.6.0/usage/exposing_services/"
    title: "k3d — Exposing Services"
  - url: "https://k3d.io/v5.6.0/design/networking/"
    title: "k3d — Networking Design"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_cluster_create/"
    title: "k3d cluster create (port mapping flags)"
  - url: "https://k3d.io/v5.6.0/usage/k3s/"
    title: "k3d — K3s Features (Traefik, servicelb, CoreDNS)"
  - url: "https://k3d.io/v5.6.0/design/defaults/"
    title: "k3d — Defaults (networking)"
last_audit_date: 2026-07-10
---

# k3d Networking

## Cluster Network

By default, k3d creates a new Docker bridge network for each cluster, named `k3d-<clustername>`. All node containers in the cluster are attached to this network and can resolve each other by container name.

```bash
# Join an existing Docker network instead
k3d cluster create mycluster --network my-custom-net
```

When using `--network`, the network is not managed by k3d (it won't be created or removed with the cluster lifecycle).

### Docker Network Modes

| Mode | Command | Notes |
|---|---|---|
| Bridge (default) | — | Each cluster gets its own `k3d-*` bridge network |
| Host | `--network host` | Cannot create multiple server nodes; single server + single agent only |
| Existing bridge | `--network my-net` | Must exist before cluster creation |

---

## Port Forwarding

Port forwarding is the primary way to access services running in the cluster from your host machine.

### Via ServersLB (Recommended)

The default Nginx load balancer (ServersLB) proxies host ports to the cluster:

```bash
k3d cluster create mycluster -p "8081:80@loadbalancer"
```

This maps host port `8081` to container port `80` on the load balancer container, which then forwards to port `80` on all server nodes.

### Direct to Agent Node

```bash
k3d cluster create mycluster -p "8082:30080@agent:0" --agents 2
```

Maps host port `8082` to container port `30080` on the first agent node (index 0). Useful for NodePort services.

### Port Range

```bash
k3d cluster create mycluster -p "30000-32767:30000-32767@server:0"
```

Exposes the entire Kubernetes NodePort range. **Warning**: Docker creates iptables entries per port — this may be slow or freeze your system with large ranges.

---

## Exposing Services

Two methods to expose applications running in the cluster. See the [Services](../services.md), [Ingress](../ingress.md), and [DNS](../dns.md) fundamentals for detailed Kubernetes-level explanations.

### 1. Via Ingress (Recommended)

```bash
# 1. Create cluster with port mapping
k3d cluster create mycluster -p "8081:80@loadbalancer" --agents 2

# 2. Create a deployment and ClusterIP service
kubectl create deployment nginx --image=nginx
kubectl create service clusterip nginx --tcp=80:80

# 3. Create an ingress
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx
  annotations:
    ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
EOF

# 4. Access via localhost
curl localhost:8081/
```

k3d ships Traefik as the default ingress controller (listening on port 80 in the cluster).

### 2. Via NodePort

```bash
# 1. Create cluster with a NodePort range mapped to an agent
k3d cluster create mycluster -p "8082:30080@agent:0" --agents 2

# 2. Create a NodePort service
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  labels:
    app: nginx
  name: nginx
spec:
  ports:
  - name: 80-80
    nodePort: 30080
    port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: nginx
  type: NodePort
EOF

# 3. Access via localhost
curl localhost:8082/
```

---

## DNS Resolution

### CoreDNS

k3d includes CoreDNS (standard k3s component) for cluster DNS. Pods resolve each other by Service name within the same namespace (`service-name`) or across namespaces (`service-name.namespace.svc.cluster.local`).

### host.k3d.internal

k3d injects a special DNS entry `host.k3d.internal` into CoreDNS NodeHosts. This resolves to the Docker network gateway IP, providing access to services running on the Docker host from inside the cluster.

### Host Aliases

```bash
k3d cluster create mycluster --host-alias "1.2.3.4:my.host.local"
```

Injects entries into `/etc/hosts` in node containers and into CoreDNS NodeHosts.

---

## ServersLB (Load Balancer)

k3d's default Nginx load balancer:
- Proxies the Kubernetes API (port 6443) to server nodes
- Handles all port mappings specified via `-p` flags
- Listens on the same ports as specified and forwards to all server nodes

```bash
# Disable load balancer
k3d cluster create mycluster --no-lb
```

Without the load balancer, port mappings go directly to server/agent nodes and you must use `--api-port` to expose the API server.

---

## Cross-Container Communication

Containers on the same Docker network as the k3d cluster can reach the cluster by node container name:

```
curl http://k3d-mycluster-server-0:8080/
```

Connect your own container to the cluster's network:

```bash
docker run --network k3d-mycluster myapp
```
