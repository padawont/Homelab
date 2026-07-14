---
title: "Job Needs (Dependencies)"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - jobs
  - dependencies
  - needs
sources:
  - url: "https://docs.github.com/en/actions/using-jobs/using-jobs-in-a-workflow#defining-prerequisite-jobs"
    title: "GitHub Actions: Defining Prerequisite Jobs"
last_audit_date: 2026-06-09
---

# Job Needs (Dependencies)

Use `needs` to define job ordering and dependencies.

## Simple Chaining

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Linting..."
  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testing..."
  deploy:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying..."
```

## Parallel + Sequential

Jobs without `needs` run in parallel. Add `needs` to create dependencies:

- `lint` and `check-types` run in parallel
- `test` waits for both
- `deploy` waits for `test`

```yaml
jobs:
  lint:
  check-types:
  test:
    needs: [lint, check-types]
  deploy:
    needs: [test]
```

## Accessing Outputs from Needed Jobs

```yaml
jobs:
  build:
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - id: version
        run: echo "version=1.0.0" >> "$GITHUB_OUTPUT"
  deploy:
    needs: build
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.version }}"
```

See [jobs-outputs.md](./jobs-outputs.md) and [needs-context.md](./needs-context.md).
