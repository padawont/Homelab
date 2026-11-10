---
title: "Alternative: FileBrowser Quantum"
status: draft
author: "padawont"
date: 2026-11-10
tags: [filebrowser-quantum, file-management, self-hosted, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/filebrowser-quantum/overview.md"
  - knowledge: "./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md"
references:
  - url: "https://github.com/gtsteffaniak/filebrowser"
    title: "FileBrowser Quantum repository and README"
  - url: "https://filebrowserquantum.com/en/docs/help/about/"
    title: "About FileBrowser Quantum (system requirements)"
last_audit_date: 2026-11-10
related_docs: []
---

# Alternative: FileBrowser Quantum

## Overview

FileBrowser Quantum is a self-hosted, browser-based file manager: a single Go binary with
the web UI embedded, Apache-2.0, current stable **v2.0.2-stable** released 2026-10-23
(https://github.com/gtsteffaniak/filebrowser). It does not own storage — it exposes
directories that already exist inside its pod through a web UI, WebDAV, and an HTTP API,
with per-user and per-source access control. One instance can declare several sources,
each with its own include/exclude rules; configuration is driven by `config.yaml`
(per `./02_Knowledge/technologies/services/filebrowser-quantum/overview.md` and
`./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md`).

This file evaluates Quantum alone against the three weighted criteria fixed for epic #810
(issue #811). The adoption decision belongs to the ADR, not here.

## Pros

- **Multi-source by design**: several paths in one instance, each with its own name,
  include/exclude rules, and permission grants — no per-directory instance to run
  (per `./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md`)
- **Storage-agnostic**: mounts whatever the pod mounts — `hostPath`, an existing PVC, or
  a new PVC — and the access mode is whatever the claim declares; the source type is a
  pod-spec choice, not a product constraint
- **Read-only and view-only scopes**: per-source permissions separate view, download,
  modify, create, and delete, so a source can be browsable without being writable
  (per `./02_Knowledge/technologies/services/filebrowser-quantum/overview.md`)
- **Small, single-process footprint**: 180 MB image **with** FFmpeg (`-slim` images omit
  it) and a memory floor of 256 MB per the vendor About page, 512 MB per the README
  comparison chart
- **No external dependency**: embedded SQLite in-process — no database server to run —
  and SSO (OIDC, LDAP, JWT, proxy) is optional rather than required
- **Reduced UI attack surface**: shell commands were removed from the UI entirely and the
  README states they will not return

## Cons

- **Contradictory memory floor**: the About page says 256 MB and the README chart says
  512 MB for the same row, so sizing has to assume the higher figure to be safe
- **Filesystem only**: no S3 or object backend; a path the pod does not mount simply
  cannot be exposed as a source
- **Host-directory sources pin the pod**: `hostPath` and `local-path` bind the data to one
  node, so the pod must land there — free on single-node k3s, a constraint once a second
  node exists
- **Young v2 line**: v2.0.0 was a breaking rewrite in July 2026, so material written for
  v1.5.x does not describe the current release
- **Read-only is arranged, not inherent**: for an existing PVC, read-only behaviour comes
  from how the pod mounts it plus the per-source permission grants, not from the product
  detecting the claim's mode

## Evaluation

### Weighted criteria

| Criterion | Weight | Score | Justification |
|---|---|---|---|
| C1 dedicated shared volume | 40% | 40 / 40 | A new PVC mounts exactly like any other volume and is then declared as a source path, with access mode set on the claim rather than by Quantum — nothing in the product constrains this shape. |
| C2 host directories | 35% | 32 / 35 | `hostPath` (or a `local-path` PVC) is a first-class source type and works directly; on single-node k3s the node pinning costs nothing today, but it does bind the pod to `node-main`. |
| C3 footprint ≤ ~1 Gi | 25% | 25 / 25 | 180 MB image with FFmpeg plus a 256 MB (About) or 512 MB (README) memory floor both fit inside 1 Gi, though capacity planning should use the 512 MB figure. |

**Weighted total: 97 / 100** — the only deduction is the node pinning implied by host
directories, not a functional gap.

### Capability table (stated, not scored)

| Capability | Stated position |
|---|---|
| Existing read-only PVC mounted read-only | Yes — an existing claim is referenced as a volume and mounted read-only in the pod spec, then exposed as a source; the per-source permission grants keep users to view/download, so read-only is honoured at two layers. |
| Multiple sources in one instance | Yes — several entries under `server.sources`, each with its own path, name, and include/exclude rules, all rendered in one UI. |
| Backend breadth | None beyond the local filesystem — no S3 or other object backend; only paths visible in the pod's mount namespace can be served. |

**Disqualifiers**: none. It needs no database the homelab does not run (embedded SQLite,
no separate server), it needs no SSO to function (local accounts suffice; OIDC/LDAP are
optional), and it does multi-source natively.

## Verdict

**Viable, no disqualifier** — the research position is that FileBrowser Quantum clears all
three weighted criteria (97/100) with no blocking dependency: the dedicated shared volume
and host-directory shapes are both plain pod mounts, the footprint stays well under 1 Gi
even at the higher of the two published memory figures, and multi-source is native rather
than bolted on. The residual risks are the contradictory memory floor, the node pinning
that host-directory sources imply, and the youth of the v2 line — points for the ADR to
weigh, not reasons to drop the candidate. Whether it is adopted is the ADR's decision
(per `./02_Knowledge/technologies/services/filebrowser-quantum/overview.md`).
