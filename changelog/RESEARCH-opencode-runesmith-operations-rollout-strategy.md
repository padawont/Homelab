---
title: "RuneSmith Rollout Strategy"
status: exploring
author: "refactorartist (Khalid Zubair)"
date: 2026-06-09
tags:
  - opencode
  - runesmith
  - rollout
  - deployment
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/publishing-workflow.md"
  - knowledge: "knowledge/tooling/opencode/plugins/github-packages-org-setup/overview.md"
  - knowledge: "knowledge/tooling/opencode/plugins/bundling-components.md"
  - knowledge: "knowledge/tooling/opencode/plugins/init-hook-lifecycle.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
  - knowledge: "knowledge/tooling/opencode/skills/workflow-patterns.md"
references:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/permissions"
    title: "OpenCode Permissions Documentation"
last_audit_date: 2026-06-09
---

# RuneSmith Rollout Strategy

- **Plugin:** `@runicengines/opencode-runesmith`
- **Distribution:** Private npm via GitHub Packages (see [distribution-comparison.md](../architecture/distribution-comparison.md))
- **Status:** Exploring — phased rollout plan under investigation

## Context

The `@runicengines/opencode-runesmith` plugin provides a suite of seven subagents (architect, spec-writer, developer, reviewer, test-writer, tech-writer, devops) and reusable skills to RunicEngines code repositories. The plugin is distributed as a private npm package via GitHub Packages, with agent and skill files copied into each project's `.opencode/` directory via a version-stamping init hook (see [init-hook.md](../architecture/init-hook.md) and [update-propagation.md](./update-propagation.md)).

Rolling a plugin of this scope — seven agents with distinct permission profiles (see [permission-profiles.md](./permission-profiles.md)), workflow and utility skills, MCP integration, and KB discovery capabilities — across an entire cooperative organisation carries significant risk. A single misconfigured permission or unhandled edge case in the init hook could disrupt development workflows across multiple repositories.

This document defines a phased rollout plan that introduces the plugin incrementally, validates each phase against measurable success criteria, and provides clear rollback paths at every stage.

## Phase 1: Pilot

The pilot phase is a controlled, low-risk introduction of the RuneSmith plugin to 1-2 friendly repositories and teams. The goal is to validate the plugin's core installation, activation, and agent workflow mechanics in a real development context before expanding to a larger audience.

### Entry Criteria

Before Phase 1 begins, the following must be satisfied:

- [ ] Plugin package `@runicengines/opencode-runesmith` published to GitHub Packages with `access: restricted`
- [ ] npm auth documentation written: `.npmrc` + `GITHUB_TOKEN` setup guide
- [ ] Init hook implemented and tested: version-stamping, copy logic, fail-open error handling
- [ ] Verification checklist (see [verification.md](./verification.md)) passes in a controlled test environment
- [ ] All seven agent `.md` files bundled and resolvable
- [ ] All skill directories bundled and loadable via `skill({ name: "rs-*" })`
- [ ] KB discovery skill configured with the knowledge-base repository URL
- [ ] Rollback procedure documented and rehearsed (see Rollback section below)
- [ ] Pilot team identified and briefed on the experiment scope

### Pilot Team Selection Criteria

Candidate pilot teams must satisfy:

| Criterion | Requirement |
|---|---|
| Repo maturity | Active development (commits in last 7 days), not in maintenance mode |
| Team size | 2-5 developers actively using OpenCode |
| Repo complexity | Moderate — single service or library, not a monorepo |
| Risk tolerance | Team explicitly agrees to be a pilot, understands instability is possible |
| Availability | At least 2 weeks of uninterrupted pilot window (no team members on extended leave) |
| Communication | Team has a designated point of contact for feedback collection |

