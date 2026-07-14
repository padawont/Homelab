---
title: "RuneSmith Maintenance and Governance"
status: exploring
author: "refactorartist (Khalid Zubair)"
date: 2026-06-09
tags:
  - opencode
  - runesmith
  - governance
  - maintenance
  - deprecation
  - release
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/versioning.md"
  - knowledge: "knowledge/tooling/opencode/plugins/publishing-workflow.md"
  - knowledge: "knowledge/tooling/opencode/plugins/bundling-components.md"
  - knowledge: "knowledge/tooling/opencode/skills/changelog-manager.md"
  - knowledge: "knowledge/tooling/opencode/skills/maintenance.md"
  - knowledge: "knowledge/tooling/opencode/agents/composition-patterns.md"
references:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://keepachangelog.com/en/2.0.0/"
    title: "Keep a Changelog 2.0.0"
  - url: "https://semver.org/spec/v2.0.0.html"
    title: "SemVer 2.0.0"
  - url: "https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry"
    title: "GitHub Packages npm Registry"
last_audit_date: 2026-06-09
---

# RuneSmith Maintenance and Governance

- **Plugin:** `@runicengines/opencode-runesmith`
- **Distribution:** Private npm via GitHub Packages (see [distribution-comparison.md](../architecture/distribution-comparison.md))
- **Status:** Exploring — governance model under investigation

## Context

The `@runicengines/opencode-runesmith` plugin is an internal tool for the RunicEngines cooperative. It bundles seven subagents, workflow and utility skills, and MCP configuration into a single npm package distributed via GitHub Packages. As the plugin moves through the phased rollout (see [rollout-strategy.md](./rollout-strategy.md)), it transitions from pilot experiment to standard infrastructure. This transition demands a formal governance and maintenance model.

This document defines the long-term ownership, maintainer model, contribution process, deprecation policy, release cadence, and changelog conventions for the plugin. It is intended to outlive the original maintainer and serve as the operating manual for whoever takes over the plugin next.

## 1. Maintainer Model

### 1.1 Core Maintainer

The plugin has a single core maintainer who holds publish access to the GitHub Packages registry and is the decision-maker for releases, roadmap priorities, and breaking changes.

| Role | Current Holder | Backstop |
|---|---|---|
| Core maintainer | refactorartist (Khalid Zubair) | TBD — see Succession Plan (Section 6) |
| Backup maintainer | None currently | First onboarding priority |

The core maintainer is listed in the plugin's `package.json` under `maintainers` and has `write:packages` permission on the plugin's GitHub repository. The maintainer is also listed as a CODEOWNER for the plugin repository so that pull requests automatically request their review.

As a lightweight pre-Phase-2 measure, consider granting a cooperative admin read-access to the GitHub Packages registry and maintaining an emergency publish procedure document.

### 1.2 Maintainer Responsibilities

| Area | Responsibilities |
|---|---|
| **Bug triage** | Monitor GitHub Issues for `runesmith-bug` label. Triage within 2 business days. Assign severity (S1-S5) per [rollout-strategy.md](./rollout-strategy.md) severity definitions. |
| **Release management** | Cut releases per the release cadence (Section 4). Publish to GitHub Packages. Tag releases. Write changelog entries. |
| **Roadmap** | Maintain a public roadmap in the plugin repository. Prioritize features based on cooperative member feedback. |
| **Community support** | Respond to questions in the designated support channel (Slack/Discord). Maintain the FAQ and onboarding guide. |
| **Review** | Review and merge or reject contributions per the contribution process (Section 2). At least one maintainer review is required for every PR. |
| **Security** | Monitor for dependency vulnerabilities. Apply security patches within 1 week of disclosure. |
| **Documentation** | Keep the plugin README, CHANGELOG, and cross-referenced documentation up to date. |

### 1.3 Maintainer Onboarding

When a new maintainer joins the team:

1. Existing maintainer adds the candidate to the GitHub repository with `Write` role.
2. Candidate is granted `write:packages` permission on the GitHub Packages registry for the `@runicengines/opencode-runesmith` package.
3. Candidate is added to `CODEOWNERS` and `package.json` maintainers array.
4. Knowledge transfer session covers: plugin architecture (see [overview.md](../overview.md)), init hook and version-stamping (see [update-propagation.md](./update-propagation.md)), permission profiles (see [permission-profiles.md](./permission-profiles.md)), rollout strategy (see [rollout-strategy.md](./rollout-strategy.md)), and the release checklist (Section 4.4).
5. Shadow period: candidate co-reviews 3 pull requests with the existing maintainer before merging independently.
6. First solo release: candidate cuts a patch release under supervision.
7. Onboarding complete. Existing maintainer updates the backup maintainer field.

