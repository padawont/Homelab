---
title: "Workflow Integration — uv, ty, and Devbox"
status: draft
author: "Khalid Zubair (refactorartist)"
date: 2026-06-28
tags: [python, type-checker, astral, ty, uv, devbox, toolchain]
sources:
  - url: "https://docs.astral.sh/ty/"
    title: "ty Documentation"
  - url: "https://docs.astral.sh/uv/"
    title: "uv Documentation"
  - url: "https://www.jetify.com/docs/devbox/"
    title: "Devbox Documentation"
last_audit_date: 2026-06-28
---

# Workflow Integration — uv, ty, and Devbox

In RunicEngines Python projects, three tools compose into a consistent development workflow:

| Tool | Role |
|---|---|
| **Devbox** | Reproducible shell environment — provides Python, uv, and system dependencies |
| **uv** | Python package and project manager — virtual environments, dependency resolution, task running |
| **ty** | Python type checker — validates type correctness using the project's code and dependencies |

## Architecture

```
devbox.json          Declares Python + uv as Nix packages
    |
    v
devbox shell         Activates environment with Python and uv on PATH
    |
    v
uv sync              Creates virtual environment, installs deps (incl. ty --dev)
    |
    v
uv run ty check      Runs ty inside the project's virtual environment
```

## Project Setup

### 1. devbox.json

Declare Python and uv as Devbox packages. Python version must match your target:

```json
{
  "packages": [
    "python@3.12",
    "uv@latest"
  ]
}
```

This pins the Python version and provides uv without requiring a separate installation. For the full `devbox.json` reference, see [tooling/dev-environments/devbox/](../../../tooling/dev-environments/devbox/configuration.md).

### 2. pyproject.toml

Add ty as a dev dependency and configure type checking under `[tool.ty]`:

```toml
[project]
name = "my-project"
requires-python = ">=3.12"

[dependency-groups]
dev = [
    "ty>=0.0.1",
]

[tool.ty]
rules = { all = "error" }
```

Run `uv sync` to install everything into the virtual environment:

```bash
uv sync
```

See [Configuration](configuration.md) for the full `[tool.ty]` reference and [Installation](installation.md) for alternative ty install methods.

### 3. uv scripts (devbox shell scripts)

Wire common commands into `devbox.json` scripts so team members run them the same way:

```json
{
  "shell": {
    "scripts": {
      "check-types": "uv run ty check src/",
      "check-types-watch": "uv run ty check src/ --watch",
      "setup": "uv sync",
      "test": "uv run pytest"
    }
  }
}
```

Usage:

```bash
devbox run setup          # uv sync
devbox run check-types    # uv run ty check src/
devbox run test            # uv run pytest
```

### 4. Pre-commit Hook

Add ty checking as a pre-commit hook so type errors are caught before commits:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ty-pre-commit
    rev: v0.0.55
    hooks:
      - id: ty
```

Or run directly via uv:

```yaml
- repo: local
  hooks:
    - id: ty
      name: ty
      entry: uv run ty check
      language: system
      types: [python]
```

## CI Integration

In CI (GitHub Actions), use the same three-tool stack. Two approaches are available depending on whether the project uses Devbox:

### uv only (no Devbox)

```yaml
steps:
  - uses: astral-sh/setup-uv@v8
    with:
      python-version: "3.13"
  - run: uv sync
  - run: uv run ty check src/ --output-format github
```

### Devbox + uv + ty

```yaml
steps:
  - uses: jetify-com/devbox-install-action@v0.15
    with:
      enable-cache: true
  - run: devbox run -- uv sync
  - run: devbox run -- uv run ty check src/ --output-format github
```

For a full CI reference including caching strategies, matrix builds, and output formats, see [operations/ci-cd/github-actions/python-run-ty.md](../../../operations/ci-cd/github-actions/python-run-ty.md).

## Best Practices

- **Pin Python via devbox, not pyproject.toml alone.** Devbox ensures the exact Python runtime, while `requires-python` in pyproject.toml sets a minimum. Using both ensures reproducibility across environments.
- **Install ty as a dev dependency with uv, not globally.** This keeps the ty version locked to the project and avoids version skew between projects.
- **Use `uv run ty check` rather than bare `ty check`.** This ensures ty uses the correct virtual environment and dependency versions.
- **Use `--watch` during development.** Running `ty check --watch` rechecks files on change and gives near-instant feedback.
- **Keep `devbox.json`, `pyproject.toml`, and `uv.lock` in version control.** The lockfile ensures deterministic dependency resolution across all environments.

## Related Notes

- [Installation](installation.md) — Installing ty via pip, uv, pipx, standalone, and Docker
- [Configuration](configuration.md) — `pyproject.toml` schema for `[tool.ty]`
- [CLI Usage](cli-usage.md) — ty check flags, exit codes, env vars
- [tooling/dev-environments/devbox/](../../../tooling/dev-environments/devbox/configuration.md) — devbox.json reference
- [operations/ci-cd/python-ci-caching/uv-caching-install.md](../../../operations/ci-cd/python-ci-caching/uv-caching-install.md) — uv caching in CI
