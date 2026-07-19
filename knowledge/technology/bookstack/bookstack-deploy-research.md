# Research: BookStack Deployment on Homelab K3s

## Overview

BookStack is a free, open-source (MIT) wiki/documentation platform built on PHP/Laravel.
Source managed on Codeberg: https://codeberg.org/bookstack/bookstack
Website: https://www.bookstackapp.com/

## Key Features

- WYSIWYG + Markdown editor
- Books → Chapters → Pages hierarchy
- Full-text search with paragraph-level linking
- Built-in diagrams.net drawing
- Role-based permissions system
- LDAP/SAML2/OIDC authentication
- Multi-factor authentication (TOTP)
- Dark/light themes
- Multi-lingual (EN, FR, DE, ES, IT, JA, NL, PL, RU, more)
- Page revisions and image management
- Cross-book sorting
- API access

## Deployment Architecture

### Docker Image: linuxserver/bookstack
- Image: `lscr.io/linuxserver/bookstack:latest`
- Internal port: 80
- Config path: /config (persists .env, uploads, logs, backups)
- Requires MariaDB database

### Database: MariaDB
- Image: `mariadb:11`
- Port: 3306
- Storage: Longhorn PVC (10Gi)

### Database Credentials
- Root password: bookstack_root_pw
- Database name: bookstack
- Database user: bookstack
- Database password: bookstack_user_pw

### Environment Variables (linuxserver/bookstack)
| Variable | Required | Description |
|---|---|---|
| APP_URL | Yes | Protocol + IP/URL + port (e.g. http://192.168.111.102) |
| APP_KEY | Yes | Session encryption key (32-char base64) |
| DB_HOST | Yes | MariaDB hostname |
| DB_PORT | Yes | MariaDB port (3306) |
| DB_USERNAME | Yes | Database user |
| DB_PASSWORD | Yes | Database password |
| DB_DATABASE | Yes | Database name |
| QUEUE_CONNECTION | No | Set to "database" for async actions |
| PUID | No | User ID (default 1000) |
| PGID | No | Group ID (default 1000) |
| TZ | No | Timezone |

### Default Login
- Email: admin@admin.com
- Password: password

### MetalLB IP Pool
- Pool name: homelab-pool
- Range: 192.168.111.100-192.168.111.120
- Used: 192.168.111.100 (Rancher), 192.168.111.101 (Kiwix)
- Allocated for BookStack: 192.168.111.102

### Cluster Details
- Node: node-1 (192.168.111.10)
- K3s version: v1.35.5+k3s1
- Storage: Longhorn (default StorageClass)
- LoadBalancer: MetalLB (FRR mode)
- Cert-Manager: installed (for future HTTPS)

### Existing Deployment Pattern (kiwix.yaml)
Single YAML file with:
1. Namespace
2. PersistentVolumeClaim (Longhorn)
3. Deployment
4. Service (LoadBalancer type)

## Definition of Done

1. BookStack accessible via HTTP at 192.168.111.102
2. MariaDB + BookStack pods running in bookstack namespace
3. Persistent storage via Longhorn PVCs
4. Default admin login works (admin@admin.com / password)
5. Page creation and file upload functional
6. K8s manifest committed to repo at configs/node-main/kubernetes/bookstack.yaml
7. Knowledge entry created at knowledge/technology/bookstack/

## Sources
- https://www.bookstackapp.com/ - Home page
- https://www.bookstackapp.com/docs/ - Documentation
- https://github.com/BookStackApp/BookStack - GitHub mirror
- https://hub.docker.com/r/linuxserver/bookstack - Docker image
- https://github.com/linuxserver/docker-bookstack - Docker image source
