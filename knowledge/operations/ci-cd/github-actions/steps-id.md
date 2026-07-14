---
title: "Step IDs"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - steps
  - ids
  - outputs
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsid"
    title: "GitHub Actions: steps.id"
last_audit_date: 2026-06-09
---

# Step IDs

Step IDs provide a unique identifier to reference step outputs and results.

## Basic Usage

```yaml
steps:
  - id: version
    run: echo "app_version=1.0.0" >> "$GITHUB_OUTPUT"

  - id: build
    run: echo "image_id=abc123" >> "$GITHUB_OUTPUT"

  - name: Use outputs
    run: |
      echo "Version: ${{ steps.version.outputs.app_version }}"
      echo "Image: ${{ steps.build.outputs.image_id }}"
```

## Accessing Step Results

```yaml
steps:
  - id: lint
    continue-on-error: true
    run: uv run ruff check

  - name: Check lint result
    if: steps.lint.outcome == 'failure'
    run: echo "Linting had errors, but continuing..."
```

## Use Cases

- Passing values to [jobs-outputs.md](./jobs-outputs.md)
- Referencing in `if:` conditionals
- Generating unique names per matrix combination
- Marking steps for other tooling to parse

## Rules

- IDs must be unique within a job
- IDs use lowercase with hyphens (kebab-case)
- Use `${{ steps.<id>.outputs.<name> }}` to reference outputs
- Use `${{ steps.<id>.outcome }}` to get step result (before `continue-on-error`)
- Use `${{ steps.<id>.conclusion }}` to get step result (after `continue-on-error`)