### 1.4 Maintainer Offboarding

When a maintainer leaves the project:

1. All GitHub permissions are revoked (repository `Write` role, `write:packages` on the npm package).
2. The departing maintainer archives any open branches or in-progress PRs with status notes.
3. A knowledge transfer session is scheduled with the remaining maintainer or the succession plan (Section 6.1) is activated.
4. The departing maintainer is removed from `CODEOWNERS` and `package.json` maintainers.

### 1.5 Escalation Path

When issues cannot be resolved by the core maintainer (e.g., disagreement on direction, unresolved security concern, maintainer unavailability):

| Level | Escalation | Decision |
|---|---|---|
| L1 | Core maintainer | Routine decisions: bug fixes, patch releases, minor features |
| L2 | Backup maintainer | When core maintainer is unavailable for > 1 week |
| L3 | RunicEngines cooperative | Architectural decisions, breaking changes, succession, archival |

At Level 3, the issue is raised at the next cooperative meeting or via the organisation's governance process. The cooperative as a whole holds authority over the plugin because it is shared infrastructure.

### 1.6 Bus Factor

The current bus factor is 1 (a single core maintainer). The backup maintainer role is intentionally empty until the first maintainer onboarding is completed. Mitigation actions:

| Action | Timeline |
|---|---|
| Identify and onboard a backup maintainer | Before Phase 2 of rollout (see [rollout-strategy.md](./rollout-strategy.md)) |
| Document all release and maintenance procedures | This document |
| Automate the release process via GitHub Actions | Before Phase 3 |
| Ensure the plugin repository is accessible to all cooperative members (read) | Immediately |

## 2. Contribution Process

### 2.1 PR Workflow for New Agent Definitions and Skills

All changes to the plugin go through the same PR workflow, regardless of whether they are agent definitions, skill files, init hook logic, or documentation.

```
Feature request / bug report
        │
        ▼
Issue filed in RunicEngines/knowledge-base
        │
        ├── Bug fixes: direct to PR
        │
        └── New features / agents / skills:
                │
                ▼
            Idea → Knowledge → Research → Proposal → PR
```

The full pipeline (idea → knowledge → research → proposal → PR) applies only to new agent definitions, new skills, or architectural changes. Bug fixes and documentation improvements may skip directly to PR.

### 2.2 Review Requirements

