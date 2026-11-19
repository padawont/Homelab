---
name: create-github-issues
description: >
  Files GitHub epics and pipeline sub-issues for the Homelab PKM using the gh CLI.
  Use when creating an epic or a sub-issue (idea / knowledge / knowledge-audit /
  research / proposal / adr / implementation / chore) on the
  RunicEngines/knowledge-base repo. Structure is owned by
  ./.opencode/GITHUB-ISSUES.md; this skill only carries the commands. Never for
  writing notes.
---

# create-github-issues

The `gh` commands and their limits. Structure — the `issue-spec` block, the slot
order, the nine topic skeletons, the write protocol, the parent rule and the
naming conventions — is owned by `./.opencode/GITHUB-ISSUES.md`.

> [!IMPORTANT]
> Every command below targets `RunicEngines/knowledge-base`. What belongs there
> versus in `padawont/Homelab` is the contract's rule, not this skill's.

## Workflow

1. Read the contract and pick the topic.
2. Draft the body from that topic's skeleton, following § Write protocol.
3. Run the gap gate — `find-gap-issue` — and apply what it returns. No file
   before the gate has answered.
4. File it with the create command below, then verify with `gh issue view`.
5. Comment the accepted gaps with the comment command below.
6. Report the issue number and its `outputs` list to the human.

## Commands

| Command | Purpose |
|---|---|
| `gh issue create --title "Epic: {name}" --body-file {path} --label epic --repo RunicEngines/knowledge-base` | Create an epic |
| `gh issue create --title "{Prefix}: {name}" --body-file {path} --label {label} --parent {epic} --repo RunicEngines/knowledge-base` | Create a sub-issue |
| `gh issue comment {n} --body-file {path} --repo RunicEngines/knowledge-base` | Post the accepted gaps after filing |
| `gh issue view {n} --json number,title,labels,parent,subIssues,body --repo RunicEngines/knowledge-base` | Read structure |
| `gh issue list --state open --search "{concept}" --repo RunicEngines/knowledge-base` | Dedupe before filing |

## Guardrails

- `gh issue edit` and `gh label list` are not on the hub's granted surface
  (`./.opencode/agents/runesmith.md`), so edits and label changes are human-run
  steps. `gh issue close` is human-run for the same reason.
- Never paste a body inline. `--body-file` needs a path the hub may write; which
  paths those are is `./.opencode/agents/runesmith.md` § Negative Constraints.
  The draft and the comment file both come from there.
- No filing before the gate. Step 3 of § Workflow is not optional; which gaps
  block and how they are settled is owned by `find-gap-issue`, not restated here.
- The comment carries the accepted gaps and their evidence only — never a run
  summary and never a second copy of the body.
- An issue whose content belongs to another repo is out of scope — see the
  contract § Out of scope rather than filing it here.
