---
name: create-github-issues
description: >
  Files GitHub epics and pipeline sub-issues for the Homelab PKM using the gh CLI.
  Use when creating an epic or a sub-issue (idea / knowledge / knowledge-audit /
  research / proposal / adr / implementation / chore) on the
  RunicEngines/knowledge-base repo. Structure is owned by
  ./.opencode/GITHUB-ISSUES.md; this skill only carries the plumbing. Never for
  writing notes.
---

# create-github-issues

Filing plumbing for issues on `RunicEngines/knowledge-base`. **Read
`./.opencode/GITHUB-ISSUES.md` first** — it owns the `issue-spec` block, the slot
order, the nine topic skeletons, the read/write protocols, and the legacy path
mapping. This skill restates none of that.

> [!IMPORTANT]
> Issues live in `RunicEngines/knowledge-base`; the content they describe lives in
> `padawont/Homelab`. Every `gh` command below carries `--repo RunicEngines/knowledge-base`.

## Workflow

1. **Read the contract.** Pick the topic from the request, then copy that topic's
   skeleton from `./.opencode/GITHUB-ISSUES.md` § Skeletons.
2. **Draft the body** with real `outputs` (`./`-rooted paths inside this repo) and
   real `sources` (absolute URL or `./` path). Write it under
   `.runesmith/*/pipeline/{n}.md` — the hub's only writable path.
3. **Self-check** against the contract's write protocol: block keys present, title
   prefix matches the topic, labels from `./AGENTS.md`, every acceptance item
   checkable.
4. **Create**, then **verify** the parent and re-parse the fence.
5. **Report** the issue number and the `outputs` list back to the human.

## Commands

| Command | Purpose |
|---|---|
| `gh issue create --title "Epic: {name}" --body-file {path} --label epic --repo RunicEngines/knowledge-base` | Create an epic |
| `gh issue create --title "{Prefix}: {name}" --body-file {path} --label {label} --parent {epic} --repo RunicEngines/knowledge-base` | Create a sub-issue |
| `gh issue view {n} --json number,title,labels,parent,subIssues,body --repo RunicEngines/knowledge-base` | Read structure |
| `gh issue list --state open --search "{concept}" --repo RunicEngines/knowledge-base` | Dedupe before filing |

## Guardrails

- `gh issue edit` and `gh label list` are **not** on the hub's granted surface
  (`./.opencode/agents/runesmith.md` holds `issue list`, `issue view`, `issue create`
  only), so edits and label changes are human-run steps.
- `--body-file` needs a real path: a human shell may write anywhere, while the hub
  may write a body only under `.runesmith/*/pipeline/`.
- Never paste a body inline; never file without a `parent` unless the issue is an epic.
- Knowledge work must decompose into atomic notes — one concept per file, ≤150 lines
  (`./AGENTS.md` § Atomic File Rule) — and every planned note appears in `outputs`.
- An issue whose content belongs to another repo is out of scope; see the contract
  § Out of scope.
- Author from `git config user.name`; dates ISO 8601.
