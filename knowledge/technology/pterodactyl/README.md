---
status: draft
date: 2026-07-29
title: "Pterodactyl — Game Server Management"
related_configs:
  - "configs-and-adr/node-main/pterodactyl/"
---

# Pterodactyl Knowledge Notes

Pterodactyl is an open-source game server management platform (MIT License). It provides a web-based control panel for deploying, managing, and scaling game servers in isolated Docker containers.

## Architecture Overview

```
Panel (PHP/Laravel + React) ←──HTTPS API + WebSocket──→ Wings (Go daemon)
                                                              │
                                                        Docker containers
                                                    (game servers per container)
```

## Notes Index

| Note | Description |
|------|-------------|
| [Overview](overview.md) | Architecture, terminology, supported games, key design decisions |
| [Panel Installation](panel-installation.md) | Ubuntu 22.04 LTS step-by-step install guide |
| [Webserver Configuration](webserver-configuration.md) | Nginx, Apache, Caddy configs, SSL, security headers |
| [Wings Daemon](wings-daemon.md) | Go daemon installation, config.yml, systemd, troubleshooting |
| [Eggs & Nests](eggs-and-nests.md) | Egg format, PTDL_v2 schema, official/community eggs, Yolks images |
| [API Integration](api-integration.md) | Client vs Application API, endpoints, WebSocket console, rate limits |
| [Operations & Maintenance](operations-and-maintenance.md) | Backup, updates, monitoring, troubleshooting, security, performance |
| [Homelab Overview](homelab-overview.md) | Deployment plan for this homelab (Harvester VM on node-main) |

## Deployment in This Homelab

Pterodactyl runs inside a Harvester VM on node-main (192.168.111.52/24). See [homelab-overview.md](homelab-overview.md) for the full deployment plan, and `configs-and-adr/node-main/pterodactyl/` for configuration.

## Related Configurations

- ADR 0004: Pterodactyl game server adoption (TBD)
- `configs-and-adr/node-main/pterodactyl/` — VM config, K8s manifests, OS config
- `configs-and-adr/node-main/vm/harvester-config.yaml` — underlying VM infrastructure