Recommended candidates: `RunicEngines/knowledge-base` (the KB team already understands the plugin's value proposition) and one small code repository (e.g., an internal tool or utility library).

### Phase 1 Feature Set

Only a subset of the full plugin capability is enabled during the pilot:

| Capability | Phase 1 Setting | Rationale |
|---|---|---|
| Agents available | `rs-architect`, `rs-developer`, `rs-reviewer` only | Core development loop: plan, implement, review |
| Spec-Writer | Disabled | Spec generation adds process overhead — not needed for pilot validation |
| Test-Writer | Disabled | Test automation depends on developer first — validate in later phase |
| Tech-Writer | Disabled | Documentation generation is non-critical for pilot |
| DevOps | Disabled | Infrastructure automation carries too much risk for Phase 1 |
| Write access | Default: read-only (`edit: deny` for non-developer agents); developer: `edit: ask` | `edit: allow` on developer requires user confirmation |
| bash access | Developer uses the same layered profile as [permission-profiles.md](./permission-profiles.md), but with `pip *` changed to `ask` for Phase 1 | Following the permission profiles design but enforcing the ask catch-all |
| Skills | `rs-issue-to-plan`, `rs-pr-packager`, `rs-discover`, `rs-consult` | Core workflow + discovery skills only |
| MCP servers | None in Phase 1 | MCP integration adds deployment complexity; defer to Phase 2 |
| KB discovery | Enabled for architect only | Architect needs KB context for planning; developer and reviewer do not |

This feature set is deliberately narrow. It validates the two most critical properties of the plugin: that the init hook installs agents correctly (see [verification.md](./verification.md) sections 1-2) and that the architect-developer-reviewer loop functions end-to-end.

Phase 1 ships modified agent .md files with restricted permissions baked in. This ensures safety by default — even if someone misconfigures their phase setting, the agent files they receive match their intended phase.

### Phase 1 Duration

3 calendar weeks (approximately 15 working days for full-time contributors), broken into:

| Week | Focus |
|---|---|
| Week 1 | Installation, onboarding, and initial usage — developers install the plugin, run through verification checklist, perform first `@rs-architect` delegation |
| Week 2 | Active use — teams use the plugin for real development tasks (bug fixes, small features) |
| Week 3 | Extended validation — stress-tested with larger tasks; feedback collection; retrospective |

If the pilot team completes the verification checklist and achieves the success metrics before 3 weeks, the phase may end early. If blockers are found, the phase is extended by up to 1 week for fix-and-retest.

### Phase 1 Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| Installation success rate | 100% of pilot developers | All team members running the plugin without init hook errors |
| Agent invocation rate | >= 10 sessions per developer per week | Telemetry: `@rs-*` mentions in OpenCode sessions |
| Architect delegation success | >= 80% of task() calls succeed without error | Log analysis from architect agent |
| Developer workflow completion | >= 70% of started tasks reach PR creation | Count `rs-pr-packager` invocations vs. task starts |
| Reviewer accuracy | No false positives in code review comments | Manual review of a sample of reviewer output |
| User satisfaction score | >= 3.5 / 5.0 | Anonymous survey at end of Phase 1 |
| Rollback incidents | 0 unplanned rollbacks | Incident log |
| Critical bugs (S1/S2) | 0 | Bug tracker |

### Phase 1 Exit Criteria (Gate to Phase 2)

All of the following must be true before Phase 2 begins:

- All Phase 1 success metrics met for 2 consecutive weeks
- No unresolved S1 or S2 bugs
- Rollback procedure executed successfully in a dry run
- Pilot retrospective completed with written findings
- At least 3 user feedback submissions collected (survey or interview)
- All Phase 2 entry criteria satisfied (see below)

## Phase 2: Team Expansion

Phase 2 expands the plugin to the entire engineering department or team (approximately 10-25 developers across multiple repositories). This phase validates that the plugin scales beyond friendly early adopters to a broader, less-invested audience.

### Entry Criteria

Before Phase 2 begins, the following must be satisfied:

- [ ] All Phase 1 exit criteria met
- [ ] Phase 1 blockers resolved and documented
- [ ] User onboarding guide written and reviewed (based on Phase 1 feedback)
- [ ] FAQ document created covering common installation issues, permission errors, and troubleshooting
- [ ] Phase 1 bug fixes shipped as plugin patch release
- [ ] Update propagation tested end-to-end (version-stamping + CLI update command, see [update-propagation.md](./update-propagation.md))
- [ ] Slack/Discord channel or GitHub Discussion category created for RuneSmith support
- [ ] Phase 2 feature gate configuration implemented (see below)
- [ ] All target team leads briefed and consent obtained

### Phase 2 Feature Set

| Capability | Phase 2 Setting | Rationale |
|---|---|---|
| Agents available | All 7 agents enabled | Full agent suite for comprehensive workflow testing |
| Write access | Full permission profiles per [permission-profiles.md](./permission-profiles.md) (includes reviewer `edit: deny`, tech-writer `bash: deny`) | Escalated from Phase 1 read-only; full permission profiles enforced |
| Skills | All workflow + utility skills enabled | Validate full skill chain (see [verification.md](./verification.md) section 4) |
| MCP servers | Enabled for opt-in repos only (see [mcp-registration.md](../architecture/mcp-registration.md) for setup) | MCP integration tested in a subset before org-wide |
| KB discovery | Enabled for all agents | All roles reference KB during workflows |
| Custom skills | Teams may request custom `rs-*` skills via PR | Tests the skill extensibility model |
| Update channel | Stable release channel (semver minor updates) | Regular updates with backward compatibility |

Permission profiles shift from the restricted Phase 1 model to the full permission matrix defined in [permission-profiles.md](./permission-profiles.md). This means:

- Reviewer gains `edit: deny` (enforcing the audit boundary)
- Tech-writer gains `bash: deny` (no shell access for documentation agents)
- Developer returns to the full layered `allow/ask/deny` profile with `"rm -rf *": deny`
- DevOps gains `docker *: ask` and `kubectl *: deny`, `aws *: deny`

The escalation is intentional — Phase 1 restricted permissions artificially to reduce blast radius. Phase 2 validates the actual permission design in a broader context.

### Phase 2 Duration

6 weeks (30 working days), broken into:

| Period | Focus |
|---|---|
| Weeks 1-2 | Onboarding wave — teams install plugin, complete onboarding guide, run smoke tests |
| Weeks 3-4 | Active use — teams use full agent suite for regular development work |
| Weeks 5-6 | Extended validation, MCP integration tests, feedback collection, retrospective |

If blockers are found, the phase is extended by up to 2 weeks for fix-and-retest. If exit criteria cannot be met after the maximum extension, a phase-gate review with all stakeholders decides whether to: (a) reduce scope and proceed, (b) return to Phase 1 with new learnings, or (c) halt the rollout.

### Phase 2 Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| Adoption rate | >= 80% of eligible developers | Plugin installation count vs. total developers in scope |
| Active repo coverage | >= 70% of target repos | Repos with >= 5 agent invocations per week |
| Agent invocation rate | >= 5 sessions per developer per week | Telemetry |
| Delegation success rate | >= 85% of architect task() calls | Log analysis |
| Time saved (self-reported) | >= 2 hours saved per developer per week | Survey at weeks 3 and 6 |
| User satisfaction score | >= 4.0 / 5.0 | Anonymous survey at end of Phase 2 |
| Skill chain completion | >= 90% of chained skills resolve correctly | Telemetry: skill dependency resolution |
| Error rate | <= 5% of agent invocations end in unhandled error | Log analysis |
| Rollback incidents | <= 1 unplanned rollback | Incident log |
| Support tickets | Decreasing week-over-week after week 3 | Support channel volume |

### Phase 2 Exit Criteria (Gate to Phase 3)

All of the following must be true before Phase 3 begins:

- All Phase 2 success metrics met for 3 consecutive weeks
- No unresolved S1 or S2 bugs for 2 consecutive weeks
- Support ticket volume at or below 5 per week for 2 consecutive weeks
- At least 10 user feedback submissions collected (mix of survey and interview)
- Performance baseline established (session latency, init hook timing, agent response time)
- Training materials created and delivered to at least one training session
- Phase 2 retrospective completed with written findings
- All Phase 3 entry criteria satisfied (see below)

## Phase 3: Org-Wide

Phase 3 rolls out the RuneSmith plugin to all RunicEngines repositories and developers. This is the final phase — after this, the plugin becomes a standard part of the cooperative's development infrastructure.

### Entry Criteria

Before Phase 3 begins, the following must be satisfied:

- [ ] All Phase 2 exit criteria met
- [ ] Phase 2 blockers resolved and documented
- [ ] Performance baselines documented and shared with org
- [ ] Training materials published (onboarding guide, FAQ, troubleshooting, video walkthrough)
- [ ] Support rotation established (who handles RuneSmith issues, response time SLAs)
- [ ] Release process documented (versioning, changelog, publishing workflow)
- [ ] Org-wide communication sent (announcement with timeline, expectations, support channels)
- [ ] Phase 3 feature gate configuration implemented (full permissions)
- [ ] All repository maintainers briefed and opt-in confirmed

### Phase 3 Feature Set

| Capability | Phase 3 Setting | Rationale |
|---|---|---|
| Agents available | All 7 agents, full capability | Complete agent suite with no restrictions |
| Write access | Full permission profiles per [permission-profiles.md](./permission-profiles.md) | Least-privilege model in effect across org |
| Skills | All skills, including custom team skills | Full skill ecosystem |
| MCP servers | Enabled per-repo configuration | Repos opt-in to MCP servers as needed |
| KB discovery | Full cross-repo discovery | All repos can search the KB |
| Custom agents | Teams may define custom subagents referencing RuneSmith skills | Plugin serves as a platform, not just a product |
| Permissions | Per-repo configuration via `opencode.json` | Repos can tighten or relax as appropriate |
| Update channel | Stable + beta channels | Org adopts stable; power users can beta test |

MCP enablement uses the manual setup approach documented in [architecture/mcp-registration.md](../architecture/mcp-registration.md) — the plugin provides copy-paste configuration snippets; developers add them to their `opencode.json`. No programmatic MCP registration exists in the current OpenCode SDK.

### Phase 3 Duration

Ongoing — no fixed end date. The first 8 weeks are a monitored rollout period, after which the plugin enters business-as-usual maintenance.

| Period | Focus |
|---|---|
| Weeks 1-4 | Onboarding wave across all remaining repos — coordinated by repo maintainers |
| Weeks 5-8 | Monitoring and stabilization — track metrics, resolve edge cases, iterate on support |
| Week 8+ | Business-as-usual — plugin is standard infrastructure |

### Phase 3 Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| Org adoption rate | >= 90% of active developers | Plugin installation count vs. total active developers |
| Org repo coverage | >= 85% of active repos | Repos with >= 3 agent invocations per week |
| Agent invocation rate | >= 5 sessions per developer per week | Telemetry |
| User satisfaction score | >= 4.2 / 5.0 | Quarterly survey |
| Time saved (org-wide) | >= 3 hours saved per developer per week | Quarterly survey |
| Error rate | <= 2% of agent invocations end in unhandled error | Log analysis |
| Support ticket volume | <= 10 per week (org-wide average) | Support channel |
| Rollback frequency | 0 rollbacks per quarter | Incident log |
| Update adoption | >= 80% of repos on latest minor version within 2 weeks of release | Version stamp telemetry |

### Phase 3 Gating — No Further Gate

Phase 3 ends the rollout sequence. There is no Phase 4. After Phase 3 success metrics are stable for 8 consecutive weeks, the plugin moves from rollout status to standard infrastructure. The research status transitions from `exploring` to `accepted` and eventually `completed`.

## Rollback Criteria and Procedure

Rollback conditions are defined per severity level. Any condition triggers the rollback procedure for the affected repos.

### Rollback Triggers

| Severity | Condition | Action | Response Time |
|---|---|---|---|
| S1 — Critical | Plugin prevents OpenCode from starting in any repo | Manual recovery: developer removes the plugin entry from opencode.json, deletes .opencode/agents/, .opencode/skills/, and the version stamp file, re-adds the plugin entry, and restarts OpenCode (see Phase 1 rollback procedure). | Immediate |
| S1 — Critical | Agent makes unauthorized file modifications (edit: deny bypassed) | Immediate manual rollback of affected agents | Immediate |
| S1 — Critical | Permission escalation: leaf agent gains task capability | Immediate manual full rollback | Immediate |
| S2 — High | Session latency exceeds 2x baseline for > 30 minutes | Manual rollback on team lead decision | Within 1 hour |
| S2 — High | > 10% of agent invocations fail with unhandled errors | Manual rollback on team lead decision | Within 2 hours |
| S2 — High | Init hook overwrites user files outside `.opencode/agents|skills/` | Immediate manual rollback per phase procedure | Immediate |
| S3 — Medium | Skill chain breaks for a critical workflow (e.g., `rs-issue-to-plan`) | Roll back affected skills; patch and re-release | Within 1 business day |
| S3 — Medium | Version stamp comparison fails silently (no re-copy on update) | Roll back to previous stamp logic; patch | Within 1 business day |
| S4 — Low | Minor permission misconfiguration (e.g., overly permissive bash rule) | Patch in next release; no rollback needed | Next patch release |

### Rollback Procedure

The rollback procedure differs by phase because the blast radius grows with each phase.

#### Phase 1 Rollback

For the pilot repos (1-2 repos):

1. Notify the pilot team via their designated communication channel.
2. The affected repo reverts the `opencode.json` plugin entry: remove `"@runicengines/opencode-runesmith"` from the `plugin` array.
3. Run the cleanup script to remove copied agent/skill files:
    ```bash
    rm -rf .opencode/agents/rs-*.md .opencode/skills/rs-*/ .opencode/.runesmith-version
    ```
4. Restart OpenCode. The missing agents and skills are no longer available.
5. File a bug report with reproduction steps, logs, and the version stamp from the affected repo.
6. The plugin maintainer publishes a patch release addressing the trigger condition.
7. Clear the OpenCode npm cache: `rm -rf ~/.cache/opencode/node_modules/@runicengines/opencode-runesmith`
8. The pilot team re-adds the plugin entry to `opencode.json` and restarts to re-install.

#### Phase 2 Rollback

For a team-level rollout (up to 10-25 developers):

1. The support lead notifies all affected teams via the support channel.
2. Individual repos follow the Phase 1 rollback procedure (remove plugin entry, clean up files).
3. For org-wide rollback (all Phase 2 repos), the plugin maintainer publishes a rollback release:
   - Increment the patch version (e.g., `1.2.0` -> `1.2.1`).
   - The rollback release reverts the offending change.
   - Developers run `bunx @runicengines/opencode-runesmith update` to trigger re-install.
   - Note: Ensure the update command uses Bun-native APIs (bun cache, bun install) consistent with bunx invocation.
4. If the rollback crosses a major or minor version boundary, the version-stamping logic handles it automatically (see [update-propagation.md](./update-propagation.md) — rollback handling).

#### Phase 3 Rollback

For an org-wide rollout (all repos):

1. The support lead declares an incident via the organisation's incident management process.
2. The plugin maintainer publishes an emergency patch release.
3. The `bunx @runicengines/opencode-runesmith update` command is broadcast via the org support channel.
4. Repos with urgent blockers (S1/S2) run the update command immediately.
5. Non-critical repos update within their normal schedule.
6. After the incident, a post-mortem is conducted and the rollout strategy is updated.

## Feedback Loops

Feedback collection is built into every phase. The mechanism varies by phase scope and intensity.

### Per-Phase User Surveys

| Phase | Survey Timing | Sample Size | Format |
|---|---|---|---|
| Phase 1 | End of week 1, end of week 3 | All pilot developers (2-5) | Structured interview (30 min) |
| Phase 2 | End of week 3, end of week 6 | All Phase 2 developers (10-25) | Anonymous survey (15 min) |
| Phase 3 | Quarterly after rollout stabilises | All active developers (org-wide) | Anonymous survey (10 min) |

Survey questions cover three categories:

- **Installation experience**: How easy was it to set up? Any auth issues? Any init hook errors?
- **Daily usage**: How often do you invoke agents? Which agent is most useful? Which is confusing?
- **Outcome**: Do you feel the plugin saves you time? What is missing? What would make you stop using it?

### Automated Telemetry

The plugin collects the following telemetry (opt-in at Phase 1, opt-in with a prompt at plugin activation encouraging participation at Phase 2, and expected as a condition of use at Phase 3):

| Event | Data Collected | Purpose |
|---|---|---|
| Plugin activation | Version string, init hook success/failure, stamp comparison result | Track installation health |
| Agent invocation | Agent name, session ID, success/failure, duration | Track adoption and error rates |
| Agent delegation | Source agent, target agent, task outcome | Track architect delegation success |
| Skill invocation | Skill name, chaining depth, success/failure | Track skill reliability |
| Permission check | Agent name, tool requested, allowed/denied | Track permission enforcement |
| Update event | Previous version, new version, stamp overwrite count | Track update propagation |

Telemetry is written to a local `.runesmith/telemetry/` directory. Teams may opt out by removing the telemetry directory. No data is sent to external servers in Phase 1 or Phase 2. In Phase 3, aggregated telemetry may be reported to a central dashboard for org-wide health monitoring. The `.runesmith/telemetry/` directory should be added to `.gitignore` to prevent accidental commits of local telemetry data.

The Phase 3 transition to required telemetry is a cooperative governance decision beyond the scope of this technical rollout document.

### Issue Tracking

Each phase uses GitHub issue labels to track feedback:

| Label | Purpose |
|---|---|
| `runesmith-pilot` | Phase 1 pilot feedback and bugs |
| `runesmith-team` | Phase 2 team expansion feedback |
| `runesmith-org` | Phase 3 org-wide feedback |
| `runesmith-bug` | Plugin bugs (any phase) |
| `runesmith-enhancement` | Feature requests (any phase) |
| `runesmith-rollback` | Rollback incidents and post-mortems |

All feedback issues are filed in the `RunicEngines/knowledge-base` repository under these labels.

### Phase-Gate Reviews

At the end of each phase, a phase-gate review is conducted before promotion to the next phase. The review involves:

**Participants:**

- Plugin maintainer(s)
- Phase participant representatives (at least 2 developers from the current phase)
- A non-participating facilitator (to reduce bias)

**Review Agenda:**

1. Success metrics review — did we meet targets? Where did we fall short?
2. Bug/incident log review — what went wrong? What was fixed? What is outstanding?
3. Feature completeness — did the enabled feature set cover the use cases adequately?
4. User feedback summary — themes from surveys and interviews
5. Rollback readiness — is the procedure documented and rehearsed?
6. Go/No-go decision — does the next phase entry criteria pass?

**Decision Rules:**

- All entry criteria must be met (checked boxes or documented waivers).
- No unresolved S1/S2 bugs.
- Unanimous consent from review participants.

## Phased Feature Gating Architecture

Feature gating across phases is implemented at multiple levels to minimise the blast radius of any single misconfiguration.

### Level 1: Plugin Version

The plugin version itself is the outermost gate. Each phase pins a version range:

| Phase | Version Range | Mechanism |
|---|---|---|
| Phase 1 | `1.0.x` (patch-only) | Users pin exact version in `package.json` |
| Phase 2 | `^1.0.0` (minor-compatible) | Users specify semver range |
| Phase 3 | `^1.0.0` or latest | Users may track latest |

The version-stamping init hook (see [init-hook.md](../architecture/init-hook.md)) ensures that the installed agent/skill files match the pinned version. A repo in Phase 1 that is accidentally pointed at a Phase 3 release will receive all agents and permissions — which defeats the gating purpose. Therefore, version pinning is enforced by convention: Phase 1 repos pin to `1.0.x`, and the init hook logs a warning if the installed version exceeds the phase's allowed range.

### Level 2: Agent Availability

The init hook conditionally copies agent files based on the phase configuration. A `.runesmith-config.json` file in the plugin package root defines which agents and skills are active per phase:

```json
{
  "phases": {
    "1": {
      "agents": ["rs-architect", "rs-developer", "rs-reviewer"],
      "skills": ["rs-issue-to-plan", "rs-pr-packager", "rs-discover", "rs-consult"],
      "mcp": false
    },
    "2": {
      "agents": ["rs-architect", "rs-spec-writer", "rs-developer", "rs-reviewer", "rs-test-writer", "rs-tech-writer", "rs-devops"],
      "skills": ["*"],
      "mcp": "opt-in"
    },
    "3": {
      "agents": ["*"],
      "skills": ["*"],
      "mcp": "per-repo"
    }
  }
}
```

The init hook reads the phase number from the project's `opencode.json` (under a `runesmith.phase` key) or defaults to Phase 1:

```json
{
  "plugin": ["@runicengines/opencode-runesmith"],
  "runesmith": {
    "phase": 2
  }
}
```

Only the agents and skills listed for that phase are copied into `.opencode/`. This prevents Phase 1 developers from accidentally invoking agents that are not yet validated.

The Level 2 agent availability gating depends on init hook behavior (phase-aware selective agent copying) that has not yet been designed in [init-hook.md](../architecture/init-hook.md). This document identifies a required follow-up to init-hook.md.

This assumes OpenCode ignores unknown top-level keys in `opencode.json`. Verify this assumption during implementation. If rejected by the schema, nest configuration inside the plugin entry's metadata field instead.

### Level 3: Permission Profiles

Within each phase, agents enforce the permission profiles defined in [permission-profiles.md](./permission-profiles.md). Phase 1 uses a restricted subset (read-only defaults, developer `edit: ask`). Phase 2 and Phase 3 use the full profile matrix.

Permission enforcement is not gated by the plugin — it is inherent to each agent's `.md` file. The phased approach controls which agents are available (and therefore which permission profiles are in play).

### Level 4: Runtime Feature Flags

For rapid toggling without a plugin release, the init hook can check a runtime feature flag. These flags are environment variables or a local config file:

```bash
RUNESMITH_FEATURES=mcp,devops,beta-skills
```

Runtime flags are intended for emergency gating only (e.g., disabling the DevOps agent org-wide while a permission bug is patched). Feature flags override the phase configuration — a flag set to `disable:devops` prevents the DevOps agent from being copied regardless of the phase setting.

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Plugin installation fails due to npm auth | Medium | High — blocks all usage | Document auth setup; provide troubleshooting script; support channel |
| Init hook corrupts existing agent/skill files | Low | High — disrupts existing workflows | Version-stamping prevents unnecessary overwrites; rollback procedure documented |
| Agent makes incorrect code changes | Medium | Medium — diff review catches errors | Reviewer agent with `edit: deny` provides independent audit; developer `edit: ask` confirms changes |
| Permission escalation in leaf agents | Low | Critical — unauthorised access | Leaf agents have `task: deny`; permission profiles enforced at agent definition level |
| Update propagation fails silently | Medium | Medium — users on stale versions | Version-stamping logs mismatch; CLI update command provides manual override |
| Org-wide rollout exceeds support capacity | Medium | High — degraded support response | Phased rollout limits blast radius; support rotation established before Phase 3 |
| Pilot team becomes dependent on incomplete plugin | Low | Medium — disruption if plugin is rolled back | Pilot team briefed on experimental nature; rollback procedure rehearsed |
| Cooperative governance rejects mandatory telemetry | Medium | High — Phase 3 success measurement impossible | Phase 3 metrics should include fallback measurement methods (surveys, manual reporting) that don't depend on mandatory telemetry |

## Timeline Summary

```
Phase 1: Pilot (3 weeks)
├── Week 1: Install + verify (2 repos, 2-5 devs)
├── Week 2: Active use
├── Week 3: Extended validation + gate review
│
▼ Phase Gate Review
│
Phase 2: Team Expansion (6 weeks)
├── Weeks 1-2: Onboarding wave (10-25 devs)
├── Weeks 3-4: Active use with full agent suite
├── Weeks 5-6: Extended validation + MCP tests + gate review
│
▼ Phase Gate Review
│
Phase 3: Org-Wide (8-week monitored rollout, then ongoing)
├── Weeks 1-4: Onboarding all remaining repos
├── Weeks 5-8: Monitoring and stabilization
├── Week 8+: Business-as-usual (plugin = standard infrastructure)
```

Total monitored rollout duration: 17 weeks (Phase 1 + Phase 2 + Phase 3 monitored period). After this, the plugin transitions to standard infrastructure with quarterly surveys and continuous improvement.

## Related Research

This rollout strategy builds on and feeds into the following RuneSmith research documents:

| Document | Relationship |
|---|---|
| [init-hook.md](../architecture/init-hook.md) | Provides the gating mechanism for phased agent/skill installation |
| [permission-profiles.md](./permission-profiles.md) | Defines the permission matrix that Phase 2+ enforces |
| [update-propagation.md](./update-propagation.md) | Handles version management across phases and rollbacks |
| [verification.md](./verification.md) | Provides the smoke test checklist used for phase-exit validation |
| [distribution-comparison.md](../architecture/distribution-comparison.md) | Establishes the npm + GitHub Packages distribution model that phases depend on |
| [mcp-registration.md](../architecture/mcp-registration.md) | Documents the manual MCP setup approach that Phase 2/3 rely on; no programmatic registration available |

## Conclusion

This three-phase rollout strategy for `@runicengines/opencode-runesmith` provides a structured, risk-controlled path from a 2-repo pilot to org-wide adoption. Each phase is bounded by clear entry and exit criteria, measurable success metrics, documented rollback procedures, and feedback loops that inform the next phase.

The phased approach addresses the three highest-risk aspects of the rollout:

1. **Installation and init hook correctness** — validated in Phase 1 with a small, cooperative pilot team before broader exposure.
2. **Permission profile enforcement** — tested in Phase 1 with restricted permissions, escalated to full profiles in Phase 2.
3. **Org-wide scale** — achieved in Phase 3 only after performance baselines and support infrastructure are established.

Feature gating at four levels (plugin version, agent availability, permission profiles, runtime flags) ensures that each phase operates within a well-defined blast radius and can be rolled back independently.
