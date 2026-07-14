# ty

ty is Astral's Python type checker and language server, written in Rust. It aims to be 10x-100x faster than existing type checkers like mypy and Pyright while maintaining broad compatibility with Python's type system. ty is currently in beta.

## Files

- [Installation](installation.md) — Pip, pipx, uv, uvx, standalone binary, and Docker installation methods
- [CLI Usage](cli-usage.md) — Command-line usage, flags, exit codes, and environment variables
- [Configuration](configuration.md) — pyproject.toml schema, rule levels, overrides, target version, and exclusions
- [Type System](type-system.md) — Redeclarations, intersection types, type narrowing, gradual typing, generics, and protocols
- [Diagnostics](diagnostics.md) — Rule-based error codes, contextual output, formatting options, and fix suggestions
- [Language Server](language-server.md) — LSP capabilities including go-to-definition, hover, completions, code actions, and inlay hints
- [Suppression](suppression.md) — Inline suppression comments, per-file suppression, standard `type: ignore`, and `@no_type_check`
- [Workflow Integration](workflow-integration.md) — Using ty with uv and Devbox in a RunicEngines Python project