| Requirement | Detail |
|---|---|
| **Maintainer review** | At least one maintainer must review and approve. |
| **ADR 0002 conventions** | PR title and commits follow [Conventional Commits](https://www.conventionalcommits.org/). Branch name follows `{type}/{issue-number}-{kebab-description}`. |
| **No self-merge** | The author may not merge their own PR, even if they are a maintainer (unless the change is trivial — typo fix, CI config — and explicitly labeled `fast-track`). |
| **Review window** | Maintainer has 3 business days to provide initial review. If no response, the PR may be escalated to the backup maintainer or cooperative. |

### 2.3 Testing Requirements

Before a PR can be merged, the verification checklist must pass in full. The checklist is defined in [verification.md](./verification.md) and covers:

1. **Plugin installation** — init hook runs without error, version stamp is written, agent/skill files land in `.opencode/`.
2. **Agent discovery** — all seven agent `.md` files are present and loadable.
3. **Skill loading** — all bundled skill directories are present and loadable via `skill({ name: "rs-*" })`.
4. **Permission enforcement** — each agent enforces its permission profile (see [permission-profiles.md](./permission-profiles.md)).
5. **Update propagation** — version mismatch triggers re-copy; stamp comparison works for upgrade, downgrade, and fresh install (see [update-propagation.md](./update-propagation.md)).
6. **Rollback** — the rollback procedure works for the relevant phase.

For new agent definitions or skill additions, the contributor must extend the verification checklist with test cases for the new component.

### 2.4 Documentation Requirements

Every PR must include or update:

| Document | When Required |
|---|---|
| `CHANGELOG.md` | Always — every PR must add a changelog entry under `## [Unreleased]` |
| Plugin `README.md` | When adding or changing agents, skills, or configuration |
| `research/opencode-runesmith/README.md` | When adding a new research file |
| Cross-referenced research files | When changing behaviour documented in other research files (e.g., changing permission profiles requires updating `permission-profiles.md`) |
| Knowledge notes | When the PR implements a behaviour that should be captured as organisational knowledge |

### 2.5 Feature Request Lifecycle

Feature requests follow the RunicEngines content pipeline:

```
GitHub Issue
    │  (user submits feature request with `runesmith-enhancement` label)
    ▼
Idea  (ideas/organisation/tools/org-wide-agent-plugin/)
    │  (the idea is the container; new features extend it)
    ▼
Knowledge  (knowledge/tooling/opencode/<area>/)
    │  (research the technical approach, update relevant knowledge notes)
    ▼
Research  (research/opencode-runesmith/<area>/)
    │  (write or extend research with findings)
    ▼
Proposal  (proposals/<id>-<name>/)
    │  (formal proposal for the cooperative to review)
    ▼
PR  (plugin repository)
```

Small features (fewer than 50 lines of changes, no new agents or skills) may skip the Idea and Proposal steps. The maintainer makes the call on what qualifies as "small."

## 3. Deprecation Policy

### 3.1 Deprecation Notice Period

When a feature, agent, skill, or configuration option is to be removed, it is first deprecated for **one minor release cycle** before removal.

| Event | Version | Timeline |
|---|---|---|
| Feature is active | 1.0.0 | Baseline |
| Feature is deprecated | 1.1.0 | Deprecation announced; feature still works |
| Feature is removed | 2.0.0 | Breaking change; migration path required |

If the deprecation crosses a major version boundary, the notice period extends from the minor release in which deprecation was announced to the next major release. For example, a feature deprecated in `1.5.0` is removed in `2.0.0`.

### 3.2 Deprecation Warnings

Deprecated features produce a warning message in the plugin's init hook logs. The warning includes:

- The name of the deprecated feature.
- The version in which it was deprecated.
- The version in which it will be removed.
- A link to the migration path documentation.

```
[RuneSmith] Warning: Agent "rs-legacy-analyzer" is deprecated in 1.1.0.
[RuneSmith] It will be removed in 2.0.0.
[RuneSmith] Migration guide: https://github.com/RunicEngines/opencode-runesmith/blob/main/docs/migrations/1.1.0-rs-legacy-analyzer.md
```

Warnings are written to `stderr` so they are visible in the OpenCode startup log. They do not prevent the plugin from loading.

Note: This deprecation warning mechanism depends on init-hook capabilities (deprecation metadata reader, warning emitter) that have not yet been designed in `init-hook.md`. This is a required follow-up to init-hook.md before this policy can be implemented.

### 3.3 Migration Path Documentation

Every deprecation must be accompanied by a migration guide. The guide is placed in the plugin repository under `docs/migrations/<version>-<feature-name>.md`.

The migration guide must include:

1. **What changed** — the deprecated feature and its replacement (or removal reason if no replacement exists).
2. **Why it changed** — rationale for the deprecation.
3. **How to migrate** — step-by-step instructions, with code examples if applicable.
4. **Timeline** — deprecation version and removal version.
5. **How to verify** — steps the user can take to confirm the migration succeeded.

A consolidated migration index is maintained in `docs/migrations/README.md`.

### 3.4 Removal Timeline

| Phase | Action |
|---|---|
| Deprecation release | Feature is functional but logs a warning. Changelog entry under `### Deprecated`. Migration guide published. |
| One minor release | At least one minor release passes with the deprecation warning in place. |
| Removal release | Feature is removed in the next major version. Changelog entry under `### Removed`. The migration guide remains published for historical reference. |

If a feature must be removed urgently (e.g., security vulnerability), the one-minor-release notice period may be waived by the cooperative at Level 3 escalation.

After an emergency removal, the maintainer must publish a retroactive migration guide documenting the removal and any required configuration changes, even if the standard deprecation notice period was bypassed.

### 3.5 Deprecation of Agents vs Skills

| Component | Deprecation Handling |
|---|---|
| **Agent** | The agent `.md` file is removed from the plugin's bundled `.opencode/agents/` in the removal release. The init hook logs a warning when it skips a deprecated agent file. The agent name is added to a legacy block list so the plugin can warn if a user's `opencode.json` references it. |
| **Skill** | The skill directory is removed from the plugin's bundled `.opencode/skills/` in the removal release. Any agent prompt that references the deprecated skill must be updated in the same release or earlier. |
| **Configuration option** | The option is removed from the init hook's config reader. If the user's `opencode.json` still sets the deprecated option, the init hook logs a warning but does not fail. |

## 4. Release Cadence

### 4.1 Version Numbering

The plugin follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html):

