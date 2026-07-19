---
title: "Placement Groups"
status: draft
author: "refactorartist"
date: 2026-07-11
tags:
  - hetzner
  - hcloud
  - placement-group
  - availability
sources:
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_placement-group_create.md"
    title: "hcloud placement-group create — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_placement-group.md"
    title: "hcloud placement-group — Reference"
  - url: "https://docs.hetzner.cloud/"
    title: "Hetzner Cloud API Documentation"
last_audit_date: 2026-07-11
---

# Placement Groups

Placement groups control the physical distribution of servers across Hetzner Cloud infrastructure. They are used to influence server placement for availability or low-latency requirements.

## Types

| Type | Behavior | Use Case |
|---|---|---|
| `spread` | Servers are placed on separate physical hosts | High availability — reduces correlated failure risk |
| `strict_spread` | Servers are placed on separate physical hosts and racks | Maximum availability — also tolerates rack-level failures |

## Commands

### Creating Placement Groups

```bash
# Create a spread placement group (recommended for HA)
hcloud placement-group create --name my-group --type spread

# Create a strict spread placement group
hcloud placement-group create --name my-strict-group --type strict_spread
```

Source: [hcloud placement-group create](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_placement-group_create.md)

### Listing and Describing

```bash
# List all placement groups
hcloud placement-group list

# Describe a specific group (shows server members)
hcloud placement-group describe my-group
```

### Updating and Deleting

```bash
# Update name or labels
hcloud placement-group update my-group

# Delete a placement group (servers must be removed first)
hcloud placement-group delete my-group
```

Source: [hcloud placement-group](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_placement-group.md)

## Using with Servers

### During Creation

```bash
hcloud server create \
  --name my-server \
  --type cx22 \
  --image ubuntu-24.04 \
  --placement-group my-group
```

### Adding and Removing Existing Servers

```bash
# Add a server to a placement group
hcloud server add-to-placement-group --placement-group my-group my-server

# Remove a server from its placement group
hcloud server remove-from-placement-group my-server
```

## Availability Strategy

For high-availability workloads, use a `spread` placement group across your critical servers:

```bash
# Create group
hcloud placement-group create --type spread --name ha-web

# Create multiple servers in the group (each lands on a different host)
hcloud server create --name web-1 --type cx22 --image ubuntu-24.04 --placement-group ha-web
hcloud server create --name web-2 --type cx22 --image ubuntu-24.04 --placement-group ha-web
hcloud server create --name web-3 --type cx22 --image ubuntu-24.04 --placement-group ha-web
```

## Related

- [Server Lifecycle](./server-lifecycle.md) — Creating, listing, and deleting servers
- [Load Balancers](./load-balancers.md) — Distributing traffic across servers in a placement group
