---
adr: 4
title: "Adopt Pterodactyl for Game Server Management"
author: padawont
status: proposed
topic: game-server
date: 2026-07-29
date-proposed: 2026-07-29
history: "2026-07-29: Created"
related_knowledge:
  - knowledge/technology/pterodactyl/
related_configs:
  - configs-and-adr/node-main/pterodactyl/
  - configs-and-adr/node-main/vm/
  - configs-and-adr/node-main/vm/harvester-config.yaml
---

# ADR 0004 — Adopt Pterodactyl for Game Server Management

## Context

The homelab hosts game servers for friends and family (Minecraft, Terraria, Valheim, etc.). Currently there is no centralized management — each game server must be SSH'd into directly, configured manually, and monitored via terminal. This is error-prone, time-consuming, and gives users no self-service ability to start/stop or manage their own servers.

Game server requirements:
- Minecraft (Java + Bedrock), Terraria, Valheim, and potentially other games
- Per-server resource isolation (one game should not starve another)
- User self-service: friends should be able to restart their own servers without SSH access
- Backup automation per-server
- Web-based UI for status, logs, and file management

The panel must run inside a Harvester VM on node-main (see ADR 0003) with limited resources: 4 vCPU, 6 GB RAM, 50 GB disk.

## Decision

Use **Pterodactyl** as the game server management platform, running Panel + Wings on the same Harvester VM (192.168.111.52).

Pterodactyl is chosen over alternatives because:

- **Docker-native isolation** — each game server runs in its own container with cgroup resource limits. No other free panel provides this level of isolation.
- **Huge egg ecosystem** — 100+ community-maintained game templates available out of the box.
- **Proven maturity** — the dominant open-source panel with the largest community and ecosystem.
- **MIT license** — no restrictions, no licensing costs.
- **REST API + WebSocket** — provides a fully programmable interface for automation and monitoring.
- **Built-in SFTP** — users get file access without SSH credentials.

Accepted trade-offs:
- Higher setup complexity vs Crafty Controller (PHP + MariaDB + Redis + Go stack)
- No in-game state tracking (vs AMP which knows player counts)
- Requires Docker — the VM must support Docker containers
- No Windows support (irrelevant — this is a Linux homelab)

### Configuration

| Parameter | Value |
|---|---|
| Panel URL | https://192.168.111.52:443 (or pterodactyl.homelab.local) |
| Wings API | 127.0.0.1:8080 (localhost only) |
| Wings SFTP | 0.0.0.0:2022 |
| Database | MariaDB on localhost |
| Queue | Redis on localhost |
| Web server | Nginx + PHP 8.3 FPM |
| SSL | Self-signed or Let's Encrypt |
| Docker network | pterodactyl_nw (172.18.0.0/16) |

## Consequences

**Positive:**
- Game server provisioning becomes a few clicks in a web UI
- Resource isolation via Docker cgroups prevents noisy neighbors
- User self-service: friends can restart, view logs, manage files via SFTP
- Backup automation per-server with configurable schedules
- REST API enables future automation (CI/CD, Discord bot integration)
- Large egg library means easy addition of new games
- Panel + Wings on one VM keeps architecture simple

**Negative:**
- Higher resource overhead than manual Docker Compose setup (~500 MB RAM for Panel stack)
- Requires ongoing maintenance: Panel migrations, Wings updates, OS patches
- Single VM is a single point of failure for all game servers
- Panel and Wings share the same VM — a Panel compromise could impact Wings (mitigated by Wings API on localhost only)
- The PHP stack (MariaDB + Redis + Nginx + PHP-FPM) adds complexity for updates and debugging

## Alternatives Considered

### Pelican Panel
- **Pros**: Active development (Pterodactyl fork), OAuth support, SQLite option, migration tool from Pterodactyl, backward-compatible with Pterodactyl eggs
- **Cons**: AGPL license, smaller community, less battle-tested. Best if Pterodactyl stagnates further. Worth revisiting for future upgrades.

### AMP (CubeCoders)
- **Pros**: In-game state tracking (knows player count), simpler install, Windows support, OIDC SSO, commercial support
- **Cons**: Paid ($10-$40 lifetime), closed source, instance limits, smaller game library vs Pterodactyl eggs. Overkill and cost-prohibitive for a small homelab.

### Crafty Controller
- **Pros**: Simple single-container setup, Minecraft-specific features (world manager, mod installer)
- **Cons**: Minecraft only, no Docker isolation per server (JVM-level only), smaller community. Unsuitable for multi-game requirements.

### Manual Docker Compose
- **Pros**: Zero panel overhead, maximum control, no maintenance burden from panel software
- **Cons**: No web UI, no user self-service, no built-in backup scheduling, no API, every server requires SSH. Does not scale to multiple users or games.

## Related Decisions

- **ADR 0003** (Harvester VM Platform) — Pterodactyl runs as a VM on Harvester
- **ADR 0001** (4-Phase Pipeline) — this ADR is tracked through the knowledge → configs → deployment pipeline
