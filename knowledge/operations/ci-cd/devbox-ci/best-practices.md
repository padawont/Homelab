---
title: "Devbox CI/CD — Best Practices & Troubleshooting"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "ci-cd", "best-practices", "troubleshooting"]
sources:
  - "https://www.jetify.com/docs/devbox/continuous-integration/github-action/"
  - "https://www.jetify.com/docs/devbox/guides/scripts/"
  - "https://www.jetify.com/docs/devbox/cli-reference/devbox-generate-dockerfile/"
  - "https://www.jetify.com/docs/devbox/configuration/"
last_audit_date: 2026-05-24
---

# Best Practices

| Practice | Reason |
|---|---|
| Pin `devbox-version` in CI | Ensures CI uses the same Devbox version as local; update deliberately |
| Enable `enable-cache` | Significantly improves CI build times on cache hits |
| Define scripts in `devbox.json` | Reusable between local and CI — `devbox run test` works everywhere |
| Use `devbox.lock` in VCS | Ensures reproducible installs across all environments |
| Set `CI=true` via `--env` | Makes scripts behave differently in CI (e.g., skip interactive prompts) |
| Test local before pushing | `devbox run test` locally matches CI exactly |
| Avoid platform-specific packages in CI | Use `platforms` / `excluded_platforms` in `devbox.json` if needed |
| Generate Dockerfile for production | Reuse the same `devbox.json` for both dev and production images |

# Troubleshooting

| Issue | Solution |
|---|---|
| Cache not hitting | Ensure `devbox.lock` is committed; clear cache via GitHub Actions UI |
| Nix build timeout | Large packages may need longer than default runner limits; use a Cachix cache for prebuilt binaries |
| `permission denied` on `/nix` | Ensure runner has sudo-less Nix support; the action handles this automatically |
| Different behavior locally vs CI | Check environment variables; use `devbox run --env CI=true` to replicate |
| Git LFS / large monorepos | Bundle devbox.json + devbox.lock in a single folder; use `project-path` input |
