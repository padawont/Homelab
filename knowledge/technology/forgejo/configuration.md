---
title: "Forgejo Configuration"
status: draft
tags:
  - git
  - forge
  - configuration
  - app-ini
  - postgres
  - reverse-proxy
  - ssh
sources:
  - url: "https://forgejo.org/docs/latest/admin/config-cheat-sheet/"
    title: "Forgejo Configuration Cheat Sheet"
  - url: "https://forgejo.org/docs/latest/admin/setup/reverse-proxy/"
    title: "Forgejo Reverse Proxy Setup"
  - url: "https://forgejo.org/docs/latest/admin/setup/recommendations/"
    title: "Forgejo Recommended Settings"
  - url: "https://forgejo.org/docs/latest/admin/installation/database-preparation/"
    title: "Forgejo Database Preparation"
  - url: "https://codeberg.org/forgejo/forgejo/src/branch/forgejo/custom/conf/app.example.ini"
    title: "Forgejo app.example.ini"
last_audit_date: 2026-07-22
related_configs:
  - "configs-and-adr/node-main/kubernetes/forgejo.yaml"
  - "configs-and-adr/node-main/OS/forgejo.nix"
---

# Forgejo Configuration

Forgejo is configured via `app.ini`, located at `custom/conf/app.ini` (or `/etc/forgejo/app.ini` for package installations). In Docker, this file is created automatically if it doesn't exist.

## Configuration via Environment Variables

All `app.ini` values can be set via environment variables using the format:

```
FORGEJO__[SECTION]__[KEY]
```

For example:

```bash
FORGEJO__server__DOMAIN=git.homelab.internal
FORGEJO__database__DB_TYPE=postgres
FORGEJO__database__NAME=forgejo
```

The DEFAULT section uses an empty section name: `FORGEJO____APP_NAME`.

## Key Configuration Sections

### Server

```ini
[server]
PROTOCOL = https
DOMAIN = git.homelab.internal
ROOT_URL = https://git.homelab.internal
HTTP_PORT = 3000
SSH_PORT = 22
START_SSH_SERVER = false
DISABLE_SSH = false
```

- `START_SSH_SERVER = false` delegates SSH to the host system (or K8s NodePort)
- `SSH_PORT` is the port shown in clone URLs

### Database

```ini
[database]
DB_TYPE = postgres
HOST = postgres-service:5432
NAME = forgejo
USER = forgejo
PASSWD = ${FORGEJO_DB_PASSWORD}
SSL_MODE = disable
```

### Session

```ini
[session]
PROVIDER = file
```

### Mailer

```ini
[mailer]
ENABLED = false
```

### Repository

```ini
[repository]
FORCE_PRIVATE = false
DEFAULT_PRIVATE = last
DEFAULT_BRANCH = main
```

### Actions

```ini
[actions]
ENABLED = true
DEFAULT_ACTIONS_URL = https://data.forgejo.org
```

## Database Setup

For PostgreSQL:

1. Create a database and user:
   ```sql
   CREATE DATABASE forgejo;
   CREATE USER forgejo WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE forgejo TO forgejo;
   \c forgejo
   GRANT ALL ON SCHEMA public TO forgejo;
   ```

2. Configure `app.ini` with the connection details.

## Reverse Proxy

When behind a reverse proxy (nginx, Traefik, Caddy), set:

```ini
[server]
PROTOCOL = https
ROOT_URL = https://git.homelab.internal
```

Configure the proxy to forward headers:

```
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header Host $host;
proxy_pass http://forgejo:3000;
```

In K8s, the ingress controller handles TLS termination — Forgejo runs on HTTP internally.

## SSH Modes

### Built-in SSH Server

Set `START_SSH_SERVER = true` and `SSH_LISTEN_PORT = 22`. Forgejo handles SSH connections directly. This is the simplest option.

### System SSH Server

Set `START_SSH_SERVER = false`. Forgejo writes public keys to the system `authorized_keys` file and delegates SSH to the system's sshd. Each key's command forces execution of the Forgejo shell. In K8s, this is impractical — use the built-in SSH server or expose SSH via NodePort.

## Post-Installation Lock

After completing the setup wizard, lock the installation to prevent re-configuration:

```ini
[security]
INSTALL_LOCK = true
```

## Recommended Settings

- Enable `INSTALL_LOCK` after initial setup
- Set `DEFAULT_ACTIONS_URL` to `https://codeberg.org` or `https://data.forgejo.org`
- Use `FORGEJO__` environment variables in Docker/K8s instead of mounting `app.ini`
- Configure `DISABLE_SSH = false` and `START_SSH_SERVER = true` in containers
- Regularly update to the latest patch version in the stable series
