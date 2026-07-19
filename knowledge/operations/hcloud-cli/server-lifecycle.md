---
title: "Server Lifecycle"
status: draft
author: "refactorartist"
date: 2026-07-11
tags:
  - hetzner
  - hcloud
  - server
  - lifecycle
  - ssh-keys
  - images
  - snapshots
sources:
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_server_create.md"
    title: "hcloud server create — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_server_list.md"
    title: "hcloud server list — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_server_create-image.md"
    title: "hcloud server create-image — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_image_list.md"
    title: "hcloud image list — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_ssh-key_create.md"
    title: "hcloud ssh-key create — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_server-type.md"
    title: "hcloud server-type — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_location.md"
    title: "hcloud location — Reference"
  - url: "https://docs.hetzner.cloud/"
    title: "Hetzner Cloud API Documentation"
last_audit_date: 2026-07-11
---

# Server Lifecycle

## Server Types

List available server types to find the right specification for your workload:

```bash
hcloud server-type list
hcloud server-type describe cx22
```

Common server type series:
- **CX** — Shared vCPU (CPX: AMD, CAX: ARM)
- **CCX** — Dedicated vCPU
- **RX** — Shared vCPU with high RAM (memory-optimized)

## Locations

List available datacenter locations:

```bash
hcloud location list
hcloud location describe nbg1
```

Available locations: `nbg1` (Nuremberg), `fsn1` (Falkenstein), `hel1` (Helsinki), `ash` (Ashburn), `hil` (Hillsboro), `sin` (Singapore)

## Images

List available operating system and application images:

```bash
# List all system images
hcloud image list

# Filter by type
hcloud image list -t system       # OS images (Ubuntu, Fedora, Debian, etc.)
hcloud image list -t app          # Application images (WordPress, Docker, etc.)
hcloud image list -t snapshot     # Custom snapshots
hcloud image list -t backup       # Automatic backups

# Filter by architecture
hcloud image list -a x86          # x86_64 images
hcloud image list -a arm          # ARM images (for CAX server types)

# Filter by label
hcloud image list -l env=production

# Describe or delete an image
hcloud image describe <image>
hcloud image delete <image>
```

Source: [hcloud image list](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_image_list.md)

## SSH Keys

Upload and manage SSH public keys for server access:

```bash
# Add SSH key from file
hcloud ssh-key create --name my-key --public-key-from-file ~/.ssh/id_rsa.pub

# Add SSH key from inline string
hcloud ssh-key create --name my-key --public-key "<key>"

# List, describe, delete keys
hcloud ssh-key list
hcloud ssh-key describe <ssh-key>
hcloud ssh-key delete <ssh-key>

# Update key metadata
hcloud ssh-key update <ssh-key>
hcloud ssh-key add-label <ssh-key> env=prod
hcloud ssh-key remove-label <ssh-key> <label-key>
```

Source: [hcloud ssh-key create](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_ssh-key_create.md)

## Creating Servers

### Basic Creation

```bash
hcloud server create --name my-server --type cx22 --image ubuntu-24.04
```

### With Location, SSH Key, and Labels

```bash
hcloud server create \
  --name my-server \
  --type cx22 \
  --image ubuntu-24.04 \
  --location nbg1 \
  --ssh-key my-key \
  --label env=prod \
  --label team=platform
```

### With Firewall, Network, and Volume (attached on creation)

```bash
hcloud server create \
  --name my-server \
  --type cx22 \
  --image ubuntu-24.04 \
  --location nbg1 \
  --ssh-key my-key \
  --firewall my-firewall \
  --network my-network \
  --volume my-volume
```

### With Placement Group and Protection

```bash
hcloud server create \
  --name my-server \
  --type cx22 \
  --image ubuntu-24.04 \
  --placement-group my-group \
  --enable-protection delete,rebuild \
  --start-after-create false
```

### Network and IP Configuration

```bash
# Attach to a network with a specific IP
hcloud server create --name my-server --type cx22 --image ubuntu-24.04 --network my-network

# Use specific primary IPs
hcloud server create --name my-server --type cx22 --image ubuntu-24.04 --primary-ipv4 <id> --primary-ipv6 <id>

# Create without IPv4
hcloud server create --name my-server --type cx22 --image ubuntu-24.04 --without-ipv4
```

Source: [hcloud server create](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_server_create.md)

## Listing and Describing Servers

```bash
# List all servers
hcloud server list

# Filter by status
hcloud server list --status running
hcloud server list --status off

# Filter by label selector
hcloud server list -l env=prod

# Sort by field
hcloud server list -s name:asc
hcloud server list -s created:desc

# Output formats
hcloud server list -o json
hcloud server list -o yaml
hcloud server list -o columns=id,name,status,ipv4

# Describe a specific server
hcloud server describe my-server
```

Source: [hcloud server list](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_server_list.md)

## Server Operations

```bash
# Power management
hcloud server poweron <server>
hcloud server poweroff <server>
hcloud server reboot <server>
hcloud server shutdown <server>     # Graceful shutdown
hcloud server reset <server>        # Hard reboot

# Access
hcloud server ssh <server>          # Spawn SSH connection
hcloud server ip <server>           # Print IP address
hcloud server reset-password <server>

# Rescue mode
hcloud server enable-rescue <server>
hcloud server disable-rescue <server>

# Console
hcloud server request-console <server>

# Change type (scale up/down)
hcloud server change-type <server>

# Rebuild from image
hcloud server rebuild <server>

# Backups
hcloud server enable-backup <server>
hcloud server disable-backup <server>

# Labels
hcloud server add-label --label env=prod <server>
hcloud server remove-label <server> <label-key>

# Network attachment
hcloud server attach-to-network --network <network> <server>
hcloud server detach-from-network <server>

# Placement groups
hcloud server add-to-placement-group --placement-group <group> <server>
hcloud server remove-from-placement-group <server>

# Update metadata
hcloud server update <server>
```

## Snapshots and Backups

### Creating Snapshots

```bash
# Create a snapshot image from a server
hcloud server create-image --type snapshot <server>

# With description and labels
hcloud server create-image --type snapshot --description "Pre-update snapshot" --label env=prod <server>
```

Source: [hcloud server create-image](https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud_server_create-image.md)

### Using Snapshots as Server Image Sources

```bash
# List snapshots
hcloud image list -t snapshot

# Create a new server from a snapshot
hcloud server create --name my-server --type cx22 --image <snapshot-id-or-name>
```

### Backup Management

```bash
# Enable automatic daily backups
hcloud server enable-backup <server>

# Disable backups
hcloud server disable-backup <server>
```

## Deleting Servers

```bash
# Delete a server (will also detach volumes, release floating IPs, etc.)
hcloud server delete <server>

# Batch delete with label selector
hcloud server list -l env=staging -o noheader -o columns=id | xargs -n1 hcloud server delete
```

## Server Lifecycle Summary

```
Create ──► Running ──► (poweroff/reset/reboot) ──► Delete
  │            │
  └── Snapshots     └── Describe / List
```

## Related

- [Firewall & Networking](./firewall-networking.md) — Firewall and network attachment
- [Placement Groups](./placement-groups.md) — Server distribution policies
- [Load Balancers](./load-balancers.md) — Traffic distribution to servers
- [Scripting](./scripting.md) — Automating server lifecycle operations
