---
title: "Diagnostics"
status: draft
author: "Khalid Zubair (refactorartist)"
date: 2026-06-28
tags: [python, type-checker, astral, ty]
sources:
  - url: "https://docs.astral.sh/ty/features/diagnostics/"
    title: "ty Diagnostics Documentation"
  - url: "https://docs.astral.sh/ty/reference/rules/"
    title: "ty Rules Reference"
  - url: "https://github.com/astral-sh/ty"
    title: "ty GitHub Repository"
last_audit_date: 2026-06-28
---

# Diagnostics

ty provides rich diagnostic output when it detects type errors, designed for both human readability and machine parsing.

## Rule Names Instead of Numeric Codes

ty uses descriptive rule names rather than numeric error codes. Each diagnostic is identified by a kebab-case name that describes the violation:

```
invalid-argument-type      — Argument type does not match parameter type
invalid-assignment         — Value type does not match variable type
missing-argument           — Required argument not provided
unsupported-operator       — Operator not supported for the given types
invalid-return-type        — Return type does not match annotation
unresolved-import          — Import could not be resolved
```

See the [Rules Reference](https://docs.astral.sh/ty/reference/rules/) for the full list of supported rules.

## Contextual Diagnostic Output

ty shows the relevant source code snippet alongside each diagnostic, with the problematic span highlighted:

```
error[invalid-argument-type]: Argument type mismatch
  --> src/utils.py:25:13
   |
25 |     result = process("abc", 42)
   |                      ^^^^^ expected `int`, got `str`
26 |     return result
```

The contextual display includes:

- File path, line number, and column position
- The affected source line(s)
- A caret (`^`) underline highlighting the exact span
- The expected vs actual types
- A human-readable message explaining the issue

## Fix Suggestions

For diagnostics where ty can automatically resolve the issue, the output includes a suggestion or fix:

```
error[missing-argument]: Missing argument
  --> src/main.py:5:1
   |
 5 | def get_name() -> str:
   |               ^^^^^^^ add return type
   |
   = suggestion: Add return type annotation
```

Use `ty check --fix` to apply fixes automatically, or use the language server's code actions to apply individual fixes.

## Output Formats

ty supports multiple output formats controlled by `--output-format`:

### Full (Default)

Verbose output with context and helpful hints:

```bash
ty check src/
```

```
error[invalid-argument-type]: Argument type mismatch
  --> src/main.py:10:5
   |
10 | x: int = "hello"
   |         ^^^^^^^^ expected `int`, got `str`
```

### Concise

One-line-per-diagnostic format:

```bash
ty check src/ --output-format concise
```

```
src/main.py:10:5: TY: invalid-argument-type: expected `int`, got `str`
src/utils.py:25:13: TY: missing-argument: missing argument `name`
```

### GitHub

Format for GitHub Actions workflow annotations:

```bash
ty check src/ --output-format github
```

### GitLab

JSON format for GitLab Code Quality reports:

```bash
ty check src/ --output-format gitlab
```

### JUnit

JUnit-style XML report for CI integration:

```bash
ty check src/ --output-format junit
```

## Diagnostic Categories

ty groups diagnostics into categories. Each category has a prefix and covers related checks:

| Category | Example Rules |
|----------|--------------|
| Type errors | `invalid-argument-type`, `invalid-assignment`, `invalid-return-type` |
| Import errors | `unresolved-import`, `conflicting-declarations` |
| Annotation errors | `missing-argument`, `invalid-type-form`, `invalid-type-arguments` |
| Name errors | `unresolved-attribute`, `unresolved-reference` |
| Control flow | `unsupported-operator`, `index-out-of-bounds`, `division-by-zero` |
| Configuration | Invalid config or missing file errors at startup |

## Unused Suppression Detection

Enabling the `unused-ignore-comment` rule reports `ty: ignore` and `type: ignore` comments that no longer suppress any violations. This helps keep suppression comments clean as code evolves.
