---
name: find-gap-issue
description: >
  Gap gate that runs before an issue is filed and never after. The hub launches
  one read-only find-gap subagent per drafted body, in parallel; the agent
  compares the draft to ./.opencode/GITHUB-ISSUES.md and returns every gap with a
  literal proposal. The hub applies the mechanical ones, asks the human about the
  rest, files with create-github-issues, then posts the accepted gaps as one
  comment. Validation only: never edits notes, never files while a blocking gap
  is open. Not for the legacy retrofit batches, which keep apply.sh / revert.sh.
---

# find-gap-issue

The gate between a drafted issue body and `gh issue create`. The structure is
owned by `./.opencode/GITHUB-ISSUES.md` § Write protocol, the `gh` commands by
`create-github-issues` § Commands, and the check list plus the JSON by
`./.opencode/agents/find-gap.md`. This skill carries only the order of the work.

## When to use

- A body has been drafted from a topic skeleton and is about to be filed.
- A filed body was edited and is about to be re-filed.

## When NOT to use

- The legacy retrofit batches — they run through their own `apply.sh` and
  `revert.sh` (`./.opencode/GITHUB-ISSUES.md` § Retrofit) and are exempt.
- Reviewing a written note — that is `loop-validation` and the five facets.
- Asking whether the Knowledge a service needs exists — that is `knowledge-gap`.
- Checking whether a cited URL is live — that is `reviewer-source`.

## Inputs

| input | source |
|---|---|
| one or more drafted bodies | `.runesmith/*/pipeline/*.md` — the hub's only write root |
| the topic of each draft | the drafter's brief, or the draft's `issue-spec` block |

## Workflow

1. **Lanes.** One lane per drafted body; every draft in the batch is a sibling of
   every other, in both directions. `N = 1` is a single-draft gate.
2. **Launch.** The hub launches `find-gap` once per draft, in parallel, each with
   the draft path, its topic and the sibling paths. Only `runesmith` holds
   `subagent: allow` (`./.opencode/WORKFLOW.md` § Coordination Rule), so this
   skill never launches anything — it says what the hub launches.
3. **Apply.** Paste every `gaps[].proposal` verbatim into the draft, at the field
   the entry names. Never paraphrase and never improve: the proposal is already
   the replacement text. A draft is a hub-writable path, so this write needs no
   other agent.
4. **Ask.** Put every blocking entry in `unresolved`, and every blocking gap whose
   proposal the human rejected, to the human with `question` — one question per
   item, carrying the field, the issue and the evidence. Record the answer beside
   the draft.
5. **File.** Only with no blocking item still open, run the create command in
   `create-github-issues` § Commands from the applied draft path. A blocking item
   the human does not settle stops the run — there is no skip path.
6. **Comment.** Post the gaps the gate reported and the human accepted as one
   `gh issue comment` per created issue, using the comment command in the same
   skill. The comment is the record of what the body deliberately does not carry:
   the field, the issue, the evidence and the human's decision. Nothing else — no
   run summary, no restatement of the body.
7. **Report.** One line each for what the gate found, what was applied, what was
   asked, and what was accepted and commented.

## Mechanical or human

- **Mechanical** — a `gaps[]` entry: the literal proposal exists, so step 3
  applies it without asking.
- **Human** — a blocking `unresolved[]` entry, or a proposal the human rejects at
  step 4. Either one keeps the draft unfiled until it is settled.
- **Coverage** — a non-blocking `unresolved[]` entry: reported, changes no
  verdict, blocks nothing.

## Guardrails

- **Validation only.** The draft is the only file this skill writes, and only
  under `.runesmith/*/pipeline/`. Never a note, never `AGENTS.md`, never
  `.opencode/`.
- **Never file past a blocking item.** Step 5 has no skip path.
- **Hub-launched.** The skill never launches `find-gap`; `runesmith` does.
- **Retrofit stays exempt.** The legacy batches keep their `apply.sh` /
  `revert.sh` and are not run through this gate.
- **No web.** URL liveness belongs to `reviewer-source`.
- **No restatement.** Structure stays in the contract, commands in
  `create-github-issues`, the criterion in the agent file.
