---
title: "Job Outputs"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - jobs
  - outputs
  - data-flow
sources:
  - url: "https://docs.github.com/en/actions/using-jobs/defining-outputs-for-jobs"
    title: "GitHub Actions: Defining Outputs for Jobs"
last_audit_date: 2026-06-09
---

# Job Outputs

Pass data from one job to another using `outputs`.

## Defining Outputs

```yaml
jobs:
  version:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.get-tag.outputs.tag }}
    steps:
      - id: get-tag
        run: echo "tag=v1.2.3" >> "$GITHUB_OUTPUT"
```

## Consuming Outputs

```yaml
jobs:
  deploy:
    needs: version
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying ${{ needs.version.outputs.tag }}"
```

## Multi-Value Outputs

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.meta.outputs.image }}
      digest: ${{ steps.meta.outputs.digest }}
    steps:
      - id: meta
        run: |
          echo "image=ghcr.io/myorg/app:latest" >> "$GITHUB_OUTPUT"
          echo "digest=sha256:abc123" >> "$GITHUB_OUTPUT"
```

## Important Rules

- Outputs are strings only (max 1 MB per job, 50 MB total per workflow run; size approximated based on UTF-16 encoding)
- Use `$GITHUB_OUTPUT` (not `::set-output`, which is deprecated)
- Step IDs are required for referencing step outputs
- The consuming job must list the producer in `needs`
- Outputs containing secrets are automatically redacted on the runner
