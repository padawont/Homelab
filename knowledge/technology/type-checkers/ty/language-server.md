---
title: "Language Server"
status: draft
author: "Khalid Zubair (refactorartist)"
date: 2026-06-28
tags: [python, type-checker, astral, ty]
sources:
  - url: "https://docs.astral.sh/ty/features/language-server/"
    title: "ty Language Server Documentation"
  - url: "https://github.com/astral-sh/ty"
    title: "ty GitHub Repository"
last_audit_date: 2026-06-28
---

# Language Server

ty includes a built-in language server that implements the Language Server Protocol (LSP), providing IDE integration for real-time type checking and editor features.

## Starting the LSP

Start the language server using the `ty server` subcommand:

```bash
ty server
```

The server communicates over stdin/stdout using the LSP protocol, which is the standard transport for most editor integrations.

## Editor Integration

Configure your editor to use ty as the Python language server.

### VS Code

Set the Python language server in `settings.json`:

```json
{
  "python.languageServer": "ty"
}
```

Additional ty-specific settings:

- `ty.path` — Path to the ty binary
- `ty.configuration` — Server configuration options
- `ty.diagnosticMode` — `"openFilesOnly"` (default), `"workspace"`, or `"off"`

### Neovim (vim-lsp or coc.nvim)

```vim
" coc.nvim example
: CocConfig
{
  "languageserver": {
    "ty": {
      "command": "ty",
      "args": ["server"],
      "filetypes": ["python"]
    }
  }
}
```

### Emacs (eglot)

```elisp
(add-to-list 'eglot-server-programs '(python-mode "ty" "server"))
```

### Helix

Add to your `languages.toml`:

```toml
[language-server.ty]
command = "ty"
args = ["server"]

[[language]]
name = "python"
language-servers = ["ty"]
```

## Capabilities

The ty language server implements the following LSP features:

### Diagnostics

ty reports type errors and other diagnostics directly in the editor. Diagnostics are updated as you type. Supports both pull and push diagnostic models:

- **Pull model** (preferred by most modern editors): Diagnostics are fetched on demand
- **Push model**: Diagnostics are pushed after every change

Use the `diagnosticMode` setting to control whether diagnostics are shown for open files only (`"openFiles"`) or the entire workspace (`"workspace"`).

### Code Navigation

- **Go to Definition**: Jump to where a symbol is defined — resolves imports, function calls, class references
- **Go to Declaration**: Navigate to the declaration site of a symbol (may differ from definition, e.g., in a stub file)
- **Go to Type Definition**: Navigate to the type of a symbol
- **Find All References**: Find every usage of a symbol across the entire workspace
- **Document and Workspace Symbols**: Outline of symbols in the current file, or search across the workspace

### Code Completions

Intelligent code completions as you type, offering suggestions for variables, functions, classes, and modules that are in scope. For symbols not yet imported, ty suggests auto-import actions.

### Code Actions and Refactorings

Quick fixes and code actions to resolve issues:

- **Add import**: Automatically add missing import statements
- **Quick fixes**: Apply fix suggestions for diagnostics
- **Rename symbol**: Safely rename symbols across the entire codebase
- **Selection range**: Expand or shrink text selection based on Python syntax understanding

### Contextual Information

- **Hover**: Display type, documentation, function signatures, and variance of type parameters
- **Inlay Hints**: Show inline type hints for variables and parameters without explicit annotations, plus parameter names at call sites. Double-click to insert annotations into source code
- **Signature Help**: Display function parameters and types when typing `(`
- **Document Highlight**: Highlight all occurrences of the symbol under the cursor
- **Semantic Highlighting**: Syntax highlighting based on underlying semantics and types

### Code Folding

Python-specific code folding ranges, including tagging docstrings as comment blocks for actions like "fold all comment blocks."

### Notebook Support

Jupyter notebooks (`.ipynb` files) are supported with full language server features. Each cell is analyzed in context, with diagnostics, completions, and other features working across cells.

### Fine-Grained Incrementality

ty's architecture is designed for low-latency updates. When you make a change in your editor, ty incrementally updates only the affected parts of the codebase. This happens at a fine-grained level, down to individual definitions, providing feedback within milliseconds even on large projects.

## Feature Reference

| Feature | Status |
|---------|--------|
| Diagnostics (pull/push) | Supported |
| Go to Definition | Supported |
| Go to Declaration | Supported |
| Go to Type Definition | Supported |
| Find References | Supported |
| Document Symbols | Supported |
| Workspace Symbols | Supported |
| Completions | Supported |
| Hover | Supported |
| Inlay Hints | Supported |
| Signature Help | Supported |
| Code Actions | Supported |
| Rename Symbol | Supported |
| Selection Range | Supported |
| Document Highlight | Supported |
| Semantic Tokens | Supported |
| Code Folding | Supported |
| Call Hierarchy | Supported |
| Type Hierarchy | Supported |
| Notebook Support | Supported |
| Code Lens | Not supported |
| Document Color | Not supported |
| Document Link | Not supported |
| Go to Implementation | Not supported (tracked in [#3514](https://github.com/astral-sh/ty/issues/3514)) |
| Document Formatting | Use [Ruff](https://docs.astral.sh/ruff/) |
| On-Type Formatting | Use [Ruff](https://docs.astral.sh/ruff/) |
| Will Rename Files | Not supported (tracked in [#1560](https://github.com/astral-sh/ty/issues/1560)) |
