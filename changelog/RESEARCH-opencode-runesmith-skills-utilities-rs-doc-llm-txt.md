---
title: "LLM.txt Generation Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-14
tags:
  - opencode
  - skills
  - documentation
  - llm-txt
  - runesmith
sources:
  - knowledge: "knowledge/design/documentation/llm-txt/README.md"
references:
  - url: "https://llmstxt.org/"
    title: "llms.txt Specification"
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
  - url: "https://llmstxt.org/intro.html#cli"
    title: "llms_txt2ctx — Context file generator (CLI reference)"
last_audit_date: 2026-06-14
---

# LLM.txt Generation Skill Design (`rs-doc-llm-txt`)

## Purpose

`rs-doc-llm-txt` is a utility skill for the `@runicengines/opencode-runesmith` plugin. It scans a project's documentation directory and generates a `/llms.txt` file per the [llmstxt.org](https://llmstxt.org/) specification. Optionally, it generates `llms-ctx.txt` and `llms-ctx-full.txt` context files using the `llms_txt2ctx` tool.

The skill makes project documentation discoverable by LLM tooling — when an LLM reads `llms.txt`, it gets a structured index of the project's documentation, enabling it to navigate docs efficiently without scanning every file.

## Skill Identity

| Property | Value |
|---|---|
| Plugin | `@runicengines/opencode-runesmith` |
| Skill name | `rs-doc-llm-txt` |
| Skill prefix | `rs-` |
| Loading model | On-demand (via `skill({ name: "rs-doc-llm-txt" })`) |
| Primary user | Tech-Writer agent |
| Secondary users | DevOps agent, Architect agent |
| Trigger | Documentation publishing, CI post-build, project setup |

## Permission Model

| Permission | Purpose |
|---|---|
| `read` | Scan documentation directory structure and read file contents |
| `glob` | Discover documentation files matching patterns |
| `bash: { "cat *": allow, "ls *": allow }` | Read file contents for summarization |
| `write` | Generate `llms.txt`, `llms-ctx.txt`, `llms-ctx-full.txt` output files |

The skill is **read-only** for scanning documentation and **write** for generating output files. It never modifies existing documentation.

## Input

The skill accepts:

1. **Documentation root path** — directory to scan (default: `docs/`).
2. **Project name** — used in the `llms.txt` H1 heading (default: derived from `package.json` `name` field or directory name).
3. **Project summary** — a one-sentence description for the blockquote summary (default: derived from `package.json` `description` or `README.md` first paragraph).
4. **Section configuration** (optional):
   - `optional_sections` — list of additional file groups to include as optional sections.
   - `exclude_patterns` — glob patterns to exclude (e.g., `*private*`, `*internal*`).
5. **Context generation** (optional):
   - `generate_ctx` — boolean, whether to generate `llms-ctx.txt` and `llms-ctx-full.txt` (default: false).
   - `ctx_tool_path` — path to `llms_txt2ctx` binary if installed.

## Workflow Steps

### Step 1: Discover documentation files

1. Recursively scan the specified doc root for `.md` and `.qmd` files.
2. Exclude auto-generated or system files (node_modules, build output, hidden files).
3. Sort files alphabetically within each directory level.
4. Build a file inventory with: relative path, title (from H1 or filename), brief description (from first paragraph).

### Step 2: Generate llms.txt

Per the [llmstxt.org spec](https://llmstxt.org/), generate:

```markdown
# <Project Name>

> <Project summary — one sentence or short paragraph describing the project>

## Core (required)

The core documentation is your primary reference. These files should fully
describe the project, its API, and how to work with it.

- [doc/path/file1.md](doc/path/file1.md): Description of what this file covers
- [doc/path/file2.md](doc/path/file2.md): Description of what this file covers

## Optional (recommended)

Additional resources that provide deeper context for specific areas.

- [doc/path/optional1.md](doc/path/optional1.md): Description
```

The spec defines this structure:
- **H1** with the project name — the only required element.
- **Blockquote** (recommended) with a short summary of the project.
- **One or more H2-delimited sections** with linked file lists. The skill uses two conventional sections:
  - **Core** — primary documentation files.
  - **Optional** — supplementary resources.

### Step 3: Classify files into Core vs Optional

Use the following heuristics:

| Classification | Criteria |
|---|---|
| **Core** | Files in root doc directory, README, index files, getting-started guides, API reference, configuration reference, architecture docs |
| **Optional** | Tutorials, how-to guides for advanced scenarios, contrib guides, changelogs, design docs, ADRs |

Override: if a file's path contains `optional/`, `extra/`, `advanced/`, classify as Optional. If it contains `core/`, `essential/`, `required/`, classify as Core.

### Step 4: Generate described links

For each file, produce a link entry with:
- Relative path from project root to the file.
- A short description (first sentence of the file, or title if the file is short).

Format: `- [path/to/file.md](path/to/file.md): Brief description of the file's content.`

### Step 5: Optionally generate context files (llms-ctx.txt / llms-ctx-full.txt)

If `generate_ctx` is enabled:

1. Check if `llms_txt2ctx` is available in PATH.
2. If available, run:
   ```
   llms_txt2ctx docs/llms.txt > docs/llms-ctx.txt
   llms_txt2ctx --optional True docs/llms.txt > docs/llms-ctx-full.txt
   ```
   The tool generates XML-structured context documents suitable for LLM consumption. Without `--optional True`, only core sections are included; with `--optional True`, all sections including Optional are included.
3. If the tool is not installed, fall back to generating a plain-text concatenation of all linked files.

### Step 6: Validate output

Verify the generated `llms.txt` against spec requirements (H1 present and non-empty) and skill policies (blockquote present, at least one link in Core section, all links are valid relative paths, no broken URLs).

## Output

The skill writes to the project root:

| File | Description |
|---|---|
| `llms.txt` | Structured documentation index per llmstxt.org spec |
| `llms-ctx.txt` | (Optional) XML-structured context document with core sections (via `llms_txt2ctx`) |
| `llms-ctx-full.txt` | (Optional) XML-structured context document with all sections including Optional (via `llms_txt2ctx --optional True`) |

## Chains With

| Skill | Condition | Step |
|---|---|---|
| `rs-discover` | If project root layout is unknown | Before Step 1 |
| `rs-doc-architect` | If documentation first needs to be restructured | Before this skill |

## Design Decisions

1. **Spec-compliant generation**. The skill produces `llms.txt` strictly following the llmstxt.org specification. Format variations (e.g., extra sections, custom markdown) are not supported — the skill serves spec, not preference.

2. **Core vs Optional heuristics**. The classification into Core and Optional sections is heuristic. Users can override by placing files in `core/` or `optional/` subdirectories. The heuristic is sufficient for most projects without manual configuration.

3. **Context file generation is optional**. `llms_txt2ctx` generates monolithic context files that some LLMs prefer over navigating a linked index. This step is opt-in because the context files can be large and are not part of the core spec.

4. **Descriptions from file content**. Each link's description is extracted from the file's first paragraph or H1, not from a separate metadata file. This keeps the skill self-contained — no additional metadata file is needed.

## See Also

- [llmstxt.org](https://llmstxt.org/) — The specification this skill implements
- [LLM.txt knowledge notes](knowledge/design/documentation/llm-txt/README.md) — Background research on llms.txt patterns
- [llms_txt2ctx](https://llmstxt.org/intro.html#cli) — Context file generator (CLI reference)
- [Doc Architect skill](../workflows/rs-doc-architect.md) — Can restructure docs before llms.txt generation
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills) — Skill system reference
