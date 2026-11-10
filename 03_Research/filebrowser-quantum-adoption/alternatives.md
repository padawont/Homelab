---
title: "Alternatives index — FileBrowser Quantum comparison"
status: draft
author: "padawont"
date: 2026-11-10
tags: [filebrowser-quantum, file-management, research, comparison]
sources:
  - knowledge: "./02_Knowledge/technologies/services/filebrowser-quantum/overview.md"
references:
  - url: "https://github.com/gtsteffaniak/filebrowser"
    title: "FileBrowser Quantum repository"
last_audit_date: 2026-11-10
related_docs: []
---

# Alternatives index — FileBrowser Quantum comparison

| Technology | File | Score | Gate | Status |
|---|---|---|---|---|
| FileBrowser Quantum | ./alternative-filebrowser-quantum.md | 97/100 | Passes | Recommended |
| classic Filebrowser | ./alternative-filebrowser-classic.md | 100/100 | **Disqualified** — one root per instance; upstream archived 2026-09-01, no further security fixes | Not carried forward — gated out and unmaintained |
| SFTPGo | ./alternative-sftpgo.md | 92/100 | Passes | Runner-up |
| Nextcloud | ./alternative-nextcloud.md | 54/100 | Passes (SQLite allowed for minimal instances) | Not carried forward — score and fit |
| Filestash | ./alternative-filestash.md | 90/100 | Passes | Close third |

## How to read the scores

- Three weighted criteria decide the score: **C1 dedicated shared volume (40%)**,
  **C2 host directories (35%)**, and **C3 footprint ≤ ~1 Gi (25%)**. Every candidate also
  states its position on the existing read-only PVC, but that capability is recorded for
  none of them — it is context, not a scored criterion.
- The **gate is absolute**. classic Filebrowser scores a perfect 100/100 and still loses,
  because it cannot put several trees behind one instance — the requirement issue #811
  calls a hard requirement. A high score prices adoption; it does not measure fitness.
- Three disqualifiers sink a candidate regardless of arithmetic: it **requires a database
  the homelab does not run**, it **requires SSO to function**, or it **cannot present
  several trees in one instance**. classic Filebrowser is the only candidate failing the
  multi-source gate, and its upstream is archived.
- Image sizes are Docker Hub **compressed** sizes measured 2026-11-10, except FileBrowser
  Quantum's vendor-published **180 MB with FFmpeg**.
- These scores are the **research input**; the ADR records the decision, and nothing in
  this index or the candidate files asserts one.
