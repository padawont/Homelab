---
title: "Forgejo Installation"
status: draft
tags:
  - git
  - forge
  - installation
  - docker
  - kubernetes
  - nixos
sources:
  - url: "https://forgejo.org/docs/latest/admin/installation/"
    title: "Forgejo Installation Guide"
  - url: "https://forgejo.org/docs/latest/admin/installation/docker/"
    title: "Forgejo Docker Installation"
  - url: "https://forgejo.org/docs/latest/admin/installation/binary/"
    title: "Forgejo Binary Installation"
  - url: "https://forgejo.org/docs/latest/admin/installation/database-preparation/"
    title: "Forgejo Database Preparation"
  - url: "https://codeberg.org/forgejo-contrib/delightful-forgejo"
    title: "Delightful Forgejo — Community Install Options"
last_audit_date: 2026-07-22
related_configs:
  - "configs-and-adr/node-main/kubernetes/forgejo.yaml"
---

# Forgejo Installation

Forgejo can be installed via Docker, binary download, NixOS module, or K8s manifests. All methods share the same configuration via `app.ini`.

## Docker / Podman

The official container image is `codeberg.org/forgejo/forgejo:16` (or `data.forgejo.org` as mirror).

```
docker pull codeberg.org/forgejo/forgejo:16
```

### Docker Compose

```yaml
networks:
  forgejo:
    external: false

services:
  server:
    image: codeberg.org/forgejo/forgejo:16
    container_name: forgejo
    environment:
      - USER_UID=1000
      - USER_GID=1000
    restart: always
    networks:
      - forgejo
    volumes:
      - ./forgejo:/data
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "3000:3000"
      - "222:22"
```

### With PostgreSQL Database

Add environment variables to configure the database connection:

```yaml
environment:
  - FORGEJO__database__DB_TYPE=postgres
  - FORGEJO__database__HOST=db:5432
  - FORGEJO__database__NAME=forgejo
  - FORGEJO__database__USER=forgejo
  - FORGEJO__database__PASSWD=forgejo
```

And add a `db` service (postgres:14) with a volume for data persistence.

### Rootless Image

Forgejo provides a `-rootless` variant (`codeberg.org/forgejo/forgejo:16-rootless`) that runs without root privileges. The data path changes to `/var/lib/gitea` and SSH port shifts to 2222.

## Binary Installation

1. Download the binary from [codeberg.org/forgejo/forgejo/releases](https://codeberg.org/forgejo/forgejo/releases)
2. Make executable: `chmod +x forgejo`
3. Create a dedicated system user: `sudo adduser --system --group forgejo`
4. Create directory structure: `/etc/forgejo`, `/var/lib/forgejo`
5. Run: `sudo -u forgejo ./forgejo web --config /etc/forgejo/app.ini`

## NixOS

Forgejo is available as a NixOS module. Enable it in `configuration.nix`:

```nix
services.forgejo = {
  enable = true;
  settings = {
    server = {
      DOMAIN = "git.example.com";
      ROOT_URL = "https://git.example.com";
      HTTP_PORT = 3000;
    };
    database = {
      DB_TYPE = "postgres";
      HOST = "/run/postgresql";
      NAME = "forgejo";
      USER = "forgejo";
    };
  };
};
```

## Kubernetes

Forgejo can be deployed on Kubernetes via:

1. **Raw manifests** — Namespace, Deployment, Service, PVC, Ingress (see `configs-and-adr/node-main/kubernetes/forgejo.yaml`)
2. **Helm chart** — Community Helm charts are available

The container image `codeberg.org/forgejo/forgejo:16` runs on port 3000. Configure the database via environment variables using the `FORGEJO__[SECTION]__[KEY]` pattern.

## Database Setup

Forgejo supports three database backends:

| Database | When to Use |
|---|---|
| SQLite | Single-user, simplest setup, no external dependency |
| PostgreSQL | Multi-user, production, better concurrency |
| MySQL/MariaDB | Compatible alternative to Postgres |

For the homelab deployment, Forgejo connects to an existing in-cluster Postgres instance. The database must be created before Forgejo starts (see Database Preparation guide).
