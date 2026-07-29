---
related_knowledge:
  - knowledge/technology/pterodactyl/
  - knowledge/kubernetes/harvester/
related_configs:
  - configs-and-adr/adr/0004-pterodactyl-game-server.md
  - configs-and-adr/node-main/vm/
---

# Pterodactyl — node-main

This directory contains Pterodactyl game server management configuration for node-main. Pterodactyl runs inside a Harvester VM on node-main hosting both the Panel and Wings daemon.

## VM Specs

| Attribute | Value |
|---|---|
| VM Name | `pterodactyl` |
| OS | Ubuntu Server 22.04 LTS |
| vCPU | 4 cores |
| RAM | 6 GB |
| Disk | 50 GB thin-provisioned Longhorn |
| IP | 192.168.111.52/24 |
| Harvester VIP | 192.168.111.51 |

## Services

- **Pterodactyl Panel** — Web UI, API, admin dashboard (Nginx + PHP 8.3 FPM)
- **MariaDB** — Panel database
- **Redis** — Queue and cache backend
- **Wings** — Game server daemon (Go)
- **Docker** — Container runtime for game servers

## Port Plan

| Port | Service | Bind |
|------|---------|------|
| 443 | Panel (HTTPS) | 0.0.0.0 |
| 2022 | Wings SFTP | 0.0.0.0 |
| 8080 | Wings API (internal) | 127.0.0.1 |
| 25565 | Minecraft Java | Game |
| 19132 | Minecraft Bedrock | Game |
| 7777 | Terraria | Game |
| 2456 | Valheim | Game |

## Directory Layout

| Directory | Purpose |
|---|---|
| `kubernetes/` | Pterodactyl K8s manifests (future — if migrated to K8s) |
| `OS/` | OS-level configuration for the Pterodactyl VM |
