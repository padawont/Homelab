---
title: "FileBrowser Quantum adoption research"
status: draft
author: "padawont"
date: 2026-11-10
tags: [filebrowser-quantum, file-management, storage, research]
sources:
  - knowledge: "./02_Knowledge/technologies/services/filebrowser-quantum/overview.md"
  - knowledge: "./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md"
  - knowledge: "./02_Knowledge/technologies/services/filebrowser-quantum/operations.md"
references:
  - url: "https://github.com/gtsteffaniak/filebrowser"
    title: "FileBrowser Quantum repository"
  - url: "https://filebrowserquantum.com/en/docs/help/about/"
    title: "About FileBrowser Quantum (system requirements)"
last_audit_date: 2026-11-10
related_docs: []
---

# FileBrowser Quantum adoption research

## Goal

Which of five file-access products should `node-main` run to put a dedicated shared
volume and a set of host directories behind one browser UI?

The need is concrete: today the only in-cluster file storage is the `cv-sender-data`
volume, and every other directory on the host is reachable only by SSH. Nothing offers a
browsable, read-and-write surface over several trees at once, so moving a file in or out
of the cluster means a shell session or a `kubectl cp`.

The comparison is bounded by the homelab, not by the products: a single node (k3s on
`node-main`), local accounts only, plain HTTP on the LAN, no identity provider, no object
store, and roughly 1 Gi of memory available. Any candidate that needs a component the
homelab does not run is out before scoring matters.

## Alternatives

See [./alternatives.md](./alternatives.md) for the index — score, gate outcome and status
for each candidate, kept there and not repeated here. The five files are
[./alternative-filebrowser-quantum.md](./alternative-filebrowser-quantum.md),
[./alternative-filebrowser-classic.md](./alternative-filebrowser-classic.md),
[./alternative-sftpgo.md](./alternative-sftpgo.md),
[./alternative-nextcloud.md](./alternative-nextcloud.md) and
[./alternative-filestash.md](./alternative-filestash.md).

## Plan for ADR

### Recommended technology and why

**FileBrowser Quantum, `v2.0.2-stable`** (Apache-2.0, single Go binary, released
2026-10-23), scored at 97/100. It is the only candidate that serves several sources in
one instance natively — each declared under `server.sources` with its own path, name,
include/exclude rules, and permission grants — which is the requirement that decided the
comparison. The dedicated shared volume and the host directories then reduce to ordinary
pod mounts, and the footprint (180 MB with FFmpeg — the `-slim` variants drop FFmpeg and
document preview and are only described as "much smaller" — memory floor 256 or 512 MB
depending on which vendor page you read) sits inside the 1 Gi budget.

### How it fits the existing homelab

- **Shared volume**: a Longhorn-backed PVC, mounted at a fixed container path and declared
  as a source — the volume's access mode stays a property of the claim, not of the app.
- **Host directories**: `hostPath` mounts for `/srv/files/*`, each path declared as its own
  source so per-source rules apply per tree.
- **Ingress**: Traefik, host `browse.local`, plain HTTP only.
- **Plain HTTP**: accepted, but recorded as a risk rather than assumed away.

### Architecture overview

```
browser → Traefik (browse.local) → Service → pod → {PVC, hostPath, read-only PVC}
```

The pod mounts three distinct shapes and Quantum serves each as a named source through the
same UI. The rendered mermaid diagram belongs to the ADR; this is the text topology only.

### Dependencies and integration points

- **Longhorn** — the PVC for the shared volume.
- **Traefik** — the Ingress; no TLS termination in scope for this pass.
- **ConfigMap** — holds `config.yaml`, so sources and settings are declarative and
  reviewable in git rather than typed into the UI.
- **None other**: no database server (state is embedded SQLite in-process) and no identity
  provider (local accounts, OIDC/LDAP left off).

### Risks and mitigation

- **Plain HTTP on the LAN** — session cookies cross the wire unencrypted, and WebAuthn is
  unavailable to any non-secure origin. Mitigation: LAN-only exposure, no port forward,
  and a recorded acceptance in the ADR; TLS is a follow-up, not a prerequisite.
- **Single-node Longhorn RWO** — a `ReadWriteOnce` claim pins the consumer to one node.
  Free today on a single-node cluster; noted as the constraint it becomes at two nodes.
- **Index cache rebuild time** — index data persists across restarts, so a normal restart
  does not re-index. A rebuild happens only when `server.indexSqlConfig.disableReuse: true`
  forces a fresh index, or when the startup integrity check discards a corrupt one; the slow
  case is a *first* scan of a large source. Mitigation: keep `server.cacheDir` on a
  persistent volume, leave `disableReuse` off, and size the probe budget before first use.
- **Contradictory memory floor** — the vendor's About page says 256 MB while its README
  chart says 512 MB for the same row. Mitigation: plan against 512 MB; the 1 Gi budget
  still holds.

### Criteria carried into the ADR

Weighted criteria from issue #811: **C1 dedicated shared volume 40%**, **C2 host
directories 35%**, **C3 footprint ≤ ~1 Gi 25%**. The read-only mount of the existing
`cv-sender-data` claim is in deployment scope but was dropped as a scored criterion — it is
a mount and a permission grant, not a differentiator between these candidates.

## Recommendation

**approve** — this is the research verdict handed to the ADR, not the adoption decision
itself.

The runner-up is **SFTPGo at 92/100**, and it lost on shape rather than on score: it is an
SFTP/HTTP/WebDAV transfer gateway with an admin UI, not a browse-first file manager, and
its multi-root support is expressed as per-account virtual folders rather than several
browsable sources with per-source rules. **Filestash at 90/100** is within two points of it
and lost on the same axis — per-source permissions and browsable-root semantics.

Worth recording alongside that: **classic Filebrowser scored 100/100** — higher than every
other candidate — and was still gated out, because it cannot put several trees behind one
instance. The weighted criteria price adoption; they do not measure fitness. **Nextcloud
passes the gate only on SQLite at 54/100** and was not carried forward on score and fit.
