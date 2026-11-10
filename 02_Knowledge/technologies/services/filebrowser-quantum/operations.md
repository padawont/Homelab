---
title: "FileBrowser Quantum — operations"
status: draft
author: "padawont"
date: 2026-11-08
tags: [filebrowser, filebrowser-quantum, operations, backup, upgrades, logging]
sources:
  - url: "https://filebrowserquantum.com/en/docs/features/indexing/"
    title: "Indexing Overview"
  - url: "https://filebrowserquantum.com/en/docs/features/item-thumbnails/"
    title: "Thumbnail Previews"
  - url: "https://filebrowserquantum.com/en/docs/configuration/server/"
    title: "Server Settings"
  - url: "https://filebrowserquantum.com/en/docs/configuration/logging/"
    title: "Logging"
  - url: "https://filebrowserquantum.com/en/docs/advanced/logging/debug-logging/"
    title: "Debug Logging"
  - url: "https://filebrowserquantum.com/en/docs/getting-started/version/"
    title: "Which version should I use?"
  - url: "https://filebrowserquantum.com/en/docs/getting-started/docker/"
    title: "Docker (v2.0.0)"
  - url: "https://filebrowserquantum.com/en/docs/getting-started/v2/migration/"
    title: "Migration Guide (v2.0.0)"
last_audit_date: 2026-11-10
related_docs:
  - "./02_Knowledge/technologies/services/filebrowser-quantum/overview.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/installation.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/configuration.md"
---

# FileBrowser Quantum — operations

## Overview

Day-two work on FileBrowser Quantum: what the index and thumbnail caches are, where persistent state lives, how to upgrade, how to inspect health and logs, and which files must be backed up. Verified against **v2.0.2-stable** (the `stable`/`latest` tag at the time of writing; released 2026-10-23), docs read 2026-11-08.

Quantum v2 uses a SQLite database (`database.sqlite` or `filebrowser.sqlite`) **plus** a separate on-disk search index, and caches previews on disk. That split is what makes the backup and upgrade steps below different from a single-file datastore.

## Details

### Index and thumbnail caches

Both live under `server.cacheDir` (built-in default `tmp`); the Docker container path and
mounts are in `./02_Knowledge/technologies/services/filebrowser-quantum/installation.md`
§ Ports, mounts, and paths.

- **Search index**: SQLite database files under `<cacheDir>/sql`. The index is built at startup when absent, then kept current by scanners: one full scan followed by four modtime-based quick scans, with adaptive intervals from ~5 minutes to 12 hours. Index data persists across restarts, so a normal restart does not re-index.
- **Rebuild cost**: the first full scan is the expensive one. Rough guide: 10k folders/10k files → seconds; 250k folders/10k files → 2–5 minutes; 500k/500k → 5+ minutes, worse on slow disks. Memory is OS-paged via SQLite (roughly 50–300 MB in the same examples).
- **What invalidates it**: setting `server.indexSqlConfig.disableReuse: true` (fresh index on every start), or a database that fails the startup integrity check — corruption is detected on startup, the old index is discarded, and a fresh one is created.
- **Thumbnails**: cached under `cacheDir`, alongside other image-processing temp files, in small (256×256), large (640×640) and original sizes. Preview generation is on demand; if the cache is lost, thumbnails are regenerated on the next request — no user data is lost.
- Quick scans detect added, deleted and renamed entries but **not** edits that keep the same size; those appear only after a full scan.

### Database

v2 stores persistent state in SQLite; v1 used BoltDB:

- **Contents**: users and credentials, shares, access rules, API tokens, index metadata, sidebar links. v2.1+ adds quota tables. Config and database are both needed for a faithful restore: `userDefaults` values set in `config.yaml` are locked in the UI, so the database does not hold them.
- **Path**: the built-in defaults are in `./02_Knowledge/technologies/services/filebrowser-quantum/installation.md` § Ports, mounts, and paths,
  and the override order (`server.database.path` → env → default) is in
  `./02_Knowledge/technologies/services/filebrowser-quantum/configuration.md` § Precedence.
- **WAL mode** (`server.indexSqlConfig.walMode: true`) adds `-wal` and `-shm` sidecar files; a dirty shutdown is more likely to discard or corrupt state, so stop the service before a file-level copy.

