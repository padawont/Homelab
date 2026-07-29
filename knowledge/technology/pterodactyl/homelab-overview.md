---
sources:
  - "https://pterodactyl.io/project/introduction.html"
last_audit_date: 2026-07-29
related_configs:
  - "configs-and-adr/node-main/pterodactyl/"
  - "configs-and-adr/node-main/vm/harvester-config.yaml"
status: draft
date: 2026-07-29
related_knowledge:
  - "knowledge/kubernetes/harvester/"
---

# Pterodactyl Homelab Overview

## Host Infrastructure

- **Hypervisor:** node-main — single physical server running Harvester HCI v1.8
- **Harvester VIP:** 192.168.111.51
- **Cluster:** Single-node Harvester (no HA, no live migration)

## Network

| Parameter | Value |
|-----------|-------|
| Subnet | 192.168.111.0/24 |
| Gateway | 192.168.111.1 |
| VLAN | Flat (no VLAN tagging) |

## Pterodactyl VM

| Property | Value |
|----------|-------|
| VM Name | `pterodactyl` |
| OS | Ubuntu Server 22.04 LTS |
| vCPU | 4 cores |
| RAM | 6 GB |
| Disk | 50 GB thin-provisioned Longhorn |
| Static IP | 192.168.111.52/24 |
| Architecture | Panel + Wings on the same VM |

## Services & Endpoints

| Service | Binding | Notes |
|---------|---------|-------|
| Panel (Nginx) | `0.0.0.0:443` | HTTPS — users browse here |
| Wings API | `127.0.0.1:8080` | Localhost only — Panel ↔ Wings internal comms |
| Wings SFTP | `0.0.0.0:2022` | External — users upload files |
| SSH | `0.0.0.0:22` | VM management |

## Port Plan

| Port(s) | Purpose | Access |
|---------|---------|--------|
| 22 | SSH | External |
| 443 | Pterodactyl Panel HTTPS | External |
| 2022 | Wings SFTP | External |
| 8080 | Wings API | Internal (localhost only) |
| 25565 | Minecraft Java | Game |
| 19132 | Minecraft Bedrock | Game |
| 7777 | Terraria / Satisfactory | Game |
| 27015 | Source/Valve games | Game |
| 28015 | Rust | Game |
| 8211 | Palworld | Game |
| 16261 | Project Zomboid | Game |

## Firewall (UFW)

```bash
ufw allow 22/tcp        # SSH
ufw allow 443/tcp       # Panel HTTPS
ufw allow 2022/tcp      # Wings SFTP
ufw deny 8080/tcp       # Block Wings API from external
ufw default deny incoming
ufw default allow outgoing
```

## Backup Strategy

### Daily VM Snapshots (Harvester)
- **Schedule:** Daily at 03:00
- **Retention:** 7 snapshots
- **Type:** Crash-consistent VM snapshot
- **Storage:** Local Longhorn

### Weekly NFS Backups
- **Schedule:** Weekly Sunday at 04:00
- **Retention:** 4 backups
- **Target:** NFS share (external, configured in Harvester Settings)
- **Content:** Full VM backup via Harvester backup target

**Pre-snapshot requirement:** Configure `dhcp-identifier: mac` in Ubuntu's netplan before first snapshot to prevent IP conflict on restore.

## Wings Configuration Notes

- `api.host` set to `127.0.0.1:8080` — prevents external access to Wings API
- `sftp.bind` set to `0.0.0.0:2022` — accessible from LAN
- Game server allocations use dynamic port mapping
- Data directories: `/etc/pterodactyl` (config) and `/var/lib/pterodactyl` (volumes)
- Docker DNS: use host DNS (192.168.111.1) instead of Cloudflare defaults

## Related

- Harvester cluster configuration: `configs-and-adr/node-main/vm/harvester-config.yaml`
- Pterodactyl service definitions: `configs-and-adr/node-main/pterodactyl/`
- Harvester knowledge: `knowledge/kubernetes/harvester/`
