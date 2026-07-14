---
title: "Suppression"
status: draft
author: "Khalid Zubair (refactorartist)"
date: 2026-06-28
tags: [python, type-checker, astral, ty]
sources:
  - url: "https://docs.astral.sh/ty/suppression/"
    title: "ty Suppression Documentation"
  - url: "https://github.com/astral-sh/ty"
    title: "ty GitHub Repository"
last_audit_date: 2026-06-28
---

# Suppression

ty provides multiple mechanisms for suppressing diagnostics, from fine-grained inline comments to broad project-level configuration.

## ty Suppression Comments

Suppress a specific rule violation on a line using a `# ty: ignore[<rule>]` comment:

```python
a = 10 + "test"  # ty: ignore[unsupported-operator]
```

Enumerating the rule name (e.g., `unsupported-operator`) is optional but strongly recommended to avoid accidentally suppressing other errors. A bare `# ty: ignore` without a rule name suppresses all diagnostics on that line.

### Multi-Line Suppression

For violations spanning multiple lines, add the comment at the end of the first or last line:

```python
# On the first line
sum_three_numbers(  # ty: ignore[missing-argument]
    3,
    2
)

# Or on the last line
sum_three_numbers(
    3,
    2
)  # ty: ignore[missing-argument]
```

### Multiple Rule Suppression

Suppress multiple violations on the same line by comma-separating rule names:

```python
sum_three_numbers("one", 5)  # ty: ignore[missing-argument, invalid-argument-type]
```

### File-Level Suppression

To suppress specific rules for an entire file, place a `# ty: ignore[<rule>]` comment on its own line before any Python code:

```python
# ty: ignore[invalid-argument-type]

def process():
    do_something(1, "bad", True)
```

## Standard Suppression Comments

ty supports the standard `# type: ignore` comment format introduced by PEP 484:

```python
# Ignore all typing errors on this line
sum_three_numbers("one", 5)  # type: ignore
```

`type: ignore[ty:<rule>]` behaves like `ty: ignore[<rule>]` and only suppresses the matching rule. Codes without a `ty:` prefix are ignored, enabling combined suppressions for multiple type checkers in one comment:

```python
# Suppress a mypy code and a ty rule in the same comment
sum_three_numbers("one", 5, 2)  # type: ignore[arg-type, ty:invalid-argument-type]
```

## Multiple Suppression Comments

To suppress a typing error on a line that already has a suppression comment from another tool (such as `# fmt: skip`), add `# ty: ignore` to the same line:

```python
result = calculate()  # ty: ignore[invalid-argument-type]  # fmt: skip
```

## @no_type_check Directive

ty supports the `@no_type_check` decorator to suppress all violations inside a function:

```python
from typing import no_type_check

@no_type_check
def main():
    sum_three_numbers(1, 2)  # no error for the missing argument
```

Decorating a class with `@no_type_check` is not supported.

## Unused Suppression Detection

If the `unused-ignore-comment` rule is enabled, ty reports `# ty: ignore` and `# type: ignore` comments that no longer suppress any violations:

```toml
[tool.ty.rules]
unused-ignore-comment = "error"
```

`unused-ignore-comment` violations can only be suppressed using `# ty: ignore[unused-ignore-comment]`. They cannot be suppressed using bare `# ty: ignore` or `# type: ignore`.

## Project-Level Suppression

To disable a rule entirely across the project, set it to `"ignore"` in the rules configuration:

```toml
[tool.ty.rules]
division-by-zero = "ignore"
```

## Best Practices

- **Prefer targeted suppression**: Use `# ty: ignore[rule-name]` over bare `# ty: ignore` to avoid masking unrelated errors.
- **Document why**: Add a brief comment explaining why the suppression is necessary:

  ```python
  x: int = get_value()  # ty: ignore[invalid-assignment] — third-party library has incorrect stubs
  ```

- **Use per-file overrides for noisy files**: Configure `[[tool.ty.overrides]]` in configuration to relax specific rules in test files or generated code rather than suppressing inline.
- **Enable unused-ignore-comment**: Keep suppression comments clean by enabling this rule to detect stale suppressions.
