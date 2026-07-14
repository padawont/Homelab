---
title: "Coverage Analysis"
status: draft
author: "Khalid Zubair"
date: 2026-06-14
tags:
  - documentation
  - coverage-analysis
  - api-documentation
  - code-analysis
sources:
  - url: "https://diataxis.fr/"
    title: "Diátaxis — The four types of documentation"
  - url: "https://www.writethedocs.org/guide/docs-as-code/"
    title: "Write the Docs — Docs as code"
last_audit_date: 2026-06-14
---

# Coverage Analysis

Coverage analysis measures what is documented versus what exists in code. It answers the question: "For every public surface of our codebase, is there corresponding documentation?" This directly supports the **completeness** dimension of Diátaxis functional quality — ensuring no public API, configuration option, or CLI flag is left undocumented.

## What to Measure

| Dimension | Source of Truth | Documentation Target |
|---|---|---|
| **API endpoints** | Route definitions (OpenAPI, Express routers, Django URL conf) | API reference docs |
| **Configuration options** | Config schema, environment variables, CLI flags | Configuration reference |
| **CLI commands & flags** | CLI framework definitions (argparse, clap, cobra, typer) | CLI reference |
| **Public API exports** | Module `__init__` files, `index.js` barrels, `pub` items | API documentation |
| **Database schema** | Migration files, ORM models, SQL DDL | Data model reference |
| **Environment variables** | `.env.example`, config parsing code | Environment reference |

## Techniques

### Parse source for exports

Use language-appropriate reflection or AST parsing to build a canonical list of public surfaces:

```python
# Python: inspect public names in a module
import mypackage
public_names = [n for n in dir(mypackage) if not n.startswith('_')]
```

```javascript
// Node.js: trace exports from a package index
const mod = require('./package');
const exported = Object.keys(mod);
```

### Compare against doc index

Build a list of documented items from the documentation itself — either by:

- **Parsing reference pages** for `## function_name()` or `### \`--flag\`` patterns
- **Reading a manifest file** that lists all documented items
- **Using tool output** from documentationjs or similar coverage tools

Then diff the two lists:

| Result | Category | Action |
|---|---|---|
| In source, in docs | Covered | Nothing |
| In source, not in docs | Gap | Write docs |
| In docs, not in source | Orphan | Audit and remove or fix docs |

## Metrics and Thresholds

| Metric | Formula | Target |
|---|---|---|
| **Endpoint coverage** | `documented_endpoints / total_endpoints` | ≥ 90% |
| **Config coverage** | `documented_options / total_options` | ≥ 95% |
| **CLI flag coverage** | `documented_flags / total_flags` | ≥ 95% |
| **Public API coverage** | `documented_exports / total_exports` | ≥ 80% |
| **Schema coverage** | `documented_tables_or_types / total_tables_or_types` | ≥ 90% |

Thresholds vary by project maturity and risk profile. A pre-1.0 project may accept lower coverage; a production API should target the thresholds above.

## Automation

Coverage analysis should run:

1. **On every PR** — flag new undocumented surfaces introduced in the diff
2. **Nightly** — generate a trending report showing coverage changes over time
3. **Pre-release** — block releases that fall below threshold without explicit exception

```yaml
# Example: GitHub Actions coverage check
- name: Check API doc coverage
  run: |
    endpoints=$(parse-endpoints src/routes/)
    documented=$(parse-endpoints docs/reference/api/)
    diff <(echo "$endpoints") <(echo "$documented") > uncovered.txt
    count=$(wc -l < uncovered.txt)
    if [ "$count" -gt 10 ]; then
      echo "FAIL: $count undocumented endpoints" && exit 1
    fi
```
