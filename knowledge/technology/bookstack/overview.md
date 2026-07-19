---
title: "BookStack"
status: draft
tags:
  - documentation
  - wiki
  - self-hosted
  - php
sources:
  - url: "https://www.bookstackapp.com/"
    title: "BookStack — Simple & Free Wiki Software"
  - url: "https://github.com/BookStackApp/BookStack"
    title: "BookStack GitHub Mirror"
  - url: "https://hub.docker.com/r/linuxserver/bookstack"
    title: "linuxserver/bookstack Docker Image"
last_audit_date: 2026-07-18
related_configs:
  - "configs/node-main/kubernetes/bookstack.yaml"
---

# BookStack

BookStack is a free, open-source (MIT) wiki and documentation platform built on PHP/Laravel. It provides a simple WYSIWYG interface for organising information into a Books → Chapters → Pages hierarchy.

## Features

- **WYSIWYG + Markdown editor** — switch between visual and markdown editing
- **Books → Chapters → Pages** — simple three-level content hierarchy
- **Full-text search** — search across all content with paragraph-level linking
- **Built-in diagrams.net** — create diagrams directly in the page editor
- **Role-based permissions** — fine-grained access control per role
- **Multi-factor authentication** — TOTP (Google/Microsoft Authenticator, Authy) + backup codes
- **Authentication** — email/password, LDAP, SAML2, OIDC, social providers
- **Multi-lingual** — EN, FR, DE, ES, IT, JA, NL, PL, RU and more
- **Dark/light themes** — user-configurable
- **Page revisions** — full version history with diff view
- **API** — REST API for programmatic access
- **Content export** — export to PDF, HTML, Markdown, plain text

## Deployment Architecture

Deployed on the homelab K3s cluster at `configs/node-main/kubernetes/bookstack.yaml`:

| Component | Image | Purpose |
|---|---|---|
| MariaDB | `mariadb:11` | Database backend (Longhorn PVC, 10Gi) |
| BookStack | `lscr.io/linuxserver/bookstack:latest` | Application server (Longhorn PVC, 5Gi) |

### Networking

- **Service type**: MetalLB LoadBalancer
- **IP**: `192.168.111.102` (from `homelab-pool`: `192.168.111.100-192.168.111.120`)
- **Port**: 80 (HTTP)

### Storage

- `bookstack-db`: Longhorn PVC, 10Gi — MariaDB data directory
- `bookstack-uploads`: Longhorn PVC, 5Gi — uploads, images, backups, themes, logs

### Environment Variables (linuxserver/bookstack)

| Variable | Value | Description |
|---|---|---|
| `APP_URL` | `http://192.168.111.102` | External access URL |
| `DB_HOST` | `mariadb` | Kubernetes service name |
| `DB_PORT` | `3306` | MariaDB port |
| `DB_DATABASE` | `bookstack` | Database name |
| `DB_USERNAME` | `bookstack` | Database user |
| `QUEUE_CONNECTION` | `database` | Async job queue (email, webhooks) |

## Initial Setup

Default admin credentials (change immediately after first login):

- **Email**: `ryanharriszubair@gmail.com`
- **Password**: `runicengines`

Access at [http://192.168.111.102](http://192.168.111.102).

## Administration

- **Settings**: UI at Settings → General (site name, logo, registration)
- **Users**: Settings → Users (create, edit, assign roles)
- **Roles**: Settings → Roles (permissions for each role)
- **Authentication**: Settings → Authentication (LDAP, SAML2, OIDC config)

## Maintenance

### Access container shell

```bash
kubectl exec -n bookstack deploy/bookstack -c bookstack -- /bin/bash
```

### Update APP_URL

```bash
kubectl exec -n bookstack deploy/bookstack -c bookstack -- \
  php /app/www/artisan bookstack:update-url OLD_URL NEW_URL
```

### Backup

MariaDB database and uploads are on separate Longhorn PVCs. Backup by:

1. **Database**: `mysqldump -h mariadb -u bookstack -p bookstack > backup.sql`
2. **Uploads**: Copy `/config` contents from the Longhorn PV

### Upgrade

The `linuxserver/bookstack:latest` tag tracks the latest release. To upgrade:

```bash
kubectl set image -n bookstack deploy/bookstack bookstack=lscr.io/linuxserver/bookstack:latest
```

## Resources

- [BookStack Documentation](https://www.bookstackapp.com/docs/)
- [BookStack GitHub](https://github.com/BookStackApp/BookStack)
- [linuxserver/bookstack Docker Image](https://hub.docker.com/r/linuxserver/bookstack)
- [BookStack Community](https://community.bookstackapp.com/)
