---
title: "direnv — Configuration"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["direnv", "configuration", "whitelist", "direnv-toml"]
sources:
  - "https://direnv.net/man/direnv.toml.1.html"
last_audit_date: 2026-05-24
---

# Configuration

## Whitelisting (Automatic Trust)

Instead of running `direnv allow` every time `.envrc` changes, you can whitelist a directory in `~/.config/direnv/direnv.toml`:

```toml
[whitelist]
prefix = [ "/absolute/path/to/project" ]
```

Or exact paths:

```toml
[whitelist]
exact = [ "/home/user/project-a/.envrc" ]
```

**Caution:** Anyone who can write files to a whitelisted directory can execute arbitrary code on your machine.

## direnv.toml

Located at `~/.config/direnv/direnv.toml`:

```toml
[global]
load_dotenv = true          # also load .env files automatically
strict_env = true           # set -euo pipefail for .envrc
hide_env_diff = true        # suppress env change output
warn_timeout = "5s"         # warn if eval takes too long
bash_path = "/run/current-system/sw/bin/bash"  # hardcode bash path
disable_stdin = true        # redirect stdin to /dev/null during eval
```