Example — abstract:

```yaml
server:
  indexSqlConfig:
    walMode: false   # true adds the -wal and -shm sidecar files
```

### Upgrades

1. Back up `config.yaml` and the SQLite database (see below) before changing tags.
2. Pull the new image or binary. No config migration is documented within v2.0.x, so a patch upgrade is a tag change plus restart.
3. Choose the tag deliberately: pinning rules and what each channel tracks are in
   `./02_Knowledge/technologies/services/filebrowser-quantum/installation.md` § Docker image and tags.
4. Verify login, shares and a search after the restart.

**v1 → v2 caveat (old data)**: v2 changes both config structure and database format. An instance whose data predates v2 cannot just switch tags: stop it, copy `database.db` somewhere safe, rename it to `database.db.old`, convert the config, set `server.database.migrateFrom` to the renamed file, and let the first v2 start import users, shares, access rules, API tokens, index metadata and sidebar links. Keep the old database until validation passes; rollback means restoring the v1 install and its backup.

### Health and logs

- **Health check**: the image ships an HTTP `GET /health` probe (see `./02_Knowledge/technologies/services/filebrowser-quantum/installation.md`
  § Ports, mounts, and paths). If you change `http.port`, update the probe's port too.
- **Logs**: stdout by default at `info|warning|error` plus API events, with colours. Set `server.logging[].output` to a path for file logs; file logs **do not rotate**, so use `logrotate` or the container runtime's log driver.
- **Debug**: add `debug` to `levels` (e.g. `"info|warning|error|debug"`) temporarily. Debug adds file/line numbers to every log line and is noisy; turn it off afterwards. `FATAL` always prints to the console and cannot be disabled.
- **Upgrade/migration check**: watch startup logs for the migration summary (`Migrated N users`, `Migrated N shares`, `Migration completed successfully!`).
- **Index check**: a slow start usually means the index integrity check or a full scan. `startupIntegrityCheck` defaults to `quickCheck`; `probe` is the documented recommendation for large indexes, and `off` gives the fastest boot at the cost of safety.

Example — abstract:

```yaml
server:
  logging:
    - output: "stdout"
      levels: "info|warning|error"
    - output: "/var/log/filebrowser/errors.log"
      levels: "error"
      noColors: true
```

### Backup

Minimum viable set — everything else is rebuildable:

| Item | Why | Rebuildable? |
|---|---|---|
| `config.yaml` | sources, auth, logging, server settings | No |
| SQLite DB (`database.sqlite`) | users, shares, rules, tokens, sidebar links | No |
| `cacheDir/sql` (index) | avoids a full scan on restore | Yes — re-index |
| `cacheDir` thumbnails/temp | previews, archive spool | Yes — regenerated |

- Stop the service (or use a filesystem snapshot) before copying the SQLite file; in WAL mode include `-wal`/`-shm`. As with any SQLite database, a hot copy of a live file can be inconsistent.
- Take `config.yaml` from its effective location rather than a guessed one; the search
  order is in `./02_Knowledge/technologies/services/filebrowser-quantum/configuration.md` § File discovery. In Docker it lives in the mounted
  data directory.
- The source data (`/folder`, `/srv`, `/data`) is **not** FileBrowser state — back it up separately; excluding it keeps the app backup small.
- Keep a copy of the pre-upgrade `database.db` when migrating from v1, outside the active data directory.

## Sources / Further Reading

- Indexing: https://filebrowserquantum.com/en/docs/features/indexing/
- Thumbnails: https://filebrowserquantum.com/en/docs/features/item-thumbnails/
- Server settings (`cacheDir`, `indexSqlConfig`, database): https://filebrowserquantum.com/en/docs/configuration/server/
- Logging: https://filebrowserquantum.com/en/docs/configuration/logging/
- Debug logging: https://filebrowserquantum.com/en/docs/advanced/logging/debug-logging/
- Version channels: https://filebrowserquantum.com/en/docs/getting-started/version/
- Docker (healthcheck, database location): https://filebrowserquantum.com/en/docs/getting-started/docker/
- v2 migration: https://filebrowserquantum.com/en/docs/getting-started/v2/migration/
