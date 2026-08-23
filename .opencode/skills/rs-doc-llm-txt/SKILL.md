---
name: rs-doc-llm-txt
description: >
  Scan documentation and generate llms.txt per llmstxt.org specification.
  Classifies files into Core and Optional sections, generates description
  links, and optionally creates context files via llms_txt2ctx.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: utility
  audience: developers, tech-writer
  trigger: manual
---

## Purpose

Generates a `/llms.txt` file per the [llmstxt.org](https://llmstxt.org/) specification by scanning documentation, classifying files into Core and Optional sections, and producing a structured markdown file with description links. When `llms_txt2ctx` is available on `PATH`, it optionally generates a context file for LLM consumption.

Key characteristics:

- **llmstxt.org compliant**: Output follows the llms.txt specification with `# Core` and `# Optional` sections.
- **Heuristic classification**: Uses directory depth, file naming, and content signals to assign Core vs Optional status.
- **Description extraction**: Generates meaningful sentence-length descriptions from H1 headings or first paragraph content.
- **Dam Lev compatibility**: When `llms_txt2ctx` is on `PATH`, can generate a companion `llms-ctx.txt` via subprocess invocation.
- **Overwrite-safe**: Existing `llms.txt` is overwritten — never appended to.

## Trigger

| Condition                                      | Type   |
| ---------------------------------------------- | ------ |
| User requests documentation index generation   | Manual |
| After documentation restructuring or additions | Manual |
| Before training a custom LLM on project docs   | Manual |

## Required Permissions

The calling agent must have these tools available:

| Tool     | Required | Scope            | Purpose                                              |
| -------- | -------- | ---------------- | ---------------------------------------------------- |
| read     | Yes      | `project: allow` | Read documentation files for content analysis        |
| glob     | Yes      | `project: allow` | Discover documentation files recursively             |
| grep     | Yes      | `project: allow` | Search for H1 headings and content patterns          |
| write    | Yes      | `project: allow` | Write llms.txt (and optionally llms-ctx.txt) to disk |
| edit     | No       | —                | Never modifies existing documentation files          |
| delegate | No       | —                | Self-contained; no delegation needed                 |

## Input

| Parameter          | Type             | Default           | Description                                                 |
| ------------------ | ---------------- | ----------------- | ----------------------------------------------------------- |
| `doc_root`         | string           | `"docs/"`         | Directory to scan for documentation files                   |
| `output_path`      | string           | `"docs/llms.txt"` | Where to write the llms.txt file                            |
| `exclude_patterns` | array (optional) | `[]`              | Glob patterns of files to exclude from the index            |
| `generate_context` | bool             | `true`            | Whether to attempt context file generation via llms_txt2ctx |

`doc_root` MUST be validated to exist before scanning. If it is missing, abort gracefully with `"Documentation root {path} does not exist"`.

`exclude_patterns` are applied against each discovered file path using glob matching. Matched files are omitted from both Core and Optional sections.

If `generate_context` is true and `llms_txt2ctx` is available on `PATH`, the skill invokes `llms_txt2ctx < llms.txt > llms-ctx.txt` to generate a companion context file alongside `llms.txt`.

## Workflow Steps

### Step 1: Discover documentation files

1. Validate `doc_root` exists. If not, abort with `"Documentation root {path} does not exist"`.
2. Recursively glob for documentation files: `**/*.md`.
3. Apply `exclude_patterns` to filter out specified files.
4. For each discovered file, record:
   - `path` — relative path from project root
   - `h1_heading` — extracted H1 (`# Title`), or inferred from first non-empty line if no H1
   - `first_paragraph` — first paragraph of meaningful text after the H1
   - `has_content` — whether the file contains non-whitespace content
5. Files with no content are skipped from the index.

### Step 2: Classify files into Core and Optional

Use these heuristics to classify each file:

**Core section** — essential documentation that any reader should start with:

| Condition                                           | Example                                                                                   |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| File is at doc root (not in a subdirectory)         | `index.md`, `README.md`, `getting-started.md`                                             |
| File name matches core keywords                     | `index`, `readme`, `getting-started`, `setup`, `quickstart`, `guide`, `overview`, `about` |
| Directory name indicates essential content          | `tutorials/`, `getting-started/`, `guides/`                                               |
| Shortest nesting depth files are preferred for Core | Depth 0-1 from doc root                                                                   |

**Optional section** — supplementary or reference content:

| Condition                                         | Example                                                             |
| ------------------------------------------------- | ------------------------------------------------------------------- |
| File is in a subdirectory two or more levels deep | `reference/sdk/python.md`                                           |
| File name matches reference keywords              | `api`, `reference`, `sdk`, `cli`, `config`, `advanced`, `deep-dive` |
| Directory name indicates reference content        | `reference/`, `sdk/`, `api/`, `advanced/`                           |

**Classification algorithm:**

1. If the relative path from doc root has 0 or 1 directory levels (e.g., `guide.md` or `tutorials/setup.md`), classify as **Core** unless the name clearly signals reference content.
2. If the relative path has 2+ directory levels (e.g., `reference/sdk/python.md`), classify as **Optional**.
3. Content signals override depth heuristics: a file named `reference.md` at the root is Optional; a file named `getting-started.md` deep in a tree is Core.
4. At least one file should be Core. If no files qualify as Core, force-classify the first discovered file as Core.

### Step 3: Generate description links

For each file, generate a description link following the llmstxt.org format:

```
- [Title](path/to/file.md): Description sentence.
```

**Description extraction priority:**

1. Use the file's H1 heading as the display title (strip the `# ` prefix).
2. If no H1, infer the title from the first non-empty line of content, truncated to 80 characters.
3. The description is the first paragraph of meaningful text (first non-heading, non-empty paragraph), truncated to one sentence (first sentence up to 200 characters).
4. If the file has no content, skip it entirely (do not include in llms.txt).

### Step 4: Write llms.txt

Assemble the output file per llmstxt.org specification:

```markdown
# {project_name}

> {project_description}

## Core

- [Title](path/to/file.md): Description sentence.

## Optional

- [Title](path/to/file.md): Description sentence.
```

- `{project_name}` is inferred from the doc root parent directory name, or from the first file's H1.
- `{project_description}` is extracted from the first Core file's first paragraph.
- Core section lists all classified Core files.
- Optional section lists all classified Optional files.
- If Core is empty, output an empty Core section with a note "No core files classified."
- If Optional is empty, omit the Optional section entirely.

### Step 5: Generate context file (optional)

1. If `generate_context` is `false`, skip this step.
2. Check if `llms_txt2ctx` is on `PATH` using `which llms_txt2ctx`.
3. If found, invoke: `llms_txt2ctx < {output_path} > {output_path.parent / 'llms-ctx.txt'}`.
4. If `llms_txt2ctx` is not found, log a warning: `"llms_txt2ctx not found on PATH. Context file not generated."` and continue without error.
5. If the subprocess fails, log: `"llms_txt2ctx invocation failed: {stderr}"` and continue.

## Output Format

The primary output is a file written to `output_path` (default `docs/llms.txt`) following the llmstxt.org specification.

If context generation succeeds, a secondary file is written to `docs/llms-ctx.txt`.

The agent should return a summary:

```yaml
summary:
  total_files: 12
  core: 5
  optional: 7
  skipped: 1
  context_generated: true
  output_path: "docs/llms.txt"
```

| Field               | Type    | Always Present | Description                               |
| ------------------- | ------- | -------------- | ----------------------------------------- |
| `total_files`       | integer | yes            | Total documentation files discovered      |
| `core`              | integer | yes            | Number of files classified as Core        |
| `optional`          | integer | yes            | Number of files classified as Optional    |
| `skipped`           | integer | yes            | Number of files skipped (empty, excluded) |
| `context_generated` | boolean | yes            | Whether llms-ctx.txt was generated        |
| `output_path`       | string  | yes            | Path to the written llms.txt file         |

## Error Handling

### Documentation Root Not Found

If `doc_root` does not exist on disk, abort with:

```
error: "Documentation root '{path}' does not exist"
suggestion: "Create the directory or specify an existing doc_root"
```

### No Documentation Files Found

If `doc_root` exists but contains no `.md` files (after filtering), produce a minimal response:

- `total_files: 0`
- `summary`: "No documentation files found in {path}."
- A file with just the header is still written:
  ```markdown
  # {project_name}

  > {project_description}
  ```

### Empty Files

Empty files (whitespace-only or zero-length) are skipped from the index with a warning. They are counted in `skipped` but not included in any section.

### no-H1 Files

If a file has no H1 heading (`# Title`), infer the title from the first non-empty line. If the file has no non-empty lines, skip it.

## See Also

- `rs-doc-architect` — Diataxis doc audit, a useful precursor
- `rs-doc-auditor` — scoring-based doc quality evaluation
- `rs-discover` — codebase context scanner
- [llmstxt.org](https://llmstxt.org/) — The llms.txt specification
- [dam/lev](https://github.com/dam/lev) — llms_txt2ctx reference implementation
