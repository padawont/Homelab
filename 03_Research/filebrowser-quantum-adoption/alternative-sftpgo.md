---
title: "Alternative: SFTPGo"
status: draft
author: "padawont"
date: 2026-11-10
tags: [sftpgo, sftp, file-management, self-hosted, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md"
references:
  - url: "https://github.com/drakkan/sftpgo"
    title: "SFTPGo repository"
  - url: "https://hub.docker.com/r/drakkan/sftpgo/tags"
    title: "Docker Hub — drakkan/sftpgo tags (sizes measured 2026-11-10)"
last_audit_date: 2026-11-10
related_docs: []
---

# Alternative: SFTPGo

## Overview

SFTPGo is an **SFTP/HTTP/WebDAV gateway first**: it exposes storage to protocol
clients and ships a web admin UI for accounts, quotas and virtual folders. It is not
browse-first — there is no document or media preview surface, so the UI exists to
administer access, not to read the files.

Access is modelled per account: each account gets virtual folders that point at
filesystem paths, so several storage roots can be presented in one instance. Its
state lives in a database — SQLite by default, PostgreSQL/MySQL optional — which the
homelab already accepts.

Image sizes were measured on Docker Hub on 2026-11-10: the `edge` tag reports
**53.5 MB compressed**, the `slim` tag is larger at **~65 MB**, and the small variants
are `edge-distroless-slim` at **23.3 MB**, `edge-alpine-slim` at **27.5 MB** and
`edge-alpine` at **27.9 MB**.

## Pros

- Multi-root in a single instance: several filesystem backends can be mounted and
  split across accounts via virtual folders.
- Protocol coverage beyond a browser — SFTP, HTTP and WebDAV reach clients that a
  web UI cannot (rsync-adjacent tooling, editors, backup jobs).
- Very small images: 53.5 MB compressed for `edge`, and down to 23.3 MB for
  `edge-distroless-slim` (27.5 MB `edge-alpine-slim`, 27.9 MB `edge-alpine`).
- Web admin UI covers accounts, quotas and virtual folders, so access management is
  not a config-file-only exercise.
- SQLite default keeps the state store local, with no extra service to run.

## Cons

- No browse-first experience and no document/media preview; consumers get a file
  transfer client, not a gallery or reader.
- Virtual folders are an access-control construct, not a browsing layout — the
  multi-root view is expressible but not the primary interface.
- The web UI is administrative; day-to-day use still happens over a protocol client.
- Any stateful deployment carries a database (SQLite file to persist) and therefore a
  volume of its own.
- No vendor-published RAM floor, so resource sizing is empirical rather than
  documented.

## Evaluation

### Scored criteria (weighted)

| Criterion | Weight | Score | Note |
|---|---|---|---|
| C1 — dedicated shared volume | 40% | 36/40 | A new PVC mounted into the pod is just a filesystem path, and a virtual folder can point at it, so serving a dedicated shared volume is fully in scope. |
| C2 — host directories | 35% | 33/35 | `hostPath` mounts reach SFTPGo the same way and per-account virtual folders expose them, though host binding keeps the pod node-locked. |
| C3 — footprint ≤ ~1 Gi | 25% | 23/25 | 53.5 MB compressed (`edge`), and 23.3 MB (`edge-distroless-slim`) / 27.9 MB (`edge-alpine`) on the small variants, all sit far under the ceiling; the `slim` tag is the outlier at ~65 MB, and no vendor-published RAM floor leaves the running figure unverified. |
| **Total** | **100%** | **92/100** | |

### Capability check (stated, not scored)

| Capability | Status |
|---|---|
| Existing read-only PVC | Yes — a claim mounted at a container path is a filesystem path like any other, which a virtual folder can address. |
| Multiple paths in one instance | Yes — per-account virtual folders express a multi-root view. |
| Backend breadth | Several filesystem backends, broader than a single local directory. |

### Disqualifiers

Database dependency — **not a disqualifier here**: SQLite is the default and the
homelab already accepts SQLite. SSO dependency — none found; local accounts are the
default path. Multi-source capability — present via per-account virtual folders, so it
does not disqualify the candidate.

## Verdict

No adoption decision is taken in this file — the call belongs to the topic overview
for epic #810. SFTPGo clears the storage criteria comfortably: it can serve a
dedicated shared volume and host directories, and its footprint is an order of
magnitude under the ceiling. What it does not provide is the browse-first surface and
the document/media preview, so it only fits a deployment whose goal is protocol
access rather than in-browser reading.
