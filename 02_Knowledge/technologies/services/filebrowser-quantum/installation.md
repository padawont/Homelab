---
title: "FileBrowser Quantum — installation"
status: draft
author: "padawont"
date: 2026-11-08
tags: [filebrowser, filebrowser-quantum, installation, docker, self-hosted]
sources:
  - url: "https://filebrowserquantum.com/en/docs/getting-started/docker/"
    title: "Docker install (v2.0.x)"
  - url: "https://filebrowserquantum.com/en/docs/getting-started/linux/"
    title: "Linux install (v2.0.x)"
  - url: "https://filebrowserquantum.com/en/docs/getting-started/version/"
    title: "Which version should I use?"
  - url: "https://filebrowserquantum.com/en/docs/help/about/"
    title: "About FileBrowser Quantum (system requirements)"
  - url: "https://github.com/gtsteffaniak/filebrowser/releases/tag/v2.0.2-stable"
    title: "v2.0.2-stable release"
  - url: "https://github.com/gtsteffaniak/filebrowser"
    title: "GitHub repository and README comparison chart"
last_audit_date: 2026-11-10
related_docs:
  - "./02_Knowledge/technologies/services/filebrowser-quantum/overview.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/configuration.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/operations.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/authentication.md"
  - "./05_Implementations/node-main/k3s/overview.md"
---

# FileBrowser Quantum — installation

## Overview

FileBrowser Quantum ships two ways: a container image (`gtstef/filebrowser` on Docker Hub,
`ghcr.io/gtsteffaniak/filebrowser` on GHCR) or a standalone Go binary per architecture.
Both read one `config.yaml` and keep state in SQLite. Verified against **v2.0.2-stable**
(released 2026-10-23, current `stable`/`latest`), docs read 2026-11-08.

The image is published as `gtstef`/`gtsteffaniak`, not `filebrowser/filebrowser`.

## Details

### Docker image and tags

| Registry | Image |
|---|---|
| Docker Hub | `gtstef/filebrowser` (the README badge target) |
| GHCR | `ghcr.io/gtsteffaniak/filebrowser` |

`latest`/`stable` and `beta` include FFmpeg and document preview (arm64, amd64);
`stable-slim`/`beta-slim` are core-only, much smaller, and also ship arm32. Pin a full
tag (`2.0.2-stable`) or a line tag (`2.0-stable`); `2-stable` is moving.

Example — abstract (the docs' compose shape; `./files` is a placeholder host path):

```yaml
services:
  filebrowser:
    image: ghcr.io/gtsteffaniak/filebrowser:stable
    volumes:
      - ./files:/folder
      - ./data:/home/filebrowser/data
    ports:
      - "8080:80"
    restart: unless-stopped
```

Create `./data/config.yaml` (even empty) before first start, and `chown 1000:1000` the
mounted directories.

### Ports, mounts, and paths

| Item | Default (v2.0.2-stable) |
|---|---|
| Listen port | `80` in the image; change with `http.port` |
| Healthcheck | `curl -f http://localhost:80/health` |
| Config | `/home/filebrowser/data/config.yaml` |
| Database | `/home/filebrowser/data/database.sqlite` |
| Cache | `server.cacheDir` (docs example: `/home/filebrowser/data/tmp`) |
| Runtime user | `filebrowser`, UID:GID `1000:1000` |

- Mount one directory at `/home/filebrowser/data` so config, database, and cache survive
  replacement; the image reads all three from there, not from `/config`.
- Mount each shared tree, then map `sources[].path` to that mount (host `./files` →
  `/folder`); container-path rule: `./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md`.
- Mount the data **directory**, not a single database file — that is the documented Docker
  guidance; `server.database.path` overrides the `FILEBROWSER_DATABASE_PATH` env var.
- Ports below 1024 are privileged: binding 80 as a non-root user needs `NET_BIND_SERVICE`
  (`cap_add:` in Docker, `AmbientCapabilities=` under systemd). Rootful Docker usually
  grants it already; rootless engines typically fail, where a port above 1023 is simpler.

### Standalone binary

Release assets are named `<os>-<arch>-filebrowser`: `linux-amd64-filebrowser`,
`linux-arm64-filebrowser`, `linux-armv7-filebrowser`, `linux-riscv64-filebrowser`, and
similar. There is no installer — download, `chmod +x`, run.

Example — abstract (documented commands):

```bash
curl -LO https://github.com/gtsteffaniak/filebrowser/releases/latest/download/linux-amd64-filebrowser
chmod +x linux-amd64-filebrowser
./linux-amd64-filebrowser setup            # writes ./config.yaml
./linux-amd64-filebrowser -c config.yaml
```

- `setup` writes `config.yaml` in the current directory; otherwise author it by hand.
- v2 reads the listen port from `http.port`; `server.port` is rejected at startup.
- With no env var and no config path, the database is `./filebrowser.sqlite` in the
  process working directory — set `server.database.path` or a fixed `WorkingDirectory`.
- The docs publish a systemd unit (`User=filebrowser`,
  `ExecStart=/usr/local/bin/filebrowser -c /opt/filebrowser/config.yaml`).

### First run and admin creation

No default password ships. With `auth.adminPassword` and `FILEBROWSER_ADMIN_PASSWORD`
both unset, the server generates a random password for user `admin`, logs it once, and
forces a change at first login.

Example — abstract:

```bash
docker compose logs filebrowser 2>&1 | grep -i "initial admin password"
```

- Setting either option to a value other than empty or `admin` re-applies that password
  on **every** start, overwriting UI changes; remove it after setup.
- The literal `admin` is treated as unset — a random password is generated anyway.
- Recovery: stop the server (only one process may hold the database), then
  `<binary> -c <config> user set admin --password '<new>'` (container uses
  `--entrypoint="" … ./filebrowser user set admin …`).

### Resources and packaging

- Image size **180 MB** with FFmpeg (the About page's comparison row); `-slim` images omit
  FFmpeg and document preview and are only described as "much smaller".
- Memory floor: the About page says **256 MB**, the README comparison chart says **512 MB**
  for the same row — the vendor conflicts with itself, so size for the higher figure.
- No official Helm chart ships with the project, so a cluster install is hand-written
  manifests.

## Sources / Further Reading

- Docker install, tags, paths, database location: https://filebrowserquantum.com/en/docs/getting-started/docker/
- Binary install, systemd, first login: https://filebrowserquantum.com/en/docs/getting-started/linux/
- Release channels and tag formats: https://filebrowserquantum.com/en/docs/getting-started/version/
- System requirements and comparison chart: https://filebrowserquantum.com/en/docs/help/about/
- v2.0.2-stable release notes: https://github.com/gtsteffaniak/filebrowser/releases/tag/v2.0.2-stable
