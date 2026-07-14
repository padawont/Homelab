---
title: "Keep a Changelog 2.0.0 — Best Practices"
status: draft
author: Khalid Zubair
date: 2026-06-14
tags:
  - changelog
  - documentation
  - best-practices
  - conventional-commits
  - llm
  - automation
sources:
  - url: https://keepachangelog.com/en/2.0.0/
    title: "Keep a Changelog v2.0.0"
last_audit_date: 2026-06-14
---

# Keep a Changelog 2.0.0 — Best Practices

## Write for Humans

Changelog entries should be written in clear, plain language aimed at human readers — not machines. Each entry should concisely describe what changed and why it matters to someone using the project. Avoid raw commit messages, internal jargon, or implementation details that are irrelevant to consumers. Many readers are not native speakers, so favor clear, concise wording.

## Be Consistent

Apply the same format, section ordering, and tone across all versions. Consistency makes the changelog predictable and easy to scan. Follow the six defined change types; do not invent new headings unless the standard types genuinely cannot cover the change.

## Curation Over Accumulation

See [spec.md](spec.md#curation-over-accumulation) for the principle. In practice:

- Do not sort every commit into a type as you make it — that is tedious and misses the point.
- Write the changelog as a summary for your readers, not as a record of your commits.
- A changelog that records only some changes can mislead as much as no changelog. Readers treat it as the full picture. Leave out trivial changes, but include every notable one.

## Link to Issues and Pull Requests

Each changelog entry should include a reference to the relevant issue or pull request. This gives readers a path to deeper context (discussion, implementation details, reproduction steps).

```markdown
### Fixed
- Fixed crash when loading empty configuration files ([#42](https://github.com/user/repo/issues/42))
```

Keep two things in mind: links break when a repository moves, and pull request numbers belong to one host, not to your code. Git tags and commit references stay with the repository. Link when it helps, prefer plain prose over a list of bare `(#1234)` references, and consider collecting references at the bottom of the file as reference-style links — the way version comparisons are — so the prose stays readable and every pointer lives in one place.

## Use Conventional Commits to Generate Raw Material

Adopting [Conventional Commits](https://www.conventionalcommits.org/) creates a structured commit history that can be parsed to auto-generate changelog drafts. The commit types map naturally:

| Conventional Commit Type | Changelog Section |
|---|---|
| `feat` | Added |
| `fix` | Fixed |
| `BREAKING CHANGE` | Highlight in Changed or Removed with `**Breaking:**` |
| `deprecate` | Deprecated |
| `remove` | Removed |
| `security` | Security (lead with CVE when available) |

Using Conventional Commits reduces the effort of maintaining a changelog, because entries can be mechanically derived from the commit log and then curated. However, **a generated changelog is raw material, not the final entry.** A commit and a changelog entry are written for different people, and one does not convert cleanly into the other. Generating the entry from the commit assumes every commit belongs in the changelog, and that the right entry is a reworded commit message. Usually it is neither: many commits do not matter to your readers, and the changes that do often span several commits. A person still has to choose what is notable, group it, and write it for the reader.

## LLM and Agent Changelog Brief

See [spec.md](spec.md#llm-and-agent-guidance) for the principle. When drafting with an LLM, give it this brief:

> Summarize notable, user-facing changes. Do not paste a git log. Sort each change into one of the six types (Added, Changed, Deprecated, Removed, Fixed, Security). Explain the reason in the text. Mark breaking changes with `**Breaking:**`. Remove anything not worth reading.

If your project uses coding agents, record that brief where they read it — for example, in an `AGENTS.md` or `CLAUDE.md` file. There is no format to configure; the instructions are the interface.

## Automation in a Supporting Role

Continuous integration can help maintain a changelog, but keep it in a supporting role. Use automation for mechanical tasks:

- Move the `Unreleased` section into a dated version at release time.
- Check that the file is formatted correctly.
- Optionally remind a contributor that a change may need an entry.

Do **not** make a changelog edit a required check on every change. That teaches people to add a line to pass the check, which fills the changelog with noise. Let automation handle mechanics, and leave the judgment to people.

## Changelog vs Release Notes

See [spec.md](spec.md#changelogs-vs-release-notes) for the distinction. In practice:

- At release time, the version's section in the changelog is already the draft — copy it into the release, and expand it only if the announcement wants more.
- Because every version sits under a predictable `## [x.y.z]` heading, a small script can extract that section and create the release without anyone retyping it.
- Keep the changelog as the canonical record. Generate host-specific release posts from it.

## Keep the Unreleased Section Up to Date

Add entries to `## [Unreleased]` as changes land in the development branch. This serves two purposes:

1. Contributors and early adopters can see what's coming in the next release.
2. At release time, the entire Unreleased block becomes the new version's entry — no retroactive writing needed.

## Version History Should Mirror Git Tags

Every version heading in the changelog should correspond to a git tag. This ensures readers (and automated tools) can cross-reference between the changelog and the tagged source. The diff links at the bottom of the file rely on tag comparisons:

```markdown
[1.0.0]: https://github.com/user/repo/compare/v0.9.0...v1.0.0
```

## Crediting Contributors

The commit history already records who did what, so a changelog does not need to credit anyone. But naming contributors, especially in a notable release, is a generous way to recognize their work. If you do:

- Keep it brief.
- Use names rather than just `@handle` handles — handles belong to one host and may not travel with the person.
- For fuller credits, use a `CONTRIBUTORS` or `AUTHORS` file rather than crowding the changelog.

## Avoid Common Anti-Patterns

- **Commit log diffs:** Do not dump raw git logs into the changelog. The commit log is a development artifact; the changelog is a user-facing document. A "git log" is the list of commits in git — but this applies to any version control system.
- **Ignoring deprecations:** Always list deprecations in the version where they appear. Users should be able to upgrade to a deprecation-aware version before the removal happens. Say which version will remove it so they can plan.
- **Confusing dates:** Always use `YYYY-MM-DD`. Regional formats (MM/DD/YYYY or DD/MM/YYYY) are ambiguous. See [format.md](format.md#yyyy-mm-dd-dating) for the heading format.
