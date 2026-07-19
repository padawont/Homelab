---
title: "direnv — Troubleshooting"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["direnv", "troubleshooting", "faq"]
sources:
  - "https://direnv.net/"
  - "https://direnv.net/man/direnv.toml.1.html"
last_audit_date: 2026-05-24
---

# Troubleshooting

| Issue | Solution |
|---|---|
| `direnv: error .envrc is blocked` | Run `direnv allow` to trust the file |
| Aliases not working in `.envrc` | direnv cannot export aliases or functions — use stdlib functions (e.g. `PATH_add`) or `~/.config/direnv/direnvrc` |
| Changes to `.envrc` not picked up | Run `direnv allow` again or whitelist the directory |
| Slow prompt | Avoid slow commands in `.envrc`; use `warn_timeout` in `direnv.toml` to diagnose which commands are slow |
| Environment not unloading after `cd` | Check for parent directory `.envrc` files with `source_up` |
| Noisy export output on every prompt | Set `hide_env_diff = true` in `direnv.toml` to suppress env change diffs |
