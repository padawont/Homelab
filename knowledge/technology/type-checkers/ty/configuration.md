---
title: "Configuration"
status: draft
author: "Khalid Zubair (refactorartist)"
date: 2026-06-28
tags: [python, type-checker, astral, ty]
sources:
  - url: "https://docs.astral.sh/ty/reference/configuration/"
    title: "ty Configuration Reference"
  - url: "https://docs.astral.sh/ty/reference/rules/"
    title: "ty Rules Reference"
  - url: "https://github.com/astral-sh/ty"
    title: "ty GitHub Repository"
last_audit_date: 2026-06-28
---

# Configuration

ty is configured via `pyproject.toml` under the `[tool.ty]` section, or via a standalone `ty.toml` file. Configuration is discovered automatically from the project root.

## Schema

Place configuration in your `pyproject.toml`:

```toml
[tool.ty]
```

Or in a standalone `ty.toml` at the project root (without the `[tool.ty]` wrapper):

```toml
[rules]
possibly-unresolved-reference = "warn"
invalid-argument-type = "error"
```

## Rules

Configure which rules are enabled and their severity using the `[tool.ty.rules]` section:

```toml
[tool.ty.rules]
invalid-argument-type = "error"
missing-argument = "warn"
division-by-zero = "ignore"
```

Use `all` to set a default severity for all rules:

```toml
[tool.ty.rules]
all = "warn"
invalid-argument-type = "error"
```

### Rule Severities

| Severity | Behavior |
|----------|----------|
| `error`  | Enable the rule and create an error diagnostic (exit code 1 by default) |
| `warn`   | Enable the rule and create a warning diagnostic (exit code 1 by default) |
| `ignore` | Disable the rule entirely |

By default, ty exits with code 1 if it emits any `warning` or `error` diagnostics. Set `terminal.error-on-warning` to `false` to exit with code 0 when only warnings remain:

```toml
[tool.ty.terminal]
error-on-warning = false
```

## Environment

Configure the Python environment assumptions:

```toml
[tool.ty.environment]
python-version = "3.12"
python-platform = "linux"
```

### `python-version`

The Python version to assume when resolving types. Affects allowed syntax, standard library definitions, and conditional type definitions. Uses format `"3.12"` (not `"py312"`). If not set, ty infers it from `project.requires-python`, then from the activated environment, then falls back to the latest supported version.

### `python-platform`

Target platform for type resolution. Specializes `sys.platform` and affects visibility of platform-specific functions. Values: `"linux"`, `"win32"`, `"darwin"`, `"android"`, `"ios"`, `"all"` (no platform assumptions). These correspond to the values from `sys.platform`.

### `python`

Path to the project's Python environment or interpreter for resolving third-party imports.

### `typeshed`

Custom directory for stdlib typeshed stubs. Defaults to ty's bundled typeshed.

### `root`

The root of the project, used for finding first-party modules. Accepts a single path string or a list of paths:

```toml
[tool.ty.environment]
root = ["./src", "./lib"]
```

### `extra-paths`

Additional paths to use as module-resolution sources.

## Source Configuration

Control which files and directories are included in type checking under `[tool.ty.src]`:

```toml
[tool.ty.src]
include = ["src/**/*.py"]
exclude = ["tests/**", "**/__pycache__/**"]
root = "src"
respect-ignore-files = true
```

### `include`

Glob patterns for files to include in type checking. Defaults to all `.py` files in the project.

### `exclude`

Glob patterns for files to exclude from type checking. Uses gitignore-style syntax.

Common default excludes include: `.bzr/`, `.direnv/`, `.eggs/`, `.git/`, `.git-rewrite/`, `.hg/`, `.mypy_cache/`, `.nox/`, `.pants.d/`, `.pytype/`, `.ruff_cache/`, `.svn/`, `.tox/`, `.venv/`, `__pypackages__/`, `_build/`, `buck-out/`, `dist/`, `node_modules/`, `venv/`.

### `respect-ignore-files`

Whether to respect `.gitignore` and other standard ignore files. Enabled by default (`true`). Disable with `--no-respect-ignore-files` on the CLI.

### `root` (deprecated)

The root of the project, used for finding first-party modules. Defaults to the project root.

**Deprecated**: Use `[tool.ty.environment].root` instead (see the Environment section above).

## Per-File Overrides

Apply different rule configurations to specific files or directories using `[[tool.ty.overrides]]`:

```toml
[tool.ty.rules]
invalid-argument-type = "error"

[[tool.ty.overrides]]
include = ["tests/**"]
rules = { invalid-argument-type = "warn" }

[[tool.ty.overrides]]
exclude = ["migrations/**"]
rules = { division-by-zero = "error" }
```

Each override can specify:

- `include` — Glob patterns to match files for this override
- `exclude` — Glob patterns to exclude files from this override
- `rules` — Rule severity overrides for matched files
- `analysis` — Analysis settings overrides

## Analysis Settings

```toml
[tool.ty.analysis]
allowed-unresolved-imports = ["legacy_module"]
replace-imports-with-any = ["deprecated_package"]
respect-type-ignore-comments = true
```

- `allowed-unresolved-imports` — Module glob patterns for which `unresolved-import` diagnostics are suppressed
- `replace-imports-with-any` — Modules whose imports are replaced with `Any`
- `respect-type-ignore-comments` — Whether to respect `# type: ignore` comments

## Terminal Output

```toml
[tool.ty.terminal]
error-on-warning = false
output-format = "full"
```

- `error-on-warning` — When `false`, warnings produce exit code 0 instead of 1
- `output-format` — Default output format: `full`, `concise`, `gitlab`, `github`, or `junit`
