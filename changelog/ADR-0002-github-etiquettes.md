# ADR-0002: GitHub Etiquettes

## README.md

# ADR 0002: GitHub Etiquettes

Establish one org-wide set of GitHub conventions for all RunicEngines repositories — branch naming, commit messages (Conventional Commits), PR workflow, merge strategy, code review, issue/label taxonomy, and CI gates — to reduce friction as contributors move between projects.

See [overview.md](./overview.md) for the full decision record.

## overview.md

---
adr: 0002
title: GitHub Etiquettes
author: noarqerimi
status: draft
topic: collaboration-workflow
technology: "GitHub, Git"
date-proposed: 2026-06-03
history: "https://github.com/RunicEngines/knowledge-base/pull/31"
context: >
  Each RunicEngines repository uses GitHub differently — divergent branch
  naming, commit message styles, PR workflows, merge strategies, review
  expectations, and CI gates. As a multi-project COOP where developers move
  between repos, this inconsistency adds cognitive overhead and slows
  onboarding.
decision: >
  All RunicEngines repositories MUST adopt one shared set of GitHub
  conventions: branch names of the form `{type}/{issue-number}-{kebab-description}`,
  Conventional Commits for commit messages, an issue-linked draft → CI → review
  → merge PR workflow, squash-merge as the default merge strategy, at least one
  approving review before merge, a shared label taxonomy, and required CI checks
  enforced via branch protection on the default branch.
consequences: >
  Consistent, predictable collaboration across every project; faster onboarding;
  clean linear history that is friendly to automation, changelogs, and bisecting.
  Trade-off: upfront discipline from contributors, some enforcement/tooling
  overhead, and stricter rules than ad-hoc per-repo habits.
sources: []
references:
  - "https://www.conventionalcommits.org/en/v1.0.0/"
  - "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches"
  - "https://github.com/RunicEngines/knowledge-base/tree/main/adr"
---

# ADR 0002: GitHub Etiquettes

## Status

Draft (2026-06-03)

## Context and Problem Statement

RunicEngines is a COOP that spans many repositories. Today each project uses GitHub in its own way:

- Branch names follow no shared scheme, so it is hard to tell at a glance what a branch is for or which issue it belongs to.
- Commit messages range from terse one-liners to free-form paragraphs, making history hard to scan and impossible to automate (changelogs, release notes, semantic versioning).
- PR workflows differ — some repos review before CI, some merge without review, some leave PRs in draft indefinitely.
- Merge strategies are inconsistent (merge commits in one repo, squash in another), producing messy and divergent histories.
- Review expectations are implicit: how many approvals are needed, how quickly, and what reviewers should look for is left to each contributor's judgement.
- Issues and labels are unstandardized, so triage and cross-repo search are unreliable.
- CI gates vary, so "ready to merge" means something different in every repo.

When contributors move between repos or collaborate across projects, this friction compounds. We need one documented, org-wide convention that reduces cognitive overhead and makes onboarding smooth, while staying lightweight enough that small repos are not burdened.

## Decision

All RunicEngines repositories MUST adopt the following GitHub conventions. Keywords MUST, SHOULD, and MAY are used in the RFC 2119 sense.

### 1. Branch naming

Branches MUST follow the pattern:

```
{type}/{issue-number}-{kebab-description}
```

- `{type}` is the kind of change. For code repositories it MUST be a Conventional Commit type (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `build`, `ci`). For content repositories such as this knowledge base, the section name MAY be used as the type instead (`ideas`, `knowledge`, `research`, `proposals`, `adr`).
- `{issue-number}` is the GitHub issue the branch addresses. It SHOULD be present whenever an issue exists; branches with no associated issue MAY omit it.
- `{kebab-description}` is a short kebab-case summary.

Examples: `feat/42-user-auth`, `fix/108-null-pointer-on-login`, `adr/3-github-etiquettes`, `research/13-section-specific-agents`.

The default branch MUST be `main`. Work MUST happen on branches and reach `main` through pull requests, never via direct pushes.

### 2. Commit messages

Commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
type(scope): short description

optional body explaining what and why

