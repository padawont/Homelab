---
title: "CLI Usage"
status: draft
author: "Khalid Zubair (refactorartist)"
date: 2026-06-28
tags: [python, type-checker, astral, ty]
sources:
  - url: "https://docs.astral.sh/ty/reference/cli/"
    title: "ty CLI Reference"
  - url: "https://docs.astral.sh/ty/reference/exit-codes/"
    title: "ty Exit Codes"
  - url: "https://github.com/astral-sh/ty"
    title: "ty GitHub Repository"
last_audit_date: 2026-06-28
---

# CLI Usage

ty provides several subcommands for type-checking Python projects and IDE integration.

## Subcommands

| Command | Description |
|---------|-------------|
| `ty check` | Check a project for type errors |
| `ty server` | Start the language server |
| `ty version` | Display ty's version |
| `ty explain` | Explain rules and other parts of ty |
| `ty help` | Print help information |
| `ty generate-shell-completion` | Generate shell completion scripts |

## ty check

The primary type-checking subcommand.

### Basic Usage

Check one or more files or directories for type errors:

```bash
ty check src/
ty check src/main.py src/utils.py
```

If no path is given, ty checks the current directory:

```bash
ty check
```

### Key Options

#### `--python-version`, `--target-version`

Set the Python version to assume when resolving types. Affects allowed syntax, standard library type definitions, and conditional type definitions:

```bash
ty check src/ --python-version 3.12
```

Valid values: `3.7`, `3.8`, `3.9`, `3.10`, `3.11`, `3.12`, `3.13`, `3.14`, `3.15`.

Note: ty officially supports type checking code targeting Python 3.10 and later. Versions `3.7`–`3.9` can still be selected, but ty may produce false positives or false negatives for standard-library APIs because its bundled stubs do not fully describe those versions.

If not specified, ty infers the version from `project.requires-python` in `pyproject.toml`, then from the activated Python environment, and finally falls back to the latest stable Python version supported by ty.

#### `--python-platform`

Target a specific platform for type resolution. Affects platform-specific type definitions (e.g., `sys.platform`, `os.name`):

```bash
ty check src/ --python-platform darwin
```

Valid values: `linux`, `win32`, `darwin`, `android`, `ios`, `all`.

#### `--config`, `-c`

Override individual configuration options from the command line using TOML key-value pairs:

```bash
ty check src/ -c rules.invalid-argument-type=error
```

#### `--extra-search-path`

Add additional directories for module resolution. Useful for first-party or third-party modules not installed in the project's Python environment:

```bash
ty check src/ --extra-search-path ./vendored-libs
```

#### `--output-format`

Control the output format for diagnostic messages. Supported values:

- `full` (default) — Print diagnostics verbosely with context and helpful hints
- `concise` — Print diagnostics concisely, one per line
- `gitlab` — JSON format for GitLab Code Quality reports
- `github` — Format for GitHub Actions workflow error annotations
- `junit` — JUnit-style XML report

```bash
ty check src/ --output-format github
```

#### `--project`

Run the command within the given project directory. `pyproject.toml` files are discovered by walking up from this directory:

```bash
ty check src/ --project /path/to/project
```

#### `--config-file`

Path to a `ty.toml` file to use for configuration. Cannot be a `pyproject.toml`:

```bash
ty check src/ --config-file ty.toml
```

#### `--fix`

Apply fixes to resolve errors automatically:

```bash
ty check src/ --fix
```

#### `--add-ignore`

Add `# ty: ignore` comments to suppress all rule diagnostics:

```bash
ty check src/ --add-ignore
```

#### `--error-on-warning`

Use exit code 1 if there are any warning-level diagnostics:

```bash
ty check src/ --error-on-warning
```

#### `--exit-zero`

Always use exit code 0, even when there are error-level diagnostics:

```bash
ty check src/ --exit-zero
```

#### `--exit-zero-on-warning`

Use exit code 0 if there are no error-level diagnostics:

```bash
ty check src/ --exit-zero-on-warning
```

#### `--watch`, `-W`

Watch files for changes and recheck files related to changed files:

```bash
ty check src/ --watch
```

#### `--python`, `--venv`

Path to the project's Python environment or interpreter for resolving third-party imports:

```bash
ty check src/ --venv .venv
```

#### `--error`, `--warn`, `--ignore`

Override the severity of specific rules from the command line:

```bash
ty check src/ --error unused-import --warn implicit-any
```

#### `--exclude`

Glob patterns for files to exclude from type checking (gitignore-style syntax):

```bash
ty check src/ --exclude 'tests/**' --exclude '*.pyi'
```

#### `--force-exclude`

Enforce exclusions even for paths passed directly on the command line.

#### `--respect-ignore-files`

Respect file exclusions via `.gitignore` and other standard ignore files.

#### `--no-progress`

Hide all progress outputs such as spinners or progress bars.

#### `--help`, `-h`

Print help information.

### Exit Codes

| Code | Description |
|------|-------------|
| 0 | No violations with severity `warning` or higher were found |
| 1 | Violations with severity `warning` or higher were found |
| 2 | Invalid CLI options, invalid configuration, or IO errors |
| 101 | Internal error |

Exit code behavior can be modified with `--exit-zero`, `--error-on-warning`, and `--exit-zero-on-warning`.

## ty server

Start the language server for IDE integration:

```bash
ty server
```

See [Language Server](language-server.md) for details.

## ty version

Display ty's version:

```bash
ty version
```

Supports `--output-format text` (default) or `--output-format json`.

## ty explain

Explain rules and other parts of ty:

```bash
ty explain rule
ty explain rule invalid-argument-type
```

## Environment Variables

### `TY_CONFIG_FILE`

Path to a `ty.toml` configuration file, equivalent to the `--config-file` option:

```bash
TY_CONFIG_FILE=/path/to/ty.toml ty check src/
```

### `TY_OUTPUT_FORMAT`

Default output format for diagnostic messages, equivalent to the `--output-format` option:

```bash
TY_OUTPUT_FORMAT=github ty check src/
```
