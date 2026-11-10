---
title: "Alternative: Filestash"
status: draft
author: "padawont"
date: 2026-11-10
tags: [filestash, file-management, self-hosted, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md"
references:
  - url: "https://github.com/mickael-kerjean/filestash"
    title: "Filestash repository"
  - url: "https://hub.docker.com/r/machines/filestash/tags"
    title: "Docker Hub — machines/filestash tags (sizes measured 2026-11-10)"
  - url: "https://www.filestash.app/docs/guide/storage.html"
    title: "Filestash — storage and Virtual Filesystem"
  - url: "https://www.filestash.app/docs/install-and-upgrade/"
    title: "Filestash — installation and upgrade"
last_audit_date: 2026-11-10
related_docs: []
---

# Alternative: Filestash

## Overview

Filestash is a self-hosted web file manager built as a connector/browser over pluggable
backends. Each connection targets a backend — a local filesystem path, an S3 bucket, a
WebDAV or FTP server, SFTP, Git, and more — and its Virtual Filesystem aggregates several
of those storages "into a single logical view of your files", mounted together through
configuration (for example `/folderA/ { "type": "local" }` beside
`/folderB/ { "type": "azure" }`). Storage guide: "You aren't limited to one either. Pick
as many storages as you like." The aggregation is a connection/virtual-mount
configuration, though, not per-source browsable roots carrying per-source permissions and
rules.

This note scores it as one candidate in the epic #810 (issue #811) field against the same
three weighted criteria as the other candidates. Image size is Docker Hub tag metadata
measured 2026-11-10; no instance was deployed for this note.

## Pros

- Broadest backend coverage in the field: S3, WebDAV, FTP, SFTP, Git and more from one
  tool.
- Compact image: 270.8 MB compressed for `latest` on Docker Hub (`machines/filestash`,
  measured 2026-11-10), far under the ~1 Gi ceiling.
- A local-filesystem backend exists, so an existing read-only PVC or a host directory can
  be browsed through it without any protocol translation.
- Several storages can be mounted into one logical view via its Virtual Filesystem
  configuration, so paths from different backends are not isolated instances.

## Cons

- Aggregation is a virtual-mount configuration, not first-class sources: mounted folders
  do not become browsable roots each carrying its own permissions and include/exclude
  rules, so the per-source model the storage note describes has no direct equivalent.
- Its breadth is a strength this homelab cannot use: there is no object store, so
  S3/WebDAV support is out of scope here.
- RAM floor is the vendor's stated baseline — "1 core, 128MB of RAM is plenty" — not a
  measured figure for this workload, so actual headroom is unproven.

## Evaluation

Weights from issue #811. Each score is the criterion's weight times the degree to which
Filestash meets it.

| Criterion | Weight | Score | Rationale |
|---|---|---|---|
| C1 — dedicated shared volume | 40% | 35/40 | A volume is mounted into the pod and exposed through a local-filesystem entry in the Virtual Filesystem, so the content is browsable; the gap is that it enters as a virtual mount rather than a first-class source with its own permissions and rules. |
| C2 — host directories | 35% | 30/35 | Several local paths aggregate into one logical view through the same Virtual Filesystem configuration, but without per-source rules distinguishing them. |
| C3 — footprint ≤ ~1 Gi | 25% | 25/25 | 270.8 MB compressed (Docker Hub `latest`, measured 2026-11-10) is well inside the ceiling, and the install guide publishes a 128 MB RAM floor on 1 core — both criteria met. |

Total: **90/100**. Gate: **passes** — multi-source aggregation is documented, so the
candidate is no longer disqualified.

Capability table — stated, not scored:

| Capability | Status | Detail |
|---|---|---|
| Existing read-only PVC | Supported | A local-filesystem entry pointed at the mounted claim browses it; read-only is enforced by the volume mount, not by the browser. |
| Multiple storages in one instance | Supported — aggregated, not first-class | The Virtual Filesystem mounts several backends "into a single logical view of your files" (`/folderA/ { "type": "local" }`, `/folderB/ { "type": "azure" }`), so storages compose; they do not appear as browsable roots with per-source permissions and rules. |
| Backend breadth | Broadest of the candidates | S3, WebDAV, FTP, SFTP, Git, and more; the homelab's no-object-store shape leaves most of that breadth unused. |

**Disqualifiers:** three are tracked — a database dependency, an SSO dependency, and
multi-source capability. The multi-source item now clears: the storage guide documents
several storages mounted into one logical view. The database and SSO items are not
established either way by the sources read for this note.

## Verdict

Carried forward as a close third in the field, behind SFTPGo (92/100). Filestash is the
broadest connector here and its 270.8 MB image with a 128 MB published RAM floor clears
C3 outright; the Virtual Filesystem also lets several storage paths aggregate into one
view. What it loses is not capability but shape — the aggregation is a virtual mount
rather than per-source browsable roots carrying their own permissions and rules, which is
exactly where FileBrowser Quantum wins. At 90/100 it sits 2 points behind SFTPGo and
carries forward as a close third — a viable fallback rather than a rejection.

No adoption decision is made in this note; that belongs to the research overview.
