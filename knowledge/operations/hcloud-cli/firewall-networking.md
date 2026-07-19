---
title: "Firewall & Networking"
status: draft
author: "refactorartist"
date: 2026-07-11
tags:
  - hetzner
  - hcloud
  - firewall
  - network
  - volume
  - subnet
  - security
sources:
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_firewall_create.md"
    title: "hcloud firewall create — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_firewall_add-rule.md"
    title: "hcloud firewall add-rule — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_firewall_delete-rule.md"
    title: "hcloud firewall delete-rule — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_firewall_apply-to-resource.md"
    title: "hcloud firewall apply-to-resource — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_firewall_remove-from-resource.md"
    title: "hcloud firewall remove-from-resource — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_network_create.md"
    title: "hcloud network create — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_network_add-subnet.md"
    title: "hcloud network add-subnet — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_network_remove-subnet.md"
    title: "hcloud network remove-subnet — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_volume_create.md"
    title: "hcloud volume create — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_volume_attach.md"
    title: "hcloud volume attach — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_volume_detach.md"
    title: "hcloud volume detach — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_volume_resize.md"
    title: "hcloud volume resize — Reference"
last_audit_date: 2026-07-11
---

# Firewall & Networking

## Firewall Management

### Creating Firewalls

```bash
# Create a firewall with a name
hcloud firewall create --name my-firewall

# Create with initial rules from a JSON file
hcloud firewall create --name my-firewall --rules-file rules.json
```

Source: [hcloud firewall create](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_firewall_create.md)

### Managing Firewall Rules

Rules are added or removed individually. Each rule specifies direction, protocol, ports, and IP ranges.

```bash
# Inbound TCP rule (port 80)
hcloud firewall add-rule \
  --direction in \
  --source-ips 0.0.0.0/0 \
  --protocol tcp \
  --port 80 \
  my-firewall

# Inbound TCP rule (port 443)
hcloud firewall add-rule \
  --direction in \
  --source-ips 0.0.0.0/0 \
  --protocol tcp \
  --port 443 \
  my-firewall

# Inbound ICMP rule (no port required)
hcloud firewall add-rule \
  --direction in \
  --source-ips 0.0.0.0/0 \
  --protocol icmp \
  my-firewall

# Restrict SSH access to specific IPs
hcloud firewall add-rule \
  --direction in \
  --source-ips <office-ip>/32 \
  --protocol tcp \
  --port 22 \
  my-firewall

# Outbound DNS rule
hcloud firewall add-rule \
  --direction out \
  --destination-ips 0.0.0.0/0 \
  --protocol udp \
  --port 53 \
  my-firewall

# Outbound HTTPS rule
hcloud firewall add-rule \
  --direction out \
  --destination-ips 0.0.0.0/0 \
  --protocol tcp \
  --port 443 \
  my-firewall
```

Source: [hcloud firewall add-rule](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_firewall_add-rule.md)

### Deleting Firewall Rules

```bash
hcloud firewall delete-rule \
  --direction in \
  --source-ips 0.0.0.0/0 \
  --protocol tcp \
  --port 80 \
  my-firewall
```

Source: [hcloud firewall delete-rule](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_firewall_delete-rule.md)

### Replacing All Rules

Replace all rules atomically from a JSON file:

```bash
hcloud firewall replace-rules --rules-file rules.json my-firewall
```

### Applying and Removing Firewalls

```bash
# Apply firewall to a server
hcloud firewall apply-to-resource --type server --server my-server my-firewall

# Apply firewall to all resources matching a label selector
hcloud firewall apply-to-resource --type label_selector --label-selector env=prod my-firewall

# Remove firewall from a server
hcloud firewall remove-from-resource --type server --server my-server my-firewall
```

Source: [hcloud firewall apply-to-resource](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_firewall_apply-to-resource.md), [remove-from-resource](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_firewall_remove-from-resource.md)

### Listing and Describing Firewalls

```bash
hcloud firewall list
hcloud firewall describe my-firewall
hcloud firewall delete my-firewall
hcloud firewall update my-firewall
```

## Network Management

### Creating Networks

