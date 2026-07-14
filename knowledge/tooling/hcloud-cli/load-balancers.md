---
title: "Load Balancers"
status: draft
author: "refactorartist"
date: 2026-07-11
tags:
  - hetzner
  - hcloud
  - load-balancer
  - networking
  - traffic
sources:
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_load-balancer_create.md"
    title: "hcloud load-balancer create — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_load-balancer_add-target.md"
    title: "hcloud load-balancer add-target — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_load-balancer_remove-target.md"
    title: "hcloud load-balancer remove-target — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_load-balancer_add-service.md"
    title: "hcloud load-balancer add-service — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_load-balancer.md"
    title: "hcloud load-balancer — Reference"
  - url: "https://docs.hetzner.cloud/"
    title: "Hetzner Cloud API Documentation"
last_audit_date: 2026-07-11
---

# Load Balancers

Hetzner Cloud Load Balancers distribute incoming traffic across multiple servers for high availability and scalability.

## Types

List available load balancer types:

```bash
hcloud load-balancer-type list
hcloud load-balancer-type describe <type>
```

## Creating Load Balancers

```bash
# Basic creation with type
hcloud load-balancer create --name my-lb --type lb11

# With location, algorithm, and network
hcloud load-balancer create \
  --name my-lb \
  --type lb11 \
  --location nbg1 \
  --algorithm-type round_robin \
  --network my-network
```

Algorithm types: `round_robin` (default), `least_connections`

Source: [hcloud load-balancer create](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_load-balancer_create.md)

## Managing Targets

Targets are servers (or IPs or label selectors) that receive traffic from the load balancer.

### Adding Targets

```bash
# Add a server target (uses public IP)
hcloud load-balancer add-target --server my-server my-lb

# Add a server target using private IP
hcloud load-balancer add-target --server my-server --use-private-ip my-lb

# Add targets by label selector
hcloud load-balancer add-target --label-selector app=web my-lb

# Add an IP target (external endpoint)
hcloud load-balancer add-target --ip 192.168.1.100 my-lb
```

Source: [hcloud load-balancer add-target](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_load-balancer_add-target.md)

### Removing Targets

```bash
hcloud load-balancer remove-target --server my-server my-lb
hcloud load-balancer remove-target --ip 192.168.1.100 my-lb
hcloud load-balancer remove-target --label-selector app=web my-lb
```

Source: [hcloud load-balancer remove-target](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_load-balancer_remove-target.md)

## Managing Services

Services define the ports and protocols the load balancer listens on and forwards to targets.

### Adding Services

```bash
# TCP service (port 80 → port 80)
hcloud load-balancer add-service \
  --protocol tcp \
  --listen-port 80 \
  --destination-port 80 \
  my-lb

# HTTP service
hcloud load-balancer add-service \
  --protocol http \
  --listen-port 80 \
  --destination-port 80 \
  my-lb

# HTTPS service with certificates
hcloud load-balancer add-service \
  --protocol https \
  --listen-port 443 \
  --destination-port 443 \
  --http-certificates <cert-ids> \
  my-lb
```

Source: [hcloud load-balancer add-service](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_load-balancer_add-service.md)

### Updating and Deleting Services

```bash
# Update a service (change destination port)
hcloud load-balancer update-service \
  --listen-port 80 \
  --protocol http \
  --destination-port 8080 \
  my-lb

# Delete a service
hcloud load-balancer delete-service --listen-port 80 my-lb
```

## Other Operations

```bash
# List all load balancers
hcloud load-balancer list

# Describe a load balancer
hcloud load-balancer describe my-lb

# Change type (scale up/down)
hcloud load-balancer change-type my-lb

# Network attachment
hcloud load-balancer attach-to-network --network my-network my-lb
hcloud load-balancer detach-from-network my-lb

# Delete a load balancer
hcloud load-balancer delete my-lb
```

## Load Balancer Setup Example

```bash
# 1. Create a load balancer
hcloud load-balancer create --name web-lb --type lb11 --location nbg1

# 2. Add targets (servers)
hcloud load-balancer add-target --server web-1 web-lb
hcloud load-balancer add-target --server web-2 web-lb
hcloud load-balancer add-target --server web-3 web-lb

# 3. Add an HTTP service
hcloud load-balancer add-service \
  --protocol http \
  --listen-port 80 \
  --destination-port 80 \
  web-lb

# 4. Describe to verify
hcloud load-balancer describe web-lb
```

## Related

- [Server Lifecycle](./server-lifecycle.md) — Creating and managing target servers
- [Placement Groups](./placement-groups.md) — Distributing target servers across hosts
- [Firewall & Networking](./firewall-networking.md) — Firewall rules for load balancer traffic
- [Scripting](./scripting.md) — Automating load balancer setup
