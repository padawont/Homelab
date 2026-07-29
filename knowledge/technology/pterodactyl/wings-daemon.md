---
sources:
  - "https://pterodactyl.io/wings/1.0/installing.html"
  - "https://github.com/pterodactyl/wings"
last_audit_date: 2026-07-29
related_configs:
  - "configs-and-adr/node-main/pterodactyl/"
status: draft
date: 2026-07-29
---

# Wings Daemon

## What Wings Is

Wings is the server daemon (backend) for Pterodactyl, written in Go. It runs on each node and handles all server-level operations, acting as the bridge between the Panel and the actual game servers.

## Responsibilities

- **HTTP API for Panel** — Exposes a REST API that the Panel communicates with to issue commands, create/delete servers, and retrieve status.
- **Server Lifecycle** — Starts, stops, restarts, and reinstalls containers.
- **WebSocket Console** — Provides real-time streaming of server console output and accepts command input via WebSocket.
- **Backups** — Creates and manages server backups, optionally compressing and uploading to S3 or other destinations.
- **SFTP Server** — Built-in SFTP server for file management; authenticates users via JWT tokens issued by the Panel.
- **Docker Management** — Spins up and manages Docker containers per-server, applies resource limits via cgroups.
- **Resource Monitoring** — Collects and exposes CPU, memory, disk, and network usage metrics per-server.
- **Crash Detection** — Monitors running containers and detects crashes, optionally restarting servers automatically.

## System Requirements

- Ubuntu 22.04+ (or any Docker-compatible Linux distribution with a kernel that supports cgroups v2 and overlay2)
- Docker Engine (latest stable)
- A Linux user with sudo access

## Docker Installation

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Log out and back in for group changes to take effect. Verify with `docker --version`.

## Wings Binary Installation

1. Download the latest release:

```bash
sudo mkdir -p /etc/pterodactyl
sudo curl -L -o /usr/local/bin/wings "https://github.com/pterodactyl/wings/releases/latest/download/wings_linux_$([[ "$(uname -m)" == "x86_64" ]] && echo "amd64" || echo "arm64")"
```

2. Make it executable:

```bash
sudo chmod +x /usr/local/bin/wings
```

## `config.yml` Structure

```yaml
api:
  host: 0.0.0.0
  port: 8080
  ssl:
    enabled: false
    cert: /etc/letsencrypt/live/node.example.com/fullchain.pem
    key: /etc/letsencrypt/live/node.example.com/privkey.pem

system:
  data: /var/lib/pterodactyl/volumes
  backup: /var/lib/pterodactyl/backups
  timezone: UTC
  sftp:
    bind: 0.0.0.0:2022
    read_only: false
  crash_detection:
    enabled: true
    detect_interval: 60
    max_restarts: 5

docker:
  network:
    interface: 172.18.0.1
    name: pterodactyl_nw
    dns:
      - 1.1.1.1
      - 1.0.0.1
    network_mode: pterodactyl_nw
  container_pid_limit: 512
  installer_limits:
    memory: 1024
    cpu: 100
  tmpfs_size: 100

throttles:
  enabled: true
  lines: 2000
  line_reset_interval: 100
  maximum_trigger_count: 5
  decay_interval: 10000
  stop_grace_period: 15
```

### Key Configuration Sections

| Section | Description |
|---------|-------------|
| `api` | Bind address, port, and optional SSL certificate paths for the Panel-facing HTTP API |
| `system` | Data/log/backup directories, timezone, SFTP bind address, and crash detection settings |
| `docker` | Network interface, DNS, network mode, PID limit, installer resource limits, tmpfs size, and log config |
| `throttles` | Console output throttling — limits lines per interval, trigger count before server stop |

## Systemd Service

Create `/etc/systemd/system/wings.service`:

```ini
[Unit]
Description=Pterodactyl Wings Daemon
After=docker.service
Requires=docker.service

[Service]
User=root
WorkingDirectory=/etc/pterodactyl
LimitNOFILE=4096
ExecStart=/usr/local/bin/wings
Restart=on-failure
RestartSec=5
StartLimitInterval=180
StartLimitBurst=30

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable --now wings
```

## Wings ↔ Panel Communication

- Communication occurs over HTTP/HTTPS on the configured `api.port`.
- All requests are authenticated with **JWT** (JSON Web Tokens).
- The Panel issues two values during node configuration: `token_id` and `token`.
- These are inserted into `config.yml` and used to sign/verify all API requests.
- Wings validates the JWT on every request; the Panel validates that the requesting Wings daemon is trusted.

## Updating Wings

Containers are **not** affected by a Wings restart. Updates follow a zero-downtime pattern:

```bash
sudo systemctl stop wings
sudo curl -L -o /usr/local/bin/wings "https://github.com/pterodactyl/wings/releases/latest/download/wings_linux_amd64"
sudo chmod +x /usr/local/bin/wings
sudo systemctl start wings
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Wings fails to start | Config YAML syntax error | Validate with `yamllint /etc/pterodactyl/config.yml` and check logs |
| Panel returns 401/403 | Token mismatch or invalid JWT | Re-run node configuration from Panel to regenerate tokens |
| Cannot connect to Wings | Port conflict | Ensure nothing else uses port 8080 with `ss -tlnp` |
| SFTP connections fail | Firewall blocking port 2022 | Check `ufw status` or firewall rules |
| Servers crash-loop | Crash detection too aggressive | Adjust `crash_detection.detect_interval` and `max_restarts` |
| Containers have no internet | DNS not reachable | Change DNS from 1.1.1.1 to host's DNS servers in config.yml |