| Bump | When |
|---|---|
| **Major** (1.0.0 → 2.0.0) | Breaking change to agent definitions, skill interfaces, init hook behaviour, or exported plugin hooks. Removal of a deprecated feature. |
| **Minor** (1.0.0 → 1.1.0) | New agent or skill added. New configuration option introduced. Deprecation notice added. Backward-compatible feature addition. |
| **Patch** (1.0.0 → 1.0.1) | Bug fix. Documentation update. Internal refactoring with no behavioural change. Dependency update with no API change. |

A "breaking change" for this plugin includes:

- Removing or renaming an agent `.md` file that users may reference in their workflows.
- Changing the `rs-*` skill prefix or skill names that agents reference via `skill({ name: "..." })`.
- Changing the version-stamping file format or location (see [update-propagation.md](./update-propagation.md)).
- Changing the init hook's contract (`activate` export signature).
- Removing a configuration option from the runtime config reader.

### 4.2 Release Types and Frequency

| Type | Frequency | Contains | Pre-release |
|---|---|---|---|
| **Patch** | As needed (no fixed schedule) | Bug fixes, security patches, dependency updates | Optional: `1.0.1-rc.1` for testing |
| **Minor** | Monthly (target: first week of month) | New features, new agents/skills, deprecations | `1.1.0-beta.1` two weeks before stable |
| **Major** | When breaking changes accumulate (target: no more than 1 per quarter) | Breaking changes, feature removals | `2.0.0-rc.1` one month before stable |

This cadence starts after Phase 1 of the rollout (see [rollout-strategy.md](./rollout-strategy.md)). During Phase 1, releases may be more frequent to address pilot feedback.

### 4.3 Pre-Release Versions

Pre-release versions follow SemVer 2.0 pre-release conventions:

| Pre-release Tag | Purpose | Audience |
|---|---|---|
| `-alpha.1` | Early development, unstable | Plugin maintainers only |
| `-beta.1` | Feature-complete, needs testing | Pilot teams, power users |
| `-rc.1` | Release candidate, final validation | All users (opt-in) |

Pre-release versions are published to GitHub Packages with the pre-release tag. The npm `latest` dist-tag is never updated for a pre-release. A separate `next` dist-tag is used:

```bash
npm dist-tag add @runicengines/opencode-runesmith@1.2.0-beta.1 next
```

Users who want pre-release versions configure their `package.json` to use the `next` tag:

```json
{
  "dependencies": {
    "@runicengines/opencode-runesmith": "next"
  }
}
```

### 4.4 Release Checklist

Every stable release follows this checklist. The maintainer works through it sequentially.

```
□ 1. CHANGELOG — Ensure `## [Unreleased]` section is complete and accurate.
     Verify all entries follow Keep a Changelog 2.0.0 format (Section 5).
     Move Unreleased entries to a new `## [<version>] - <date>` section.

□ 2. Version bump — Run `npm version <patch|minor|major>`.
     This updates package.json and creates a git tag (e.g., `v1.1.0`).

□ 3. Build — Run `npm run build`.
     Verify the built output (dist/) contains all expected files.
     Run the test suite: `npm test`.

□ 4. Verification checklist — Run the full verification checklist from
     verification.md. Document results.

□ 5. Publish — Run `npm publish`.
     Verify the package appears on GitHub Packages:
     https://npm.pkg.github.com/@runicengines/opencode-runesmith

□ 6. Git push — `git push origin main --tags`.
     This triggers the GitHub Actions CI pipeline.

□ 7. GitHub Release — Create a GitHub Release from the tag.
     Title: "Release v<version>"
     Body: Paste the changelog section for this version.
     Attach any binary artifacts (if applicable).

□ 8. Announce — Post in the cooperative's support channel:
     "v<version> released. See https://github.com/RunicEngines/opencode-runesmith/releases/tag/v<version>"

□ 9. Update dist-tag (if pre-release became stable) —
     `npm dist-tag add @runicengines/opencode-runesmith@<version> latest`
```

Steps 1-3 may be done in a release preparation branch. Steps 4-8 are performed on `main` after the version bump commit and tag are pushed.

The release checklist should be automated as a GitHub Actions workflow for Phase 3 (see [rollout-strategy.md](./rollout-strategy.md)). The manual workflow described here is the Phase 1/2 fallback.

## 5. Changelog Conventions

### 5.1 Format

The plugin maintains a `CHANGELOG.md` in the plugin repository following [Keep a Changelog 2.0.0](https://keepachangelog.com/en/2.0.0/). The format is:

```markdown
# Changelog

