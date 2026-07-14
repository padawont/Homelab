---
title: "Devbox — Best Practices & Common Pitfalls"
status: draft
author: "Ryan Harris (padawont)"
date: 2026-06-17
tags: ["devbox", "best-practices", "pitfalls", "security"]
sources:
  - "https://www.jetify.com/docs/devbox/configuration/"
  - "https://www.jetify.com/docs/devbox/faq/"
  - "https://www.jetify.com/docs/devbox/guides/pinning-packages/"
last_audit_date: 2026-06-17
---

# Devbox — Best Practices & Common Pitfalls

## Pinning Nixpkgs with Custom Inputs

When you need a specific nixpkgs commit (for newer packages, compatibility, or project-wide version lock), use the `inputs` field in `devbox.json`:

```json
{
  "packages": ["my-package@latest"],
  "inputs": {
    "nixpkgs": {
      "github": "NixOS/nixpkgs/9c6fb5421a9b5f053e45ab22dbca92be5a2464c4"
    }
  }
}
```

This overrides the default nixpkgs channel with the exact commit specified. All packages resolved from that input will use the same commit, ensuring reproducible environments across the team.

See [configuration.md](./configuration.md) for the full `inputs` schema and additional input sources.

## Do Not Edit `devbox.lock` by Hand

`devbox.lock` is auto-generated and records exact Nix commit hashes for every package in your project. Hand-editing it will cause hash mismatches, failed builds, and unreproducible environments.

- To update packages: use `devbox update`
- To add/remove packages: use `devbox add` / `devbox rm`
- The lock file belongs in source control but should never be manually modified

## Do Not Store Secrets in Shell Hooks

`devbox.json` is committed to source control. Hard-coding secrets in `init_hook` or `shell_hook` leaks credentials to every contributor and anyone with repository access.

```json
{
  "shell": {
    "init_hook": ["export DB_PASSWORD=s3cret"]
  }
}
```

Instead:
- Use `.env` files loaded via `"env_from": ".env"` in `devbox.json` (add `.env` to `.gitignore`)
- Use Jetify Secrets for cloud-managed secrets
- Use environment variables set at the system or CI level

See [configuration.md](./configuration.md) for `env_from` and environment variable configuration.

## Do Not Skip init_hook When System Setup Is Needed

If your project requires symlinks, database initialization, config file generation, or other setup steps, put them in `init_hook`. Omitting it forces every developer to discover and run these steps manually — defeating the reproducibility goal of Devbox.

```json
{
  "shell": {
    "init_hook": [
      "ln -sf ../../config/development.yaml config.yaml",
      "mkdir -p data/ uploads/",
      "test -f .env || cp .env.example .env"
    ]
  }
}
```

See [configuration.md](./configuration.md) for the `init_hook` syntax and ordering relative to other shell hooks.
