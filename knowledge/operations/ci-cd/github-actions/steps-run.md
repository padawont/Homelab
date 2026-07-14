---
title: "Steps: run (Shell Commands)"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - github-actions
  - steps
  - shell
sources:
  - url: "https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsrun"
    title: "GitHub Actions: steps.run"
last_audit_date: 2026-06-09
---

# Steps: run (Shell Commands)

The `run` keyword executes shell commands inside the runner.

## Basic Usage

```yaml
steps:
  - run: echo "Hello, world!"
  - run: ls -la
  - run: uv run pytest
```

## Multi-Line Commands

```yaml
steps:
  - run: |
      echo "Building project..."
      uv sync
      uv build
```

## Shell Selection

```yaml
steps:
  - run: echo "Using default bash"
    shell: bash

  - run: Get-ChildItem
    shell: pwsh

  - run: echo "Using Python"
    shell: python {0}
```

## Exit Codes and Error Handling

- Non-zero exit codes fail the step by default
- Use `|| true` or `set +e` to allow failures
- Use `continue-on-error: true` for non-blocking steps

## Best Practices

- Use `uv run` for Python commands (not `uvx` for project commands)
- Use `uvx` for one-off tools (e.g., `uvx ruff check`)
- Keep commands readable — use multi-line for complex scripts
