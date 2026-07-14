---
title: "Devbox CI/CD"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "ci-cd", "github-actions", "nix-caching"]
sources:
  - "https://www.jetify.com/docs/devbox/continuous-integration/github-action/"
  - "https://www.jetify.com/docs/devbox/cli-reference/devbox-generate-dockerfile/"
  - "https://www.jetify.com/docs/devbox/installing-devbox/"
last_audit_date: 2026-05-24
---

# Devbox CI/CD

Using Devbox in CI/CD pipelines ensures parity between local and CI environments — the same `devbox.json` that defines your local toolchain also provisions the exact same tools in CI.

## Detailed Guides

| File | Description |
|---|---|
| [github-actions.md](./github-actions.md) | Setup, workflows, action inputs reference |
| [running-commands.md](./running-commands.md) | Commands and scripts in CI |
| [caching.md](./caching.md) | Built-in cache, Cachix, and manual caching |
| [dockerfile.md](./dockerfile.md) | Containerized CI with Docker |
| [other-platforms.md](./other-platforms.md) | GitLab CI, CircleCI, and other runners |
| [best-practices.md](./best-practices.md) | Best practices and troubleshooting |
