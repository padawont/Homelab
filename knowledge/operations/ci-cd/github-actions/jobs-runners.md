---
title: "Job Runners"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - runners
  - ubuntu
sources:
  - url: "https://docs.github.com/en/actions/using-jobs/choosing-the-runner-for-a-job"
    title: "GitHub Actions: Choosing the Runner"
last_audit_date: 2026-06-09
---

# Job Runners

The `runs-on` key selects the runner environment for a job.

## GitHub-Hosted Runners

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
  test:
    runs-on: ubuntu-24.04
  windows:
    runs-on: windows-latest
  macos:
    runs-on: macos-latest
```

| Label | Specs |
|---|---|---|
| `ubuntu-latest` | 4-core CPU, 16 GB RAM, 14 GB SSD (public repos) |
| `ubuntu-24.04` | Same as latest, pinned version |
| `windows-latest` | Windows Server 2025 |
| `macos-latest` | macOS 15 (arm64) |

> **Note:** `ubuntu-latest` on private repos uses 2-core CPU and 8 GB RAM. Public repo specs (4-core, 16 GB) are shown in the table as the most common case for RunicEngines projects.

## Self-Hosted Runners

```yaml
jobs:
  deploy:
    runs-on: [self-hosted, linux, arm64, production]
```

Labels are set when registering the runner. Use `self-hosted` plus custom labels.

## Runner Selection

- Use `ubuntu-latest` for most CI tasks
- Use `windows-latest` / `macos-latest` for cross-platform testing
- Use self-hosted for GPU, ARM, or internal network access
- Self-hosted runners have less strict security — be careful with untrusted PRs

## See Also

- [secrets-org-repo.md](./secrets-org-repo.md) — Runner-level secrets