```bash
# Create a network with a private IP range (RFC 1918)
hcloud network create --name my-network --ip-range 10.0.0.0/16
```

### Listing, Describing, and Deleting Networks

```bash
# List all networks
hcloud network list

# Describe a specific network
hcloud network describe my-network

# Delete a network
hcloud network delete my-network
```

Source: [hcloud network create](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_network_create.md)

### Managing Subnets

Subnets carve out smaller IP ranges from the network's IP range for specific purposes. Subnet types:
- **cloud** — Default type for Hetzner Cloud resources
- **server** — For servers attached directly
- **vswitch** — For vSwitch connections

```bash
# Add a cloud subnet
hcloud network add-subnet \
  --type cloud \
  --network-zone eu-central \
  --ip-range 10.0.1.0/24 \
  my-network

# Add a server subnet
hcloud network add-subnet \
  --type server \
  --network-zone eu-central \
  --ip-range 10.0.2.0/24 \
  my-network

# Remove a subnet (by exact IP range)
hcloud network remove-subnet --ip-range 10.0.1.0/24 my-network
```

Source: [hcloud network add-subnet](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_network_add-subnet.md), [remove-subnet](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_network_remove-subnet.md)

### Network Routes and IP Range Changes

```bash
# Add a route
hcloud network add-route --destination 10.0.0.0/16 --gateway 10.0.0.1 my-network

# Remove a route
hcloud network remove-route --destination 10.0.0.0/16 --gateway 10.0.0.1 my-network

# Change IP range (careful — may affect existing resources)
hcloud network change-ip-range --ip-range 10.0.0.0/8 my-network
```

### Server Network Attachment

```bash
# Attach server to network (can also be done at server creation time)
hcloud server attach-to-network --network my-network my-server

# Detach server from network
hcloud server detach-from-network my-server
```

## Volume Management

### Creating Volumes

```bash
# Create a 50 GB volume
hcloud volume create --name my-volume --size 50

# Create with location, auto-attach, and format
hcloud volume create \
  --name my-volume \
  --size 50 \
  --location nbg1 \
  --server my-server \
  --automount \
  --format ext4
```

Source: [hcloud volume create](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_volume_create.md)

### Attaching and Detaching Volumes

```bash
# Attach to a server
hcloud volume attach --server my-server my-volume

# Attach with automount
hcloud volume attach --automount --server my-server my-volume

# Detach from its current server
hcloud volume detach my-volume
```

Source: [hcloud volume attach](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_volume_attach.md), [detach](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_volume_detach.md)

### Resizing Volumes

```bash
# Increase volume size (can only be increased, not decreased)
hcloud volume resize --size 100 my-volume
```

Source: [hcloud volume resize](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_volume_resize.md)

### Listing and Deleting Volumes

```bash
hcloud volume list
hcloud volume describe my-volume
hcloud volume delete my-volume
hcloud volume update my-volume
```

## IP Range Planning for Multi-Tier Deployments

When building multi-tier deployments with private networking, plan IP ranges to leave room for growth:

1. **Primary network** — e.g., `10.0.0.0/16`
2. **Tier 1 subnet** — e.g., `10.0.1.0/24` (256 addresses for compute nodes)
3. **Tier 2 subnet** — e.g., `10.0.2.0/24` (for internal services)
4. **Tier 3 subnet** — e.g., `10.0.3.0/24` (for data/storage layer)

Example:

```bash
# Create network with a private IP range
hcloud network create --name app-cluster --ip-range 10.0.0.0/16

# Add subnets per tier
hcloud network add-subnet --type cloud --network-zone eu-central --ip-range 10.0.1.0/24 app-cluster
hcloud network add-subnet --type cloud --network-zone eu-central --ip-range 10.0.2.0/24 app-cluster

# Create a firewall for the application tier
hcloud firewall create --name app-tier

# Allow inbound traffic to the application
hcloud firewall add-rule --direction in --source-ips <admin-ip>/32 --protocol tcp --port 443 app-tier
```

## Related

- [Server Lifecycle](./server-lifecycle.md) — Attaching firewalls, networks, and volumes during server creation
- [Scripting](./scripting.md) — Automating firewall and network batch operations
