---
name: kb-scaffold-topic
description: Create topic folder from section template, populate frontmatter, strip template comments, initialize changelog for ideas
---

# kb-scaffold-topic

## When to use me

Call this skill when a user asks you to create a new topic, document, note, or entry in any section of the Knowledge Base. Use it instead of manually creating folders and files. Do NOT use this for editing existing topics — it is for initial creation only.

---

## Before you start

Read the target section's `AGENTS.md` (e.g. `ideas/AGENTS.md`) for:
- Folder naming pattern and required files
- Frontmatter required and optional fields
- Status lifecycle

Also read `templates/AGENTS.md` for the full frontmatter field reference and available template mapping across all sections.

The section `AGENTS.md` defines WHAT to create. This skill defines HOW to create it.

## ADR numbering

ADR folders use `<NNNN>-<topic>/` where `NNNN` is the **GitHub issue number** from `RunicEngines/knowledge-base`. Load the `gh` skill and use `gh issue list --repo RunicEngines/knowledge-base --json number,title` to find the relevant issue. Do **not** auto-increment from local folders and do **not** ask the user.

## Creating the folder and copying files

1. Create the destination directory path (kebab-case).
2. Copy every file from the template directory into the destination.
3. If a destination file already exists, **stop and report** — do not overwrite.
4. If the template directory does not exist or is missing expected files, **stop and report**.
5. After copying templates, create `README.md` with a single `# {Title}` heading (no frontmatter). There is no template for README.md.

## Filling frontmatter

Apply frontmatter rules to `overview.md` (and `index.qmd` for proposals) only. Do **not** modify `changelog.md`.

### Auto-fill (do not ask)

Auto-fill these fields when present in the section's field set (check the section's `AGENTS.md` and `templates/AGENTS.md`):

| Field | Value |
|---|---|
| `status` | `draft` |
| `date` | Today's date in `YYYY-MM-DD` format |
| `author` | Derive from `git config user.name` or `git config user.email`. If neither is available, ask. |
| `last_audit_date` | Today's date in `YYYY-MM-DD` format |
| `date-proposed` | Today's date in `YYYY-MM-DD` format |

For ADR files, follow the conditional rule in `adr/AGENTS.md` for when `date` should be set.

### Ask the user

- `title` — always ask
- `tags` — ask, default to empty array `[]`
- For remaining optional fields from `templates/AGENTS.md` — ask the user. Prompt for all fields that cannot be derived.

### Template comments

Remove all `<!-- ... -->` blocks from every file. Fold empty lines left by removed comments.

## Changelog initialization (ideas only)

After copying `changelog.md` for ideas, add one initial entry:

```yaml
entries:
  - date: <today YYYY-MM-DD>
    description: "Initial creation"
    author: <derived author>
```

## Response contract

Return results as JSON:

```json
{
  "success": true,
  "section": "ideas",
  "topic_path": "ideas/category/subcategory/topic-name/",
  "files_created": ["README.md", "overview.md", "changelog.md"],
  "error": null
}
```

On failure:
```json
{
  "success": false,
  "section": "ideas",
  "topic_path": null,
  "files_created": [],
  "error": "Destination `ideas/existing/path/` already exists — refusing to overwrite"
}
```

## Error handling (stop and report)

Do not silently recover. On any failure, print a specific error message and stop. Do not create partial output.

- "Template directory `templates/<name>/` does not exist"
- "Destination `<path>` already exists — refusing to overwrite"
- "Invalid section `<name>`. Valid: ideas, knowledge, research, proposals, adr"
- "Name `<name>` is not kebab-case"
- "Check section's `AGENTS.md` for folder naming rules — this path does not follow them"

