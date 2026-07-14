---
title: "Common CI Failures (Troubleshooting)"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - troubleshooting
  - ci
  - errors
  - debugging
sources:
  - url: "https://docs.github.com/en/actions/how-tos/troubleshoot-workflows"
    title: "How-tos for GitHub Actions"
last_audit_date: 2026-06-09
---

# Common CI Failures (Troubleshooting)

Frequent issues and their solutions when using GitHub Actions.

## Syntax Errors

```
Invalid workflow file: .github/workflows/ci.yml
The workflow is not valid.
```

**Fix:** Validate locally with `action-validator` or use the GitHub Actions tab editor which validates YAML.

## Permission Denied

```
Error: Resource not accessible by integration
```

**Fix:** Add explicit `permissions:` block:

```yaml
permissions:
  contents: read
  pull-requests: write
```

## uv Not Found

```
Error: uv: command not found
```

**Fix:** Use `astral-sh/setup-uv@v8.2.0` before any `uv` command.

## Step Not Found (Output Reference)

```
The expression 'steps.build.outputs.version' is invalid
```

**Fix:** Ensure the referenced step has an `id:` and the output is written to `$GITHUB_OUTPUT`.

## Reusable Workflow Input Type Mismatch

```
Error: Unable to process input 'timeout': value '15' is not a valid number
```

**Fix:** Ensure input types match — YAML interprets `15` as a number, `"15"` as a string.

## Concurrency Blocking Deploy

```
Deployment waiting for other runs in concurrency group
```

**Fix:** Use unique concurrency groups per environment:

```yaml
concurrency:
  group: deploy-${{ github.ref_name }}
```

## Debug Mode

Enable debug logging for troubleshooting. Set `ACTIONS_STEP_DEBUG` as a repository secret or variable — it **cannot** be set in the workflow `env:` block.

## See Also

- [github-token-permissions.md](./github-token-permissions.md) — Token issues
- [jobs-outputs.md](./jobs-outputs.md) — Output troubleshooting
