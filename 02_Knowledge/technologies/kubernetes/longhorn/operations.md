---
title: "Longhorn operations"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, storage, longhorn, operations, backup, snapshot]
sources:
  - url: "https://longhorn.io/docs/1.12.1/snapshots-and-backups/backup-and-restore/"
    title: "Longhorn backup and restore"
  - url: "https://longhorn.io/docs/1.12.1/snapshots-and-backups/setup-a-snapshot/"
    title: "Longhorn snapshots"
  - url: "https://longhorn.io/docs/1.12.1/nodes-and-volumes/volumes/expansion/"
    title: "Expanding Longhorn volumes"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/longhorn/storage.md"
---

# Longhorn operations

## Overview

Day-to-day Longhorn work: protecting data with snapshots and backups, safely maintaining nodes, resizing volumes, and upgrading the storage layer without losing availability. All operations are driven from the UI, `kubectl` against Longhorn CRDs, or the `longhornctl` CLI.

## Details

### Snapshots

Snapshots are point-in-time, space-efficient copies of a volume, stored locally on the same disks. Create manually or on a schedule; chain them for retention (e.g. keep last 5 daily). Snapshots do not protect against node loss — backups do.

### Backups

Backups upload snapshots off-cluster to an S3-compatible endpoint, NFS share, or SMB share. Set a backup target in settings, then create a recurring backup job per volume.

```text
Example — abstract
backup target: s3://backup-bucket@us-east-1/
recurring job: every 6h, retain 4
restore: create new volume from backup (restores to a fresh volume, not in place)
```

### Detach / attach

Volumes attach to the node running the workload pod and detach when no pod uses them. Force detach is available for stuck volumes but should be a last resort — it can leave replicas inconsistent and trigger a rebuild.

### Volume expansion

Longhorn supports online expansion. Grow the PVC size and the volume, engine, and filesystem resize automatically (the StorageClass must have `allowVolumeExpansion: true`). Shrinking is not supported.

### Node maintenance and drain

- **Drain a node** before maintenance: move workloads off, then let Longhorn rebuild replicas on remaining nodes. Set the node to "drain" state or cordon + drain with the cluster tooling.
- **Node down**: remaining replicas keep serving; degraded volume rebuilds when the node returns or after the replica timeout.
- For planned maintenance, prefer evicting the node in the Longhorn UI first so replicas rebuild before the node goes offline.

### Upgrade

Upgrade the Helm chart in place; Longhorn upgrades the manager, then the instance-managers, then engines (per-volume, and can be deferred). Read the release notes — some upgrades require steps between versions. Upgrade engines during a maintenance window for busy volumes.

## Sources / Further Reading

- [Longhorn backup and restore](https://longhorn.io/docs/1.12.1/snapshots-and-backups/backup-and-restore/)
- [Longhorn snapshots](https://longhorn.io/docs/1.12.1/snapshots-and-backups/setup-a-snapshot/)
- [Expanding Longhorn volumes](https://longhorn.io/docs/1.12.1/nodes-and-volumes/volumes/expansion/)
- [Longhorn storage](./02_Knowledge/technologies/kubernetes/longhorn/storage.md)
