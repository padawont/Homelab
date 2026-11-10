---
title: "FileBrowser Quantum for homelab file access"
status: draft
author: "padawont"
date: 2026-11-08
tags: [file-management, self-hosting, storage]
technologies: []
related_ideas: []
---

# FileBrowser Quantum for homelab file access

## Objective

Give the homelab a single browser-based view over its files instead of shell-only
access. Today, reading anything means SSH: the only files inside the cluster live in
the `cv-sender/cv-sender-data` volume, and everything else sits on the host
filesystem. Neither is reachable without a terminal.

A web file manager would make shares, uploads and previews possible from a browser —
no SSH session and no `kubectl cp` just to move a file around.

FileBrowser Quantum (`gtsteffaniak/filebrowser`), an actively developed fork of
Filebrowser, is the starting candidate. It is not a commitment: naming it here only
gives the Knowledge stage something concrete to read against, and the product
comparison belongs to Research.

## Three Source Types

Any solution must be able to surface three kinds of source, not just one:

1. **A dedicated shared volume on the cluster** — a new place for files that should
   live with the workloads rather than on the host.
2. **Selected host directories** — chosen paths from the node's filesystem, not the
   whole disk, exposed read/write as needed.
3. **An existing Longhorn PVC** — the `cv-sender/cv-sender-data` volume, so the data
   already in the cluster becomes browsable in the same UI.

Each source should appear side by side in one view; a solution covering only the first
or only the third would not meet the want.

## Access Model

Fixed by the human, not open for redesign at this stage:

- **Local user accounts** — accounts defined in the file manager itself.
- **Plain HTTP on the LAN** — no TLS termination, no certificates.
- **No SSO, no identity provider.**

This is an accepted risk, recorded rather than endorsed. Cert-manager is present in
the cluster but has no `ClusterIssuer`, so TLS would be extra work this idea
deliberately defers. The homelab LAN is treated as trusted enough for cleartext
traffic; that judgement is the reason the model is acceptable, not a claim that it is
safe in general.

## Possibilities

- One landing page for every file the homelab owns, whether it lives on the host or
  behind a PVC.
- Uploads and downloads from a phone or a laptop without a shell — useful for moving
  large files that are awkward over `kubectl cp`.
- Previews and browsing as a low-effort way to check what is actually on disk.
- A single-node cluster keeps the scope small: no shared-storage coordination, no
  multi-node placement questions, no role model beyond local users.

Platform context for the eventual deployment lives in
`./05_Implementations/node-main/k3s/overview.md` (cluster and ingress entry point) and
`./05_Implementations/node-main/longhorn/overview.md` (block storage and free
capacity). Traffic would reach the UI through the existing Traefik load balancer at
`192.168.111.7`.

## Open Questions

- Which of the three source types is hardest to expose — is a host path or a Longhorn
  PVC the awkward one in practice?
- How should host directories be selected and mounted: one broad path or a small
  allowlist?
- Does the chosen tool handle several distinct sources in one UI, or does each source
  need its own instance?
- What does "read/write as needed" mean per source — which of the three, if any,
  should be read-only?
- Where does authentication live if the idea is later accepted: still local accounts,
  or does the trusted-LAN assumption get revisited first?
- Does the plain-HTTP model survive contact with browser behaviour (credentials over
  cleartext, clipboard and upload APIs)?
