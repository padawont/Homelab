---
title: "Forgejo operations — backup, restore, upgrades"
status: accepted
author: "padawont"
date: 2026-08-23
tags: [forgejo, operations, backup, restore, upgrade]
sources:
  - url: "https://forgejo.org/docs/latest/admin/upgrade/"
    title: "Forgejo upgrade guide"
  - url: "https://forgejo.org/docs/latest/admin/command-line/"
    title: "Forgejo command-line interface"
  - url: "https://forgejo.org/docs/latest/admin/release-schedule/"
    title: "Forgejo release schedule"
  - url: "https://forgejo.org/docs/latest/admin/troubleshooting/logging/"
    title: "Forgejo logging configuration"
last_audit_date: 2026-08-23
related_docs:
  - "./02_Knowledge/technologies/services/forgejo/overview.md"
  - "./02_Knowledge/technologies/services/forgejo/install-config.md"
  - "./02_Knowledge/technologies/kubernetes/longhorn/storage.md"
---

# Forgejo operations — backup, restore, upgrades

## Overview

Day-to-day operations for a self-hosted Forgejo instance: consistent backups
with `forgejo dump` (or snapshotting), safe upgrades between releases, and
restore/verification. Forgejo follows semantic versioning since 7.0.0, and the
database stores its schema version so a downgrade is refused automatically.

## Details

### Backup

The reliable option is a synchronized point-in-time snapshot of all storage
Forgejo uses. On k3s that means snapshotting the Longhorn volume
(`./02_Knowledge/technologies/kubernetes/longhorn/storage.md`); if storage is
spread across several systems (DB on one volume, repos on another), stop
Forgejo during the backup so the pieces stay consistent.

For a simple single-filesystem setup the built-in command is:

```bash
forgejo dump
```

- Produces a single zip containing configuration, repositories, and the
  database.
- SQLite is already included in the zip; for PostgreSQL/MySQL also take a
  native `pg_dump`/`mysqldump` — the SQL dump embedded by `forgejo dump` has
  known bugs when re-injected into a new database.
- Schedule it as a k8s CronJob writing to a backup location (e.g. a separate
  volume or object storage), keeping a few rotations.

### Restore

1. Stop Forgejo.
2. Extract the dump zip and restore data, repos, and config to the data volume.
3. Restore the native database dump (for Postgres/MySQL).
4. Start Forgejo and verify:
   `forgejo doctor check --all --log-file /tmp/doctor.log`
   plus a manual web-UI walk-through (login, a repo, an issue).

### Upgrades

Forgejo release lifecycle:

| Channel | Support |
|---|---|
| **Stable** (latest) | Bugfix + security fixes for ~3 months + 2-week overlap |
| **LTS** (version published the first quarter of every year) | Critical fixes for ~1 year 3 months |
| **Experimental** (dev) | Not for production |

Upgrade procedure:

1. **Back up first** — required when moving across a stable release, wise for
   minor/patch.
2. Read the release notes for the target version, including known problematic
   upgrade paths (see the upgrade guide).
3. Before switching: `forgejo manager flush-queues` (queued data is not
   guaranteed compatible between versions).
4. Perform the upgrade by replacing the container image or binary — migrations
   run automatically on first start.
5. **Verify carefully**: `forgejo doctor check --all` plus a manual checklist.
   A restore after an upgrade is easy; fixing a live instance weeks later is not.

Notes:

- Major version jumps (e.g. 15 → 16) may contain breaking changes and require
  the manual procedure; upgrading X → X+1 needs human verification. Staying on
  the `16` image tag gives minor updates automatically.
- Docker installs need docker >= 20.10.6.
- The database version guard refuses to start a downgraded binary against a
  newer database — do not bypass it.
- Subscribe to the security-announcements repo to plan security releases.

### Day-to-day

- Logs: k8s — `kubectl logs -f deploy/forgejo -n forgejo`; Forgejo can also
  write logs to files via `[log]` sections (console/file modes); SQL logging
  is toggled by `LOG_SQL=true` in the `[database]` section.
- Health: rely on pod liveness/readiness probes hitting the web port; run
  `forgejo doctor` after any upgrade.
- Cross-check storage usage on the Longhorn PVC periodically.

## Sources / Further Reading

- Upgrade guide: https://forgejo.org/docs/latest/admin/upgrade/
- CLI reference (`dump`, `doctor`, `forgejo-cli`): https://forgejo.org/docs/latest/admin/command-line/
- Release schedule: https://forgejo.org/docs/latest/admin/release-schedule/
- Logging configuration: https://forgejo.org/docs/latest/admin/troubleshooting/logging/
- Install: `./02_Knowledge/technologies/services/forgejo/install-config.md`