optional footer (e.g. Closes #42, BREAKING CHANGE: ...)
```

- `type` MUST be one of the Conventional Commit types listed above.
- `scope` SHOULD identify the area touched (e.g. the section name in this repo: `feat(adr): ...`).
- The subject line SHOULD be in the imperative mood and SHOULD be 72 characters or fewer.
- Breaking changes MUST be signalled with a `!` after the type/scope or a `BREAKING CHANGE:` footer.

### 3. Pull request workflow

Every change MUST land through a pull request targeting `main`. The lifecycle is:

```
draft → CI passes → review → merge
```

- A PR SHOULD be opened as a **draft** while work is in progress and marked ready for review only when CI is green.
- A PR MUST link the issue it resolves using a closing keyword in the description (e.g. `Closes #42`).
- The PR title MUST follow the Conventional Commits format, because it becomes the squash-merge commit subject.
- The PR description SHOULD summarize what changed and why, and call out anything reviewers should focus on.

### 4. Merge strategy

- **Squash merge MUST be the default** for feature and fix branches, producing one clean, well-described commit per PR on `main` and a linear history.
- **Merge commits MAY be used** only for long-lived integration branches where preserving individual commits is deliberately valuable (rare).
- **Rebase merge MAY be used** for small, already-clean commit series when a maintainer wants to preserve atomic commits without a merge bubble.
- Branches MUST be deleted after merge.

### 5. Code review

- Each PR MUST receive **at least one approving review** from someone other than the author before merge.
- Reviewers SHOULD respond within **one business day** of being requested.
- Reviewers check: correctness, adherence to these conventions and any section `AGENTS.md`, test coverage where applicable, documentation updates, and absence of secrets or unrelated changes.
- Authors MUST resolve or explicitly acknowledge every review thread before merging.

### 6. Issues and labels

- Substantial work SHOULD start from a GitHub issue so branches and PRs have something to link to.
- Repositories SHOULD provide issue templates for at least **bug report** and **feature/enhancement**.
- A shared label taxonomy MUST be used, grouped by purpose:
  - **type** — `bug`, `enhancement`, `documentation`, `chore`
  - **area** — repo-specific (e.g. in this repo: `adr`, `ideas`, `knowledge`, `research`)
  - **scope/priority** — `org` (applies across all RunicEngines projects), `good first issue`, `blocked`, `fast-track` (see Section 8 for process)
- Labels MAY be extended per repo, but the type and scope groups MUST remain consistent across repos so cross-repo search and triage stay reliable.

### 7. CI/CD expectations

- Required CI checks (lint, build, tests, and any repo-specific validation) MUST pass before a PR can merge.
- The default branch MUST be protected: direct pushes disabled, required status checks enabled, and at least one approving review required.
- A PR MUST NOT be merged while any required check is failing or pending.

### 8. Fast-track process

Some issues are simple or urgent enough to warrant an expedited process (e.g. typo fixes, docs corrections, time-sensitive hotfixes). The fast-track process provides a controlled exception pathway without discarding the conventions this ADR establishes.

- A fast-track MUST begin with **mutual consent** of the RunicEngines developers — consent MAY be informal (async chat, verbal agreement). A comment on the issue documenting who consented (e.g. "+1 to fast-track from @alice and @bob") SHOULD be added as the canonical record of agreement.
- Once agreed, a `fast-track` label MUST be applied to the **issue**. The corresponding PR MUST also carry the `fast-track` label for visibility.
- A `fast-track` label MUST be created as an **org-wide label** so it is available in every RunicEngines repository.
- Fast-track PRs MUST still pass required CI checks enforced by branch protection. The mutual consent accelerates **review turnaround and thoroughness**, not enforcement gates.
- When branch protection requires an approving review, at least one consenting developer MUST submit a formal GitHub approval to satisfy the enforcement — mutual consent governs *thoroughness* of review, not *existence* of a review record.
- Steps outside branch protection (e.g. draft phase duration, depth of review commentary) MAY be waived by mutual consent.
- Fast-track SHOULD be used sparingly — for changes where the cost of full process demonstrably exceeds the value of the change. Routine use of fast-track for non-urgent work defeats the consistency this ADR is designed to establish.
- Fast-track MUST NOT be used for changes that require an idea, research, or proposal cycle — it is reserved for operational changes (typo fixes, docs corrections, hotfixes) that would not traverse the full content pipeline.

## Consequences

**Positive:**

- Consistent collaboration: a branch, commit, or PR reads the same way in every repo.
- Faster onboarding — contributors learn one workflow once and reuse it everywhere.
- Clean, linear history from squash merges, friendly to bisecting, changelog generation, and release automation.
- Conventional Commits unlock automated changelogs and semantic versioning later.
- Reliable cross-repo triage and search via the shared label taxonomy.
- Branch protection makes "ready to merge" mean the same thing everywhere.
- Fast-track provides an escape hatch for trivial or urgent changes, reducing friction without abandoning conventions.

**Negative / trade-offs:**

- Upfront discipline: contributors must learn and follow the conventions.
- Some enforcement and tooling overhead (branch protection, optional commit/PR-title linting).
- Squash merge discards intermediate commit granularity, which a few workflows may miss.
- Stricter than current ad-hoc per-repo habits; existing repos need a one-time migration.
- Fast-track risks normalization of deviance if overused — must be used sparingly to avoid undermining the conventions.

## Considered Options

### Conventional Commits + squash merge + branch protection (chosen)

- **Pros**: Widely adopted and well-documented; machine-parseable history; clean linear `main`; enables changelog/semver automation; low ongoing cost once set up.
- **Cons**: Requires contributors to learn the format; squash loses intra-PR commit detail.

### No convention / free-form (current state)

- **Pros**: Zero learning curve; maximum contributor freedom.
- **Cons**: Inconsistent across repos; unsearchable history; no automation possible; high onboarding friction — the exact problem this ADR addresses.

### Heavier GitFlow (develop/release/hotfix branches)

- **Pros**: Explicit release and hotfix lanes; familiar to some teams.
- **Cons**: Overkill for most RunicEngines repos; many long-lived branches and merge bubbles; more process than a COOP of small projects needs.

## Compliance

- Branch protection on `main` enforces required reviews, required status checks, and no direct pushes in every repository.
- Repositories SHOULD add lightweight automation where useful — a commit-lint / PR-title-lint check to enforce Conventional Commits, and a CI job that fails on convention violations.
- This ADR is the canonical reference; section `AGENTS.md` files and repo `CONTRIBUTING` docs SHOULD link to it rather than restating the rules.
- Deviations MUST be justified in the relevant PR and, if they represent a lasting change, captured in a superseding ADR.
