---
title: "Installing and configuring Forgejo"
status: draft
author: "padawont"
date: 2026-08-23
tags: [forgejo, kubernetes, helm, ingress, storage, configuration]
sources:
  - url: "https://forgejo.org/docs/latest/admin/installation/"
    title: "Forgejo installation guide"
  - url: "https://forgejo.org/docs/latest/admin/installation/docker/"
    title: "Forgejo installation with Docker"
  - url: "https://forgejo.org/docs/latest/admin/config-cheat-sheet/"
    title: "Forgejo configuration cheat sheet"
  - url: "https://forgejo.org/docs/latest/admin/setup/storage/"
    title: "Forgejo storage settings"
last_audit_date: 2026-08-25
related_docs:
  - "./02_Knowledge/technologies/services/forgejo/overview.md"
  - "./02_Knowledge/technologies/services/forgejo/operations.md"
  - "./02_Knowledge/technologies/services/forgejo/security.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/ingress.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/storage.md"
---

# Installing and configuring Forgejo

## Overview

Forgejo ships as a container image (`codeberg.org/forgejo/forgejo`) or a binary
distribution. On k3s it deploys as a Deployment with a Longhorn PVC, a Service
(`forgejo-http`, port 3000), and a Traefik Ingress at `git.homelab.local`.
Configuration lives in `app.ini` (created by the image on first start) and can
be overridden via `FORGEJO__[SECTION]__[KEY]` env vars.

> Not deployed yet — all manifests below are **Example — abstract**, not live config.

## Details

### Container image

```bash
docker pull codeberg.org/forgejo/forgejo:16
```

- The `16` tag tracks the latest minor release of the v16 line; `16.0` tracks
  the latest patch. Swap `codeberg.org` for the mirror `data.forgejo.org`.
- Rootless variant: `...:16-rootless` (data dir `/var/lib/gitea`, UID/GID 1000).
- Note: the `:16-rootless` variant stores data under `/var/lib/gitea`, so if you switch from the standard image you must change the volume mount from `/data` to `/var/lib/gitea` (the `/data` mountPath in the manifest below is correct for the non-rootless `:16` image).

### k3s deployment

Example — abstract (raw manifests; a Helm chart wraps the same primitives):

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: forgejo-data
  namespace: forgejo
spec:
  storageClassName: longhorn
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 20Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: forgejo
  namespace: forgejo
spec:
  replicas: 1
  selector: { matchLabels: { app: forgejo } }
  template:
    metadata:
      labels: { app: forgejo }
    spec:
      containers:
        - name: forgejo
          image: codeberg.org/forgejo/forgejo:16
          ports:
            - containerPort: 3000   # web UI + git HTTP
            - containerPort: 22     # git over SSH
          volumeMounts:
            - { name: data, mountPath: /data }
          env:
            - { name: FORGEJO__server__ROOT_URL, value: "https://git.homelab.local/" }
      volumes:
        - name: data
          persistentVolumeClaim: { claimName: forgejo-data }
---
apiVersion: v1
kind: Service
metadata:
  name: forgejo-http
  namespace: forgejo
spec:
  selector: { app: forgejo }
  ports:
    - { name: http, port: 3000, targetPort: 3000 }
```

The Ingress is the `forgejo-ingress` resource shown in
`./02_Knowledge/technologies/kubernetes/concepts/ingress.md` — Traefik routes
`git.homelab.local` to `forgejo-http:3000` and terminates HTTPS there.

### Configuration (`app.ini` and env vars)

| Setting | Purpose |
|---|---|
| `[server] DOMAIN` / `ROOT_URL` | Hostname and external URL — `ROOT_URL` should be `https://git.homelab.local/` |
| `[server] SSH_PORT` | Port for git-over-SSH (e.g. `22` or `2222` behind a host mapping) |
| `[database] DB_TYPE` | `sqlite3` (default), `mysql`, or `postgres` |
| `[service] DISABLE_REGISTRATION` | Block public sign-up (see the security note) |
| `[actions]` | Enable/disable Forgejo Actions |
| `[security] SECRET_KEY` | Instance secret; generate a random value on first install |

Every key maps to `FORGEJO__[SECTION]__[KEY]`, e.g.
`FORGEJO__server__ROOT_URL=https://git.homelab.local/`; values can only be added
via env vars, never removed — removal requires editing `app.ini`.

### Database

- **SQLite** is the default and is enough for a single-owner homelab instance;
  the database file lives on the data volume.
- **PostgreSQL / MySQL** are supported for heavier instances; point
  `[database] DB_TYPE/HOST/NAME/USER/PASSWD` at the DB service.

### Storage

- All repository data, LFS, and uploads live under the mounted volume; on k3s
  that is the Longhorn PVC (`./02_Knowledge/technologies/kubernetes/longhorn/storage.md`).
- The volume must be owned by the image's UID/GID (1000) or the container fails
  to start.
- `ReadWriteOnce` is fine for a single node; a snapshot-capable StorageClass
  helps backups (`./02_Knowledge/technologies/services/forgejo/operations.md`).

### HTTPS

Traefik terminates TLS on the Ingress (cert-manager or self-signed). Forgejo
serves plain HTTP internally on port 3000; `ROOT_URL` should still advertise the
`https://` URL so links and OAuth callbacks are correct.

## Sources / Further Reading
- Installation guide: https://forgejo.org/docs/latest/admin/installation/
- Docker install (volumes, DB, rootless, NFS): https://forgejo.org/docs/latest/admin/installation/docker/
- Configuration cheat sheet: https://forgejo.org/docs/latest/admin/config-cheat-sheet/
- Storage settings: https://forgejo.org/docs/latest/admin/setup/storage/
- Overview: `./02_Knowledge/technologies/services/forgejo/overview.md`
