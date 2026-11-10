---
title: "Alternative: Nextcloud"
status: draft
author: "padawont"
date: 2026-11-10
tags: [nextcloud, collaboration, file-management, self-hosted, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md"
references:
  - url: "https://github.com/nextcloud/server"
    title: "Nextcloud server repository"
  - url: "https://hub.docker.com/r/library/nextcloud/tags"
    title: "Docker Hub — library/nextcloud tags (sizes measured 2026-11-10)"
  - url: "https://docs.nextcloud.com/server/latest/admin_manual/installation/system_requirements.html"
    title: "Nextcloud system requirements"
last_audit_date: 2026-11-10
related_docs: []
---

# Alternative: Nextcloud

## Overview

Nextcloud is a **collaboration suite** — calendars, contacts, talk, and office alongside
files — not a file browser. The file view is one module among many, and it runs against a
Nextcloud-managed data directory backed by a database: SQLite is supported, but only for
testing and minimal instances, while production guidance points at
PostgreSQL/MySQL/MariaDB. The rest of the stack is a PHP web application.

This candidate is evaluated against the same three weighted criteria as the others, with
storage expectations taken from `./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md`
(the three source types: dedicated shared volume, selected host directories, existing
Longhorn PVC). No adoption decision is made here.

## Pros

- **Mature file handling**: uploads, sharing links, versions, and quotas are all
  first-class, with a long release history behind them.
- **A dedicated volume is the native layout**: the data directory is meant to live on its
  own volume, so a new PVC is the intended deployment shape rather than a workaround.
- **Broad storage reach**: non-local backends are reachable through external storage, so a
  single instance can present more than one path.
- **Collaboration included**: calendars, contacts, and talk come with the file module, so
  a second service for those needs is unnecessary.

## Cons

- **A real database server is the production shape**: SQLite is supported, but the system
  requirements page qualifies it as "(only recommended for testing and minimal-instances)",
  and production guidance points at PostgreSQL/MySQL/MariaDB. This homelab runs no database
  service, so a realistic deployment means standing one up alongside the PHP application
  stack — it is a strong preference, not an absolute requirement, since SQLite is permitted.
- **Not a directory browser**: files live in a Nextcloud-managed data directory, not an
  arbitrary host directory. External storage is the add-on that reaches anything else, and
  it brings indexing metadata with it.
- **Collaboration surface cost**: the file view ships inside a suite, so the image, the
  update path, and the attack surface all carry modules this use case does not need.
- **Own identity model**: users and sessions are Nextcloud's own, which makes any external
  SSO an integration rather than a default.

## Evaluation

Scored against the three weighted criteria. Each score is out of that criterion's weight.

| # | Criterion | Weight | Score | Assessment |
|---|---|---|---|---|
| C1 | Dedicated shared volume | 40% | 32/40 | A new PVC as the data directory is exactly Nextcloud's intended layout, so this criterion is met almost natively; only the split between the data volume and the database volume keeps it off full marks, and reaching anything already mounted needs the external-storage add-on. |
| C2 | Host directories | 35% | 7/35 | It does not browse arbitrary host directories the way a file manager does — files live in a Nextcloud-managed data directory, with external storage as an add-on — so the browse-what-is-mounted requirement is largely unmet. |
| C3 | Footprint ≤ ~1 Gi | 25% | 15/25 | The `stable` image measures 489.2 MB compressed (2026-11-10), and the requirements page puts the recommended minimum at 512 MB RAM per process — together they land right at the ~1 Gi budget with no headroom. |
| | **Total** | **100%** | **54/100** | |

There is a RAM floor: the system requirements page sets a minimum of **128 MB RAM per
process**, with a recommended minimum of **512 MB RAM per process**.

Capabilities, stated and **not** scored:

| Capability | Status |
|---|---|
| Existing read-only PVC | Partial — the claim can be mounted, but its contents become Nextcloud-managed index metadata rather than a read-only browse root. |
| Multiple storage paths in one instance | Yes — each added path is an external storage mount configured individually. |
| Backend breadth | Broad in principle — every non-local backend goes through the external storage add-on. |

**Disqualifier:** none absolute. SQLite is a supported database, so the candidate passes the
database gate rather than failing a hard requirement. What remains is a strong production
preference for a real database server (PostgreSQL/MySQL/MariaDB) plus a PHP application
stack — a substantially heavier deployment than a file browser. The SSO dependency (its own
account model as the default identity source) and the absence of native multi-source
browsing compound the problem rather than cause it.

## Verdict

Not carried forward for the file-browser role — on score and on fit, not on an absolute
disqualifier. The 54/100 total reflects the weakest points: host directories at 7/35, since
files live in a Nextcloud-managed data directory rather than arbitrary host trees, and
footprint at 15/25, since the 489.2 MB image plus 512 MB recommended per process consumes
the whole ~1 Gi budget. A dedicated shared volume is the native layout (32/40) and the
database gate itself is passed on SQLite, but a production-shaped deployment here means
PostgreSQL/MySQL/MariaDB plus a PHP application stack. Adopting it would mean operating
that stack to gain a collaboration suite where a file browser was asked for.