All notable changes to @runicengines/opencode-runesmith are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- ... (new features, new agents, new skills)

### Changed

- ... (changes to existing functionality)

### Deprecated

- ... (features to be removed in a future major release)

### Removed

- ... (features removed in this release)

### Fixed

- ... (bug fixes)

### Security

- ... (vulnerability fixes)
```

### 5.2 Per-Component Change Tracking

Each changelog entry is prefixed with the affected component type to make the scope clear at a glance:

| Prefix | Component | Example |
|---|---|---|
| `agent:` | Agent definition change | `agent:rs-architect: added webfetch: allow for architecture research` |
| `skill:` | Skill change | `skill:rs-pr-packager: improved conventional commit parsing` |
| `init:` | Init hook change | `init: added phase-aware agent filtering` |
| `plugin:` | Plugin core change | `plugin: updated @opencode-ai/plugin peer dependency to ^0.3.0` |
| `docs:` | Documentation change | `docs: updated migration guide for rs-legacy-analyzer` |
| `ci:` | CI/CD change | `ci: added automated release workflow` |

Example changelog entry:

```markdown
## [1.1.0] - 2026-07-01

### Added

- agent:rs-devops: new DevOps agent for CI/CD and infrastructure workflows
- skill:rs-dependency-checker: new utility skill for vulnerability scanning
- init: version-stamping now logs the previous and new version on mismatch

### Changed

- agent:rs-developer: bash permissions now include `pip *: allow` (was `ask`)
- skill:rs-issue-to-plan: improved GitHub issue link parsing for cross-repo references

### Deprecated

- agent:rs-legacy-analyzer: deprecated in favour of rs-discover; scheduled for removal in 2.0.0

### Fixed

- init: init hook no longer crashes when `.opencode/` directory is missing on first run
- skill:rs-pr-packager: fixed commit range selection when there are merge commits
```

### 5.3 Unreleased Section

The `## [Unreleased]` section is the working area. Every merged PR adds an entry under the appropriate category in the Unreleased section. At release time, the maintainer renames `## [Unreleased]` to `## [<version>] - <date>` and opens a fresh `## [Unreleased]` section.

### 5.4 Pre-Release Version Handling

Pre-release versions are listed in the changelog with their pre-release tag:

```markdown
## [1.1.0-beta.1] - 2026-06-20

### Added

- ... (pre-release features listed here)

---

## [1.0.0] - 2026-06-01
```

The pre-release section is removed when the stable version is released. Pre-release changelogs are primarily for early testers and may be less detailed than stable release notes.

### 5.5 Changelog Location

The changelog lives in the plugin repository (`RunicEngines/opencode-runesmith/CHANGELOG.md`), not in the Knowledge Base. It is referenced here as a specification of what the changelog must contain. The [changelog-manager skill](../../../knowledge/tooling/opencode/skills/changelog-manager.md) knowledge note documents the automated changelog update workflow that the `rs-changelog-manager` skill uses.

## 6. Long-Term Ownership

### 6.1 Succession Plan

If the core maintainer leaves the cooperative or is unable to continue maintaining the plugin, the following succession process applies:

1. The departing maintainer notifies the cooperative via the governance channel.
2. The cooperative nominates a successor (or opens a call for volunteers) within 2 weeks.
3. If no volunteer steps forward, the cooperative may either:
   a. Archive the plugin (see Section 6.3) and remove it from active use.
   b. Contract a member to maintain it with cooperative compensation.
4. Once a successor is identified, the 2-week maintainer onboarding process (Section 1.3) begins, accelerated if the departing maintainer is still available.
5. If the departure is sudden (no notice), the backup maintainer (once appointed) assumes the core maintainer role immediately. If no backup exists, the cooperative appoints an interim maintainer within 1 week.

### 6.2 Knowledge Transfer Plan

Knowledge transfer is triggered when:

- A new maintainer joins (Section 1.3).
- The core maintainer begins offboarding (Section 1.4).
- The succession plan is activated (Section 6.1).

The knowledge transfer covers:

