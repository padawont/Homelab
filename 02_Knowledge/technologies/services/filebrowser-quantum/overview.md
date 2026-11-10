---
title: "FileBrowser Quantum — overview and lineage"
status: draft
author: "padawont"
date: 2026-11-08
tags: [filebrowser, filebrowser-quantum, file-management, self-hosted]
sources:
  - url: "https://github.com/gtsteffaniak/filebrowser"
    title: "FileBrowser Quantum README (gtsteffaniak/filebrowser)"
  - url: "https://filebrowserquantum.com/en/docs/getting-started/v2/about/"
    title: "About v2.0.0 — FileBrowser Quantum docs"
  - url: "https://filebrowserquantum.com/en/docs/getting-started/linux/"
    title: "Linux install — FileBrowser Quantum docs"
  - url: "https://filebrowserquantum.com/en/docs/changelog/stable/"
    title: "Stable changelog — FileBrowser Quantum docs"
  - url: "https://github.com/gtsteffaniak/filebrowser/releases/tag/v2.0.2-stable"
    title: "v2.0.2-stable release"
last_audit_date: 2026-11-10
related_docs:
  - "./02_Knowledge/technologies/services/filebrowser-quantum/installation.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/configuration.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/authentication.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/sharing-and-permissions.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/operations.md"
  - "./01_Ideas/filebrowser-quantum/idea-filebrowser-quantum.md"
---

# FileBrowser Quantum — overview and lineage

## Overview

FileBrowser Quantum is a self-hosted, browser-based file manager: it exposes
directories that already exist on a server's filesystem through a web UI, with
browsing, uploads, downloads, previews, search and per-user access control. It is
a large fork of the original `filebrowser/filebrowser` project (referred to here
as *classic Filebrowser*), maintained by gtsteffaniak and distributed under
Apache-2.0. Quantum ships as a single Go binary with the web UI embedded, as does
classic Filebrowser, but the fork has diverged far enough that most
classic-Filebrowser assumptions do not carry over.

- **Project**: `gtsteffaniak/filebrowser`; canonical docs at filebrowserquantum.com
- **Licence**: Apache-2.0 (FileBrowser Quantum)
- **Distribution**: one Go binary with the embedded web UI; a container image is
  also published
- **Current stable line**: v2.0.x — latest stable **v2.0.2-stable**, released
  2026-10-23
- **Verified against**: v2.0.2-stable, docs read 2026-11-08

**Fit in one line** — Quantum fits a homelab that wants a single web view over
several local filesystem paths with real multi-user access control. It does not
fit a need for object storage, a native mobile client, or having the file manager
act as the identity provider. This note describes the product; the adoption
question belongs to the ADR, not here.

## Details

### Lineage: classic Filebrowser → Quantum

- The README calls Quantum "a massive fork of the file browser open-source
  project" and lists the changes as the fork's reason to exist.
- Classic Filebrowser exposes a single source; Quantum exposes several at once,
  each with include/exclude rules. This is the fork's headline difference.
- Quantum's configuration is driven by a `config.yaml` file, which the README
  lists as a fork addition.
- Quantum removes shell commands from the UI completely, and the README states
  they will not return.
- Quantum v2.0.0 (published 2026-07-23) replaced the original key/value database
  with a structured SQLite database plus a write-through state layer, and
  requires a config migration plus a one-time database migration from v1.x.
  Material written for v1.5.x therefore does not describe the current line.

### Licence and distribution shape

- Quantum is Apache-2.0, matching the licence file in the repository.
- It is distributed as a standalone binary with the frontend embedded, and as a
  container image. Quantum's v2 database is embedded SQLite, not a separate
  database server.
- The web UI is a PWA, so it can be installed to a home screen from the browser;
  that is not the same thing as a native app (see below).

### Feature surface (Quantum)

Each item is covered in detail by a sibling note; see `related_docs`.

- **Sources**: multiple filesystem paths in one instance, with include/exclude
  rules and per-source read-only options.
- **Configuration**: a single `config.yaml`, plus CLI, environment variables and
  an API for administration.
- **Authentication**: local password accounts with TOTP 2FA and passwordless
  passkeys, and delegated login via OIDC, LDAP, JWT or a reverse proxy.
- **Authorisation**: access scoped to user or group and source path; v2 adds
  per-source view / download / modify / create / delete permissions, with a
  separate view grant so viewing need not imply downloading.
- **Sharing**: public and upload links, with expiry, optional password, audience
  control and per-share view/edit/upload permissions.
- **Access protocols**: WebDAV in addition to the web UI and HTTP API.
- **API**: long-lived API tokens and a Swagger page at `/swagger`.
- **Search**: indexed, as-you-type search with size filters and advanced search.
- **Presentation**: thumbnails for images, office documents, video, album art and
  3D models; folder sizes; gallery/list views; themes and branding.
- **Operations-facing features**: an activity log with CSV export, and duplicate-file /
  file-size analysis tools; storage quotas arrive in v2.1+.

### Where it does not fit

- **No object storage.** Quantum browses filesystem paths; the README comparison
  table marks S3 support as absent. Files must be present or mounted locally —
  classic Filebrowser is the same in this respect.
- **No native mobile app.** The README table marks a mobile app as absent; the
  browser PWA is the only mobile path.
- **Not an identity provider.** Quantum consumes OIDC/LDAP/JWT/proxy identities
  from elsewhere, or uses its own local accounts. It does not issue identities for
  other services.
- **Docs site is primary; the README is secondary** and may lag behind it. Where
  they disagree, the docs site at filebrowserquantum.com is the reference.
- **A young v2 line.** v2.0.0 was a breaking rewrite in July 2026; v2.0.1 was
  security-only and v2.0.2 mixed security with bug fixes. Guides
  written for v1.5.x or for the first 2.0 release may not match the current one.

### Quick contrast

The classic column is transcribed from the README's comparison chart and was not
independently verified against the classic project.

| Capability | Classic Filebrowser | FileBrowser Quantum |
|---|---|---|
| Sources per instance | single source only | several, with include/exclude rules |
| WebDAV | no | yes |
| SSO (OIDC) / LDAP | no | yes |
| Long-lived API tokens | no | yes |
| Indexed / advanced search | no | yes |
| S3 object storage | no | no |
| Native mobile app | no | no |
| Shell commands in UI | yes | removed, will not return |

## Sources / Further Reading

- FileBrowser Quantum README: https://github.com/gtsteffaniak/filebrowser
- About v2.0.0: https://filebrowserquantum.com/en/docs/getting-started/v2/about/
- Linux install (binary packaging): https://filebrowserquantum.com/en/docs/getting-started/linux/
- Stable changelog: https://filebrowserquantum.com/en/docs/changelog/stable/
- v2.0.2-stable release: https://github.com/gtsteffaniak/filebrowser/releases/tag/v2.0.2-stable
