---
sources:
  - "https://pterodactyl.io/project/introduction.html"
  - "https://pterodactyl.io/panel/1.0/getting_started.html"
last_audit_date: 2026-07-29
related_configs:
  - "configs-and-adr/node-main/pterodactyl/"
status: draft
date: 2026-07-29
---

# Pterodactyl Overview

## What is Pterodactyl?

Pterodactyl is a free, open-source (MIT License) game server management platform. It provides a web-based control panel for deploying, managing, and scaling game servers across one or more physical or virtual machines. Each game server runs in an isolated Docker container with resource limits enforced via cgroups.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       PTERODACTYL PANEL                         │
│                    (PHP / Laravel + React)                      │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌─────────────┐  ┌────────────┐  │
│  │ Web UI   │  │ Admin    │  │ API (REST)   │  │ Database   │  │
│  │ (React)  │  │ Dashboard│  │              │  │ (MySQL)    │  │
│  └──────────┘  └──────────┘  └──────┬───────┘  └────────────┘  │
└─────────────────────────────────────┼───────────────────────────┘
                                      │ HTTPS API + WebSocket
                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         WINGS DAEMON                            │
│                    (Go binary per node)                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Docker       │  │ Server      │  │ Console Streaming     │  │
│  │ Management   │  │ Lifecycle   │  │ (WebSocket)           │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────────┘  │
│         │                  │                                     │
│         ▼                  ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Docker Containers (cgroups)                 │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │   │
│  │  │ Server 1│ │ Server 2│ │ Server 3│ │ Server N│ ...  │   │
│  │  │ (Game)  │ │ (Game)  │ │ (Game)  │ │ (Game)  │      │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │   │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Terminology

| Term | Definition |
|------|------------|
| **Panel** | PHP/Laravel web application serving the UI, API, and admin dashboard. Manages users, servers, nodes, and eggs. |
| **Wings** | Go daemon running on each node. Manages Docker containers, server lifecycle, file operations, and console streaming. |
| **Node** | A physical or virtual machine running Wings. Hosts game server containers. |
| **Server** | A single game server instance running inside a Docker container on a node. |
| **Egg** | A configuration template defining how a game server is provisioned. Specifies Docker image, startup command, environment variables, and install script. |
| **Nest** | A grouping of related eggs (e.g., "Minecraft" nest contains Paper, Vanilla, Forge eggs). |
| **Allocation** | An IP:port pair assigned to a server for inbound connections. |
| **Yolks** | Pre-built Docker images maintained by the Pterodactyl project, providing consistent runtime environments for supported games. |

## Supported Games

Pterodactyl ships with official Yolks and eggs for major games, and an extensive community egg ecosystem covers hundreds more.

**Officially supported (via Yolks):**

- Minecraft (Vanilla, Paper, Spigot, Forge, Fabric, CurseForge)
- Rust
- Terraria
- ARK: Survival Evolved
- Counter-Strike 2
- Team Fortress 2
- Garry's Mod
- Valheim
- Factorio

**Community eggs (thousands available):** Palworld, Enshrouded, Satisfactory, V Rising, Project Zomboid, 7 Days to Die, among hundreds of others.

## Egg System

Eggs are the core abstraction for defining how a game server runs. Each egg contains:

| Component | Description |
|-----------|-------------|
| **Docker Image** | The container image hosting the game server binaries and runtime. |
| **Startup Command** | The command and arguments passed to the container entrypoint. Supports variable injection (e.g., `{{SERVER_MEMORY}}`). |
| **Variables** | Environment variables exposed to the end user in the Panel UI. Defined with name, description, default value, rules (validation). |
| **Install Script** | A shell script run during server installation to download and configure game binaries. |
| **Configuration Files** | YAML/JSON/INI templates for auto-generating server config files with injected variables. |

## Panel ↔ Wings Communication

- **REST API (HTTPS):** The Panel sends commands to Wings over HTTPS (create, start, stop, delete, modify allocations, transfer files).
- **WebSocket:** Real-time console output is streamed from Wings to the Panel (and to the user's browser) via a WebSocket connection.
- **Authentication:** Wings authenticates Panel requests using a shared secret token (JWT). Panel verifies Wings responses using SSL/TLS certificates.
- **Heartbeat:** Wings periodically sends heartbeat signals to the Panel reporting server states, resource usage, and health.

## Docker Isolation Model

- **Per-server containers:** Every game server runs in its own Docker container.
- **Resource limits:** CPU shares, memory limits, disk quotas, and I/O priorities are enforced via cgroups and Docker resource constraints.
- **Network isolation:** Each container has a dedicated network namespace. Allocations map host IP:port to container ports.
- **Filesystem isolation:** Server files are mounted into containers via bind mounts from the host filesystem.
- **Security:** Containers run under a restricted user with minimal capabilities. Wings manages the Docker socket — the Panel never has direct Docker access.

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Separate Panel from Wings** | Security boundary — a compromise in the web-facing PHP Panel cannot directly affect the Docker host. Components can be scaled independently. |
| **Panel in PHP/Laravel** | Mature web framework with robust ORM, queue system, and admin UI tooling. Well-suited for a database-driven web control panel. |
| **Wings in Go** | Systems-level language suited for Docker API interaction, filesystem operations, and concurrent server management. Compiles to a single binary with no runtime dependencies. |
| **Docker for isolation** | Industry-standard containerization with cgroup resource enforcement. Eliminates the need for separate VMs per game server. |
| **Egg system as configuration** | Decouples game-specific logic from platform code. New games can be added without modifying Panel or Wings source. |
