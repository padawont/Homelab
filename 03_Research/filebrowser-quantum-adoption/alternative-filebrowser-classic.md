---
title: "Alternative: classic Filebrowser"
status: draft
author: "padawont"
date: 2026-11-10
tags: [filebrowser, file-management, self-hosted, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/filebrowser-quantum/overview.md"
references:
  - url: "https://github.com/filebrowser/filebrowser"
    title: "Classic Filebrowser repository (archived 2026-09-01)"
  - url: "https://hub.docker.com/r/filebrowser/filebrowser/tags"
    title: "Docker Hub — filebrowser/filebrowser tags (sizes measured 2026-11-10)"
last_audit_date: 2026-11-10
related_docs: []
---

# Alternative: classic Filebrowser

## Overview

Classic Filebrowser (`filebrowser/filebrowser`) is the upstream project Quantum forked:
a self-hosted, browser-based file manager distributed as one Go binary with the web UI
embedded, under Apache-2.0. Its entire state — users, settings and the file index — lives
in a single embedded **BoltDB** file, `./filebrowser.db` by default, alongside the tree it
serves, so state is portable and there is no database server to run.

It is the mature option: the v2.63.x line (current tag `v2.63.23`) has been in production
use far longer than Quantum's v2, which dates its breaking rewrite to July 2026. The
trade-off the fork exists to fix is structural — classic Filebrowser serves **one source
per instance**, where Quantum serves several.

This file evaluates it as a candidate for issue #811 under the three weighted criteria of
epic #810. It records evidence and a verdict on the candidate; the adoption decision
belongs to the ADR.

## Pros

- **Maturity.** A long v2.63.x line, wide install base, and behaviour that has not moved
  under its users recently — the opposite of Quantum's young v2 line.
- **Small image.** 16.1 MB compressed on Docker Hub for `latest`/`v2.63.23` (measured
  2026-11-10), which clears the footprint target with room to spare.
- **No external dependencies.** The embedded BoltDB file and local accounts mean no
  database service and no identity provider are required to start it.
- **Mount shape is not a constraint.** It serves any directory the container can see, so
  a dedicated shared volume and plain host bind-mounts both work; the criteria C1 and C2
  are configuration rather than features.
- **Simple state.** One BoltDB file plus the mounted tree can be copied for backup, and
  a rebuild is a container restart.

## Cons

- **One source per instance.** Three trees mean three containers, three URLs, three
  credential sets, three BoltDB files. This is the whole problem, not an inconvenience.
- **Upstream is archived.** The repository was archived on 2026-09-01, the last planned
  release has shipped, and the project states there will be no further releases, bug fixes
  or security fixes — it advises anyone still running File Browser to treat it as
  unmaintained software.
- **No SSO or LDAP.** Local accounts only: classic's own `docs/authentication.md` lists
  just JSON, proxy-header, a hook and no-auth methods, so ACME SSO would have to be
  fronted by a proxy or abandoned.
- **Thinner authorisation model.** No per-source view/download/modify grants, so the
  read-only posture for a shared volume is enforced at the mount, not in the app.
- **Feature gaps that compound the multi-instance cost.** No WebDAV, no indexed or
  advanced search, no long-lived API tokens — each has to be worked around per instance.
- **Command runner ships disabled, not on.** `--disableExec` defaults to true, so the
  shell-command feature is inert unless an operator turns it on; Quantum removed it
  deliberately, and enabling it widens what a compromised admin account can do.
- **No vendor-published RAM floor.** No minimum memory figure is published anywhere in the
  project's documentation, so memory must be measured on this host rather than quoted.

## Evaluation

**Method.** Image size was read from Docker Hub's *Compressed size* column for the
`filebrowser/filebrowser` `latest` tag, which resolves to `v2.63.23`, on 2026-11-10:
**16.1 MB compressed**. The ~31 MB figure often quoted for this image is not the
compressed registry size — it corresponds to the uncompressed/on-disk layer footprint —
so it is not used here. C1 and C2 were assessed from how the container consumes mounts;
C3 from the measured compressed size and the absence of any published RAM floor.

| Criterion | Weight | Score | Basis |
|---|---|---|---|
| C1 — dedicated shared volume | 40% | 40/40 | A dedicated volume mounted into the container is the normal deployment shape; it is served as-is with no import step. |
| C2 — host directories | 35% | 35/35 | Host paths bind-mount directly, and the only state outside them is the BoltDB file, so host trees stay authoritative. |
| C3 — footprint ≤ ~1 Gi | 25% | 25/25 | 16.1 MB compressed is two orders of magnitude under the ceiling; no vendor-published RAM floor exists, so memory sizing is a measurement, not a citation. |
| **Total** | **100%** | **100/100** | All three weighted criteria pass. |

Capabilities relevant to issue #811, stated and **not** scored:

| Capability | Classic Filebrowser | Note |
|---|---|---|
| Existing read-only PVC | Supported — a read-only mount is served as-is. | Read-only is a property of the mount, not a per-source setting; Quantum can make one source read-only without touching the mount. |
| Multiple sources in one instance | **Not supported** — one root per instance. | The requirement in issue #811 is three trees behind one instance. |
| Backend breadth | **BoltDB only** — no SQLite option, no external database server. | A second backend would not serve a second tree; classic offers none. |

**Disqualifier check** — database dependency: none, the state is a single embedded BoltDB
file and no server is required · SSO dependency: none, local accounts suffice to run it,
OIDC and LDAP being absent · multi-source capability: **absent**, one root per instance, so
the three-tree requirement is met only by running three instances. That last line is the
disqualifier, and it is not softened by the perfect score above.

## Verdict

**Rejected** for issue #811 — not on footprint and not on mount shape, both of which it
passes cleanly, but on the one capability the homelab actually requires. It posts the
highest weighted score in the set, 100/100, and is disqualified by the multi-source gate:
classic serves one root per instance, so the three-tree requirement is met only by running
three instances. That is the primary reason it is not carried forward.

Archive status is an independent second reason. The upstream repository was archived on
2026-09-01, the last planned release has shipped, and the project states there will be no
further releases, bug fixes or security fixes, advising that anyone still running File
Browser treat it as unmaintained software. A perfect weighted score cannot paper over an
unmaintained upstream that ships no security fixes.

The cost of pressing it into service is concrete: three containers, three URLs, three user
sets, three BoltDB files, and no shared search or SSO across them — precisely the
operational burden Quantum was forked to remove. It stays in the record as the mature
baseline the other candidates are measured against, and as the reference case for "good,
mature, wrong shape" whose upstream has stopped.

No adoption decision is made here; the ADR decides.
