---
title: "hcloud CLI"
status: draft
author: "refactorartist"
date: 2026-07-11
tags:
  - hetzner
  - hcloud
  - cli
  - cloud
  - infrastructure
sources:
  - url: "https://github.com/hetznercloud/cli"
    title: "hetznercloud/cli — GitHub"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/tutorials/setup-hcloud-cli.md"
    title: "Setup hcloud CLI — Tutorial"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/reference/manual/hcloud.md"
    title: "hcloud CLI Manual — Reference"
  - url: "https://github.com/hetznercloud/cli/blob/main/docs/guides/using-output-options.md"
    title: "Using Output Options — Guide"
  - url: "https://docs.hetzner.cloud/"
    title: "Hetzner Cloud API Documentation"
  - url: "https://docs.hetzner.com/"
    title: "Hetzner Cloud General Documentation"
last_audit_date: 2026-07-11
---

# hcloud CLI

`hcloud` is the official command-line interface for managing Hetzner Cloud resources. It provides full CRUD operations for servers, SSH keys, firewalls, networks, volumes, placement groups, load balancers, images, and more.

## Installation Quickstart

```bash
# macOS / Linux (Homebrew)
brew install hcloud

# Linux (manual binary)
curl -sSLO https://github.com/hetznercloud/cli/releases/latest/download/hcloud-linux-amd64.tar.gz
sudo tar -C /usr/local/bin --no-same-owner -xzf hcloud-linux-amd64.tar.gz hcloud

# Docker
docker run --rm -e HCLOUD_TOKEN="<token>" hetznercloud/cli:latest <command>
```

See [installation-auth.md](./installation-auth.md) for all installation methods.

## Authentication Quickstart

```bash
# Create API token at: Hetzner Console → Project → Security → API Tokens
# Then create a CLI context:
hcloud context create <project-name>
# Verify:
hcloud datacenter list
```

See [installation-auth.md](./installation-auth.md) for context management and multi-project setup.

## Atomic Notes

| Note | Covers |
|---|---|
| [installation-auth.md](./installation-auth.md) | Package managers, direct download, Docker, Go install, API token creation, context management, shell completion |
| [server-lifecycle.md](./server-lifecycle.md) | Server create/list/describe/delete, server types, images, locations, SSH keys, labels, snapshots, power operations |
| [firewall-networking.md](./firewall-networking.md) | Firewall CRUD and rules, network/subnet management, volume attach/detach/resize |
| [placement-groups.md](./placement-groups.md) | Placement group create/delete/list/describe, spread vs strict-spread types |
| [load-balancers.md](./load-balancers.md) | Load balancer create/delete/list/describe, target management, service configuration |
| [scripting.md](./scripting.md) | JSON/YAML/columns output, jq patterns, batch operations, error handling, context automation, API fundamentals |

## Related

- [Kubernetes Knowledge Notes](../../technology/kubernetes/) — K8s fundamentals for cluster provisioning
- [ADR 0008 — Pilot OpenChoreo IDP](../../../adr/0008-pilot-openchoreo-idp/) — Context for Phase 5 Hetzner VM provisioning