| Topic | Source |
|---|---|
| Plugin architecture overview | [overview.md](../overview.md) |
| Package structure and naming | [package-structure.md](../architecture/package-structure.md) |
| Init hook and version-stamping | [init-hook.md](../architecture/init-hook.md), [update-propagation.md](./update-propagation.md) |
| Permission profiles | [permission-profiles.md](./permission-profiles.md) |
| Rollout strategy and phase gates | [rollout-strategy.md](./rollout-strategy.md) |
| Verification checklist | [verification.md](./verification.md) |
| MCP registration | [mcp-registration.md](../architecture/mcp-registration.md) |
| Distribution rationale | [distribution-comparison.md](../architecture/distribution-comparison.md) |
| Agent-skill mapping | [agent-skills-mapping.md](./agent-skills-mapping.md) |
| All open research questions | [open-questions-resolved.md](./open-questions-resolved.md) |
| This document | [maintenance-governance.md](./maintenance-governance.md) |

All research documents are linked from the topic [README.md](../README.md). The knowledge transfer is considered complete when the incoming maintainer has read each document and can explain the design decisions it contains.

### 6.3 Plugin Archival Process

If the plugin is no longer maintained and no successor can be found, the cooperative may archive it. Archival is a cooperative-level decision (Level 3 escalation).

Archival steps:

1. The plugin repository is marked as archived on GitHub (Settings → Danger Zone → Archive this repository).
2. A final release note is published: "`@runicengines/opencode-runesmith` is no longer maintained. See [ARCHIVED.md](ARCHIVED.md) for alternatives."
3. An `ARCHIVED.md` file is added to the repository root explaining:
   - Why the plugin was archived.
   - What users should do instead (remove the plugin entry from `opencode.json`).
   - Where to find alternative tools or approaches.
   - The archive date and the last maintainer.
4. The npm package `@runicengines/opencode-runesmith` is deprecated on GitHub Packages:
   ```bash
   npm deprecate @runicengines/opencode-runesmith \
     "This package has been archived. See https://github.com/RunicEngines/opencode-runesmith#readme for details."
   ```
5. The plugin entry is removed from the `@runicengines` organisation's recommended tooling documentation.
6. The research files in this knowledge base are updated: the `status` field in all RuneSmith research documents transitions from `exploring` or `accepted` to `superseded`, with a frontmatter field noting the archival reason.

### 6.4 Escrow Arrangement

As a cooperative asset, the plugin's source code and all publishing credentials must be accessible to more than one person:

| Asset | Location | Access |
|---|---|---|
| Source code | GitHub repository (RunicEngines/opencode-runesmith) | All cooperative members have read access |
| Publish token (NPM_TOKEN / GITHUB_TOKEN with write:packages) | Stored as a GitHub Actions secret in the plugin repository | Only maintainers with GitHub Admin access can view/modify |
| Plugin private key (if any) | Not applicable — no code signing | N/A |

If the core maintainer is unavailable and a publish is needed, a cooperative GitHub Admin can generate a new `GITHUB_TOKEN` with `write:packages` scope from the repository settings. This ensures the cooperative is never locked out of its own infrastructure.

## Related Research

| Document | Relationship |
|---|---|
| [rollout-strategy.md](./rollout-strategy.md) | Defines the phased rollout that this governance model supports after Phase 1 |
| [update-propagation.md](./update-propagation.md) | Version-stamping mechanism that release cadence depends on |
| [permission-profiles.md](./permission-profiles.md) | Agent permissions that deprecation policy may modify |
| [verification.md](./verification.md) | Testing checklist that every release must pass |
| [distribution-comparison.md](../architecture/distribution-comparison.md) | Establishes the npm + GitHub Packages distribution that the release process targets |
| [open-questions-resolved.md](./open-questions-resolved.md) | Version numbering question (raised in distribution-comparison.md), resolved here with SemVer 2.0 |

## References

- [Keep a Changelog 2.0.0](https://keepachangelog.com/en/2.0.0/) — Changelog format specification
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) — Version numbering specification
- [GitHub Packages npm Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry) — Publishing target
- [OpenCode Plugins Documentation](https://opencode.ai/docs/plugins) — Plugin development reference

## Conclusion

This document establishes the governance and maintenance framework for `@runicengines/opencode-runesmith` through the project's full lifecycle: from active development with a core maintainer through potential succession or archival. It addresses the open question from [distribution-comparison.md](../architecture/distribution-comparison.md) regarding version numbering strategy by adopting SemVer 2.0 with a monthly minor cadence. It also satisfies the Phase 3 entry criterion from [rollout-strategy.md](./rollout-strategy.md) that a release process must be documented before org-wide rollout.
