---
sources:
  - "https://eggs.pterodactyl.io"
  - "https://github.com/pterodactyl/game-eggs"
last_audit_date: 2026-07-29
related_configs:
  - "configs-and-adr/node-main/pterodactyl/"
status: draft
date: 2026-07-29
---

# Eggs & Nests

## Overview

- **Egg** — A JSON configuration template that defines how a server is provisioned, installed, and run. Every server in Pterodactyl is created from an egg.
- **Nest** — A logical grouping of related eggs (e.g., "Minecraft", "SteamCMD games"). Nests are purely organizational and have no runtime effect.

## Egg Format (PTDL_v2)

The canonical egg schema uses the key `PTDL_v2` at the root. Top-level fields:

| Field | Description |
|-------|-------------|
| `meta` | Internal version / schema info |
| `name` | Human-readable egg name |
| `author` | Email or identifier of the creator |
| `description` | Brief summary |
| `features` | Array of feature flags (e.g. `["eula"]`) |
| `docker_images` | Map of image labels to Docker image URIs (see Yolks below) |
| `startup` | Startup command with `{{variable}}` placeholders |
| `config` | Logs, file parsing, stop command, and port mapping overrides |
| `scripts.installation` | Script that runs during server install (bash by default) |
| `variables` | Array of user-configurable variables (see below) |
| `file_denylist` | Array of file extensions / names that users cannot access via the file manager |

### Variable Fields

Each entry in `variables`:

| Field | Description |
|-------|-------------|
| `name` | Display name |
| `description` | Help text shown to the user |
| `env_variable` | Environment variable name injected into the container |
| `default_value` | Fallback if the user provides none |
| `user_viewable` | Boolean — visible to the end user |
| `user_editable` | Boolean — can the end user change this? |
| `rules` | Laravel validation rules (e.g. `required|string|max:20`) |
| `field_type` | UI hint: `text`, `select`, `boolean` |

Variables are injected as environment variables at container runtime.

## Official Egg Repository

- **Repo**: [github.com/pterodactyl/game-eggs](https://github.com/pterodactyl/game-eggs)
- Contains **100+ eggs** organised by nest.
- Nest layout:
  ```
  game-eggs/
    minecraft/
      paper/
        egg-paper.json
        README.md
      fabric/
        egg-fabric.json
      ...
    steamcmd/
      rust/
        egg-rust.json
      ...
  ```

### Available Games (partial list)

| Category | Games |
|----------|-------|
| Minecraft Java | Paper, Fabric, Forge, CurseForge, Technic, Vanilla |
| Minecraft Bedrock | PocketMine-MP, Nukkit, PowerNukkitX |
| Survival/Open World | Rust, Terraria, ARK, Valheim, Factorio, 7 Days to Die, Palworld, Enshrouded, Valheim |
| FPS | CS2, TF2, Garry's Mod, Left 4 Dead 2, Half-Life 2 DM, DayZ, Insurgency |
| RPG/MMO | Mount & Blade II, Neverwinter Nights, Path of Titans |
| Racing | Assetto Corsa, BeamNG.drive |
| Other | Among Us (Impostor), FiveM, GTA:SA-MP, Foundry VTT, Teamspeak, Mumble |

## Creating & Importing Eggs

**Via Panel UI:**
1. Admin Panel → Nests → Create New Egg
2. Set name, description, author
3. Define Docker images from yolks
4. Write startup command with `{{variable}}` placeholders
5. Add installation script
6. Define variables with validation rules
7. Export as JSON when done

**Via JSON import:**
1. Download `egg-*.json` from the [game-eggs](https://github.com/pterodactyl/game-eggs) repo
2. Admin Panel → Nests → Import Egg
3. Upload the JSON file

## Yolks Docker Images

All official eggs reference images from the [Yolks](https://github.com/pterodactyl/yolks) project hosted under `ghcr.io/pterodactyl/yolks`:

| Category | Images |
|----------|--------|
| Java | `java:8`, `java:11`, `java:16`, `java:17`, `java:21`, `java:24`, `java:25` |
| Node.js | `nodejs:18`, `nodejs:20`, `nodejs:22` |
| Python | `python:3.10`, `python:3.11`, `python:3.12` |
| Go | `go:1.22`, `go:1.24`, `go:1.26` |
| Game-specific | `games:rust`, `games:source`, `games:conan_exiles` |
| Installer | `installers:alpine`, `installers:debian` |

## Key Details

- Startup command variables use `{{ }}` double-brace syntax (e.g. `{{SERVER_JARFILE}}`).
- The `scripts.installation` field contains a bash script that runs inside the installer image.
- `file_denylist` blocks file access in the Panel file manager (not at the OS level).
- Laravel validation rules support `required`, `regex`, `min`, `max`, `in:...`, `string`, `integer`, `boolean`.
- Docker images support both `linux/amd64` and `linux/arm64` architectures.
