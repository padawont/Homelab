---
title: "direnv — CLI Reference"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["direnv", "cli", "reference"]
sources:
  - "https://direnv.net/man/direnv.1.html"
last_audit_date: 2026-05-24
---

# CLI Reference

| Command | Description |
|---|---|
| `direnv allow [<path>]` | Grant permission to load an `.envrc` or `.env` |
| `direnv deny [<path>]` | Revoke authorization |
| `direnv edit [<path>]` | Open in `$EDITOR` and auto-allow |
| `direnv exec <dir> <cmd> [<args>]` | Execute command with arguments after loading the dir's `.envrc` |
| `direnv reload` | Trigger an environment reload |
| `direnv status` | Print debug status information |
| `direnv prune` | Remove old allowed-file records |
| `direnv stdlib` | Print the stdlib script |
| `direnv hook <shell>` | Generate shell hook code |
| `direnv export <shell>` | Load env and print diff for the given shell |
| `direnv fetchurl <url> [<integrity-hash>]` | Fetch a URL into direnv's content-addressed storage |
| `direnv help` | Show help |
| `direnv version` | Print version |
