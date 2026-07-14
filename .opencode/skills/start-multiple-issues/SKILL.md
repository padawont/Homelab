---
name: start-multiple-issues
description: Start a single joint worktree for multiple GitHub issues of the same type — fetches all issues, derives combined branch name, creates one worktree for all
---

# start-multiple-issues

Use this skill when you see the command `start multiple issues <issue-numbers>` (e.g., `start multiple issues 63 64 65`).

This creates a **single joint branch** for all issues together (e.g., `knowledge/63-64-65-combined-topic`), NOT separate branches for each issue.

**Do NOT** call `start-issue` multiple times or create separate branches. Use this skill to create ONE joint branch.

Do NOT use this for single-issue work — use `start-issue` instead.

---

## AGENTS.md boundary

Branch naming rules and the full label taxonomy come from [ADR 0002](../../../adr/0002-github-etiquettes/overview.md) Section 1 (branch naming) and Section 6 (labels). The label-to-type mapping in this skill is derived from ADR 0002 — it must not redefine concepts already defined there.

The Knowledge Base section structure and label categories come from the root [AGENTS.md](../../../AGENTS.md).

Skill patterns for invoking `gh` come from the `gh` skill — this skill references it by path rather than duplicating its patterns.

---

## Before you start

Read the `gh` skill for patterns on invoking the GitHub CLI from agents.

Read ADR 0002 (`adr/0002-github-etiquettes/overview.md`) Section 1 for branch naming format and valid types, and Section 6 for the label taxonomy used in mapping below.

---

## Workflow

### 1. Accept issue numbers and optional slug as input

The user provides two or more GitHub issue numbers and an optional `--slug` flag for the combined description:

- `58 59 60` — joint branch, no slug provided (will derive from first issue's title)
- `58 59 60 --slug "combined-topic"` — joint branch with explicit slug

Derive the repo from the current working directory:

```bash
repo=$(git remote get-url origin | sed 's|.*github\.com[:/]||;s|\.git$||')
```

If no remote or not in a git repo, fail with JSON: `{"success": false, "error": "No git remote found", "step": "derive_repo"}`.

Parse arguments:
- Collect all arguments before `--slug` that are numeric → issue numbers
- If `--slug` is present, the next argument is the slug value
- If fewer than 2 issue numbers are given, fail with JSON: `{"success": false, "error": "At least 2 issue numbers required", "step": "parse_input"}`

### 2. Fetch issue details

Fetch ALL issues in parallel:

```bash
for num in "${ISSUE_NUMS[@]}"; do
  gh issue view "$num" --repo "$repo" --json title,labels &
done
```

Collect all titles and label names per issue.

If `gh` fails for any issue (auth, network, not found), fail with JSON: `{"success": false, "error": "<gh error for issue N>", "step": "fetch_issue"}`.

### 3. Map labels to ADR 0002 branch type

For EACH issue, map its labels against the mapping below. When an issue has multiple matching labels, apply **priority rules**:

**Section-specific labels** (high priority): `knowledge`, `research`, `ideas`, `adr`, `proposal`
**Generic labels** (low priority): `enhancement`, `bug`, `documentation`, `chore`

If an issue has both a section-specific and generic label, use the section-specific one. For example:
- `knowledge` + `enhancement` → `knowledge/`
- `research` + `bug` → `research/`

Only fail if an issue has multiple **section-specific** labels (e.g., `knowledge` + `research`).

| Issue label | Branch type | Priority |
|---|---|---|
| `chore` | `chore/` | generic |
| `ideas` | `ideas/` | section |
| `knowledge` | `knowledge/` | section |
| `research` | `research/` | section |
| `adr` | `adr/` | section |
| `proposal` | `proposals/` | section |
| `enhancement` | `feat/` | generic |
| `bug` | `fix/` | generic |
| `documentation` | `docs/` | generic |

If any issue has no matching label, fail with JSON: `{"success": false, "error": "No matching label found for issue <N>", "step": "map_labels", "labels": [<issue N labels>]}`.

If ALL issues resolve to the same branch type, use that type. If any issue's type differs from the others, fail with JSON:

```json
{
  "success": false,
  "error": "Issues have different branch types: issue-58=knowledge, issue-59=research",
  "step": "map_labels"
}
```

### 4. Determine slug

The slug is the **topic component** of the branch name (the part after the issue numbers). Issue numbers are always included separately.

- If `--slug` was provided, use that value as the slug
- If `--slug` was NOT provided, **auto-derive** a combined slug from all issue titles:
  1. Strip common prefixes (e.g., "Knowledge:", "Research:", "Fix:", etc.)
  2. Extract key terms from each title
  3. Combine into a short descriptive phrase (e.g., "pydantic vcr fastapi" → "pydantic-vcr-fastapi")
  4. If the combined result is too long (>60 chars), use a representative subset or fall back to `combined-<type>`
- Run the result through `slugify()`:

  1. Lowercase
  2. Remove punctuation and special characters (keep letters, digits, hyphens, and spaces)
  3. Replace spaces with `-`
  4. Collapse consecutive `-` into one
  5. Strip leading/trailing `-`
  6. Truncate to 60 characters max

If slugification produces an empty string, use `joint-issue` as the fallback slug.

### 5. Assemble branch name

Sort issue numbers in ascending order. Join them with `-`. The branch name is **always** in this format:

`<type>/<issue1>-<issue2>-...-<issueN>-<slug>`

The issue numbers are **always included**, regardless of whether `--slug` was provided or auto-derived.

Examples:
- With `--slug combined-knowledge-run` for issues 63, 64, 65: `knowledge/63-64-65-combined-knowledge-run`
- Without `--slug` for issues 63, 64, 65 (auto-derived from titles "Knowledge: Pydantic AI", "Knowledge: VCR.py", "Knowledge: FastAPI"): `knowledge/63-64-65-pydantic-vcr-fastapi`

### 6. Create worktree and switch to it

```bash
wt switch --create --yes <branch>
```

This creates a git worktree for the branch and runs the project's `post-start` hook (e.g. `wt step copy-ignored`). The caller (e.g. devbox script) is responsible for `cd` into the worktree — the skill only creates it and returns the path.

The worktree path follows the convention: `../<repo-name>.<branch-with-slashes-replaced-by-dots>`.

If `wt` fails (worktree already exists, branch conflict), fail with JSON: `{"success": false, "error": "Worktree already exists for <branch>", "step": "create_worktree", "hint": "Use wt switch <branch> instead"}`.

### 7. Error handling

- **Prerequisites** — Before starting, verify `gh auth status` and `which wt` are available. Fail with JSON `{"success": false, "error": "<tool> not found", "step": "prerequisites"}`.
- **Git not clean** — If the working tree has uncommitted changes, fail with JSON: `{"success": false, "error": "Working tree not clean", "step": "git_clean_check"}`.

---

## Response contract

**Output ONLY valid JSON. No text before or after the JSON.**

On success:

```json
{
  "success": true,
  "branch": "knowledge/58-59-60-combined-research-slug",
  "worktree_path": "~/Projects/RunicEngines/knowledge-base.knowledge.58-59-60-combined-research-slug",
  "issue_numbers": [58, 59, 60],
  "issue_title": "Combined: #58 <title> + #59 <title> + #60 <title>",
  "slug_source": "flag"  
}
```

- `slug_source` is `"flag"` if `--slug` was provided, `"auto"` if auto-derived from all issue titles.

On failure:

```json
{
  "success": false,
  "error": "Description of what went wrong",
  "step": "The workflow step that failed"
}
```

Write ONLY the JSON response — agents may call this skill programmatically and must receive parseable JSON with no surrounding text.

