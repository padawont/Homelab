---
name: start-issue
description: Start an OpenCode session on a GitHub issue using worktrunk — fetches issue details, derives ADR 0002 branch name, creates a git worktree, and switches into it
---

# start-issue

## When to use me

Call this skill when a user asks you to start working on a GitHub issue. It automates the full workflow: fetch issue → derive branch type from labels → format branch per ADR 0002 → create worktree and switch into it.

Do NOT use this for editing existing topics or non-issue work.

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

### 1. Accept issue number as input

The user provides a GitHub issue number (e.g. `58`). Derive the repo from the current working directory:

```bash
repo=$(git remote get-url origin | sed 's|.*github\.com[:/]||;s|\.git$||')
```

If no remote or not in a git repo, fail with JSON: `{"success": false, "error": "No git remote found", "step": "derive_repo"}`.

### 2. Fetch issue details

```bash
gh issue view <num> --repo "$repo" --json title,body,labels
```

Extract individual fields using `--jq` per the `gh` skill:

```bash
title=$(gh issue view <num> --repo "$repo" --json title --jq '.title')
body=$(gh issue view <num> --repo "$repo" --json body --jq '.body')
label_names=$(gh issue view <num> --repo "$repo" --json labels --jq '.labels[].name')
```

### 3. Map labels to ADR 0002 branch type

Match the issue's labels against the mapping below. When an issue has multiple matching labels, apply **priority rules**:

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

If no label matches, fail with JSON: `{"success": false, "error": "No matching label found for branch type", "step": "map_labels", "labels": [<issue labels>]}`.

### 4. Slugify title

1. Lowercase the title
2. Remove punctuation and special characters (keep letters, digits, hyphens, and spaces)
3. Replace spaces with `-`
4. Collapse consecutive `-` into one
5. Strip leading/trailing `-`
6. Truncate to 60 characters max

### 5. Assemble branch name

`<type>/<issue-number>-<slug>`

If slugification produces an empty string (e.g., title is all symbols), use `issue-<number>` as the slug.

### 6. Create worktree and switch to it

```bash
wt switch --create --yes <branch>
```

This creates a git worktree for the branch and runs the project's `post-start` hook (e.g. `wt step copy-ignored`). The caller (e.g. devbox script) is responsible for `cd` into the worktree — the skill only creates it and returns the path.

The worktree path follows the convention: `../<repo-name>.<branch-with-slashes-replaced-by-dots>`.

The `@tasks` section label taxonomy and `@projects` field configurations are defined in [`tasks/`](../../../tasks/).

### 7. Error handling

- **Prerequisites** — Before starting, verify `gh auth status` and `which wt` are available. Fail with JSON `{"success": false, "error": "<tool> not found", "step": "prerequisites"}`.
- **Git not clean** — If the working tree has uncommitted changes, fail with JSON: `{"success": false, "error": "Working tree not clean", "step": "git_clean_check"}`.
- **`gh` fails** (auth, network, not found) — Fail with JSON: `{"success": false, "error": "<gh error>", "step": "fetch_issue"}`.
- **`wt` fails** (worktree already exists, branch conflict) — Fail with JSON: `{"success": false, "error": "Worktree already exists for <branch>", "step": "create_worktree", "hint": "Use wt switch <branch> instead"}`.

---

## Response contract

**Output ONLY valid JSON. No text before or after the JSON. No conversational messages, no questions, no status updates — only the JSON payload.**

On success, output:

```json
{
  "success": true,
  "branch": "research/53-research-org-wide-agent-plugin-remaining-research-topics",
  "worktree_path": "~/Projects/RunicEngines/knowledge-base.research-53-research-org-wide-agent-plugin-remaining-research-topics",
  "issue_number": 53,
  "issue_title": "Research: Org-Wide Agent Plugin — Remaining Research Topics"
}
```

On failure, output:

```json
{
  "success": false,
  "error": "Description of what went wrong",
  "step": "The workflow step that failed"
}
```

Write ONLY the JSON response — agents may call this skill programmatically and must receive parseable JSON with no surrounding text.

