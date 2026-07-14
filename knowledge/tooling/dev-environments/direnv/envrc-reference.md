---
title: "direnv — .envrc Reference"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["direnv", "envrc", "security"]
sources:
  - "https://direnv.net/man/direnv.1.html"
last_audit_date: 2026-05-24
---

# The `.envrc` File

An `.envrc` is a bash file that exports environment variables. It is evaluated by direnv whenever you enter the directory.

## Quick Demo

```bash
mkdir ~/my-project && cd ~/my-project
echo export FOO=foo > .envrc
# direnv blocks it by default — security mechanism
direnv allow .
# direnv: loading .envrc
# direnv: export +FOO
echo $FOO  # foo
cd ..
echo $FOO  # (unset)
```

## Security Model

direnv does **not** load `.envrc` files automatically. You must explicitly trust a file with:

```bash
direnv allow .
```

Revoke trust with:

```bash
direnv deny .
```

Edit and auto-allow a file:

```bash
direnv edit .envrc
```
