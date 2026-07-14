---
title: "Type Check with ty in GHA"
status: draft
author: "Khalid Zubair (refactorartist)"
date: 2026-06-28
tags:
  - python
  - ty
  - type-checking
  - uv
  - devbox
sources:
  - url: "https://docs.astral.sh/ty/"
    title: "ty Documentation"
  - url: "https://docs.astral.sh/ty/reference/cli/"
    title: "ty CLI reference"
  - url: "https://github.com/astral-sh/setup-uv"
    title: "astral-sh/setup-uv"
  - url: "https://github.com/jetify-com/devbox-install-action"
    title: "devbox-install-action"
last_audit_date: 2026-06-28
---

# Type Check with ty in GHA

Run ty for static type checking using `uv run` in GitHub Actions. Two approaches are supported depending on whether the project uses Devbox for environment management.

## Approach 1: uv only (no Devbox)

For projects that use uv directly without Devbox:

```yaml
name: Type Check

on: push

jobs:
  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v8
        with:
          python-version: "3.13"
      - run: uv sync
      - run: uv run ty check src/
```

### With Caching

```yaml
steps:
  - uses: astral-sh/setup-uv@v8
    with:
      python-version: "3.13"
      enable-cache: true
  - run: uv sync
  - run: uv run ty check src/
```

The uv cache is scoped to the lockfile hash. See [python-cache-uv.md](./python-cache-uv.md) for advanced caching strategies and [uv-caching-install.md](../python-ci-caching/uv-caching-install.md) for the full caching reference.

## Approach 2: Devbox + uv + ty

For projects that use Devbox to manage the toolchain:

```yaml
name: Type Check

on: push

jobs:
  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - name: Install Devbox
        uses: jetify-com/devbox-install-action@v0.15
        with:
          enable-cache: true

      - name: Install dependencies
        run: devbox run -- uv sync

      - name: Type check
        run: devbox run -- uv run ty check src/
```

The `devbox run --` prefix ensures ty runs inside the Devbox shell with the correct Python version and uv from `devbox.json`. The Devbox action caches the Nix store based on `devbox.lock`, so package installation is fast on cache hits.

For a full Devbox CI reference, see [../devbox-ci/github-actions.md](../devbox-ci/github-actions.md).

## With Strict Mode

```yaml
steps:
  - run: uv run ty check src/ --error all
```

## With Configuration File

If `pyproject.toml` configures `[tool.ty]`, no CLI flags are needed:

```yaml
steps:
  - run: uv run ty check
```

ty discovers configuration from `pyproject.toml` in the project root automatically. See [Configuration](../../../technology/type-checkers/ty/configuration.md) for the full schema.

## Cache ty's Incremental Analysis

ty maintains internal state across runs to speed up rechecks, but its cache path is **not yet documented or stable**. Do not attempt to cache ty's internal state — version skew may cause incorrect results.

Instead, focus on caching uv's dependency cache so `uv sync` is fast:

```yaml
steps:
  - uses: astral-sh/setup-uv@v8
    with:
      enable-cache: true
  - run: uv sync
  - run: uv run ty check src/
```

See [python-cache-uv.md](./python-cache-uv.md) for uv caching strategies.

## Output Format for CI

Use GitHub Actions annotations for inline error reporting:

```yaml
steps:
  - run: uv run ty check src/ --output-format github
```

This formats diagnostics as GitHub Actions workflow commands, rendering them inline on the file and line in the PR's Files Changed tab.

Other formats useful in CI:

| Format | Use Case |
|---|---|
| `github` | Annotations in PR and file view |
| `gitlab` | GitLab Code Quality reports |
| `junit` | Test-report-style XML for other CI systems |
| `concise` | Compact one-line-per-diagnostic output |

## Matrix: Multiple Python Versions

```yaml
jobs:
  type-check:
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: astral-sh/setup-uv@v8
        with:
          python-version: ${{ matrix.python-version }}
      - run: uv sync
      - run: uv run ty check src/
```

ty checks source compatibility against the target version set in `pyproject.toml` or `--python-version`. The matrix ensures the project type-checks correctly across all supported Python versions.

## Best Practices

- Run ty after ruff to avoid formatting-related false positives. See [python-run-ruff.md](./python-run-ruff.md).
- Pin ty as a dev dependency in `pyproject.toml` so CI matches local versions.
- Use `--output-format github` on pull request workflows for inline annotations.
- The `--watch` flag is not needed in CI — the runner executes a single pass.
- Fail fast with `--error all` to treat all diagnostics as errors.
- If using Devbox, always pass `enable-cache: true` to the devbox-install-action to avoid rebuilding the Nix store on every run.

## See Also

- [python-run-mypy.md](./python-run-mypy.md) — Type-check with mypy (alternative)
- [python-run-ruff.md](./python-run-ruff.md) — Linting with ruff
- [python-setup-uv.md](./python-setup-uv.md) — Python and uv setup
- [python-cache-uv.md](./python-cache-uv.md) — uv caching strategies
- [Workflow Integration](../../../technology/type-checkers/ty/workflow-integration.md) — Using ty with uv and Devbox locally
