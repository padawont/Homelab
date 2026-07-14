---
title: "RuneSmith Testing Methodology"
status: exploring
author: "refactorartist (Khalid Zubair)"
date: 2026-06-09
tags:
  - opencode
  - runesmith
  - testing
  - quality
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/init-hook-lifecycle.md"
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-09
---

# RuneSmith Testing Methodology

- **Topic:** Testing the `@runicengines/opencode-runesmith` plugin — agents, skills, infrastructure, and lifecycle
- **Plugin context:** Seven subagents (architect, spec-writer, developer, reviewer, test-writer, tech-writer, devops), workflow and utility skills, version-stamping init hook, KB discovery, MCP integration
- **Status:** Exploring — framework definition, dataset design, judge pattern under investigation

## 1. Testing Framework Overview

Testing a plugin that ships LLM-powered agents and skills requires a taxonomy that separates concerns that can be automated deterministically from those that must be evaluated qualitatively. The RuneSmith testing framework defines five test types, with a composite Regression Suite (Section 1.6) that runs all types together as a lifecycle gate:

### 1.1 Deterministic Tests

Code paths with no LLM involvement. These run in CI on every commit and must pass before a merge.

| Test Area | What It Covers | Examples |
|---|---|---|
| Init hook | File copy logic, version-stamp comparison, phase gating | `initHookCopiesAgentsOnFreshInstall`, `initHookSkipsCopyWhenVersionMatches`, `initHookOnlyCopiesPhaseAgents` |
| File operations | Agent `.md` parsing, SKILL.md structure, directory creation | `agentFileParsesFrontmatter`, `skillDirCreatedWithSKILLmd` |
| Permissions | Permission DSL parsing, deny/allow/ask evaluation | `reviewerDenyEdit`, `developerAllowGitCommit`, `devopsDenyKubectl` |
| Version-stamping | Stamp read/write, comparison, update trigger | `stampFileWrittenOnInit`, `stampMismatchTriggersReCopy`, `stampMatchSkipsReCopy` |
| CLI commands | `update` command, cache clearing, status reporting | `updateCommandClearsCache`, `updateCommandReportsCurrentVersion` |

**Test runner:** `bun test` (lightweight, fast startup, TypeScript-native). Tests live in `tests/deterministic/` within the plugin package.

**Pass requirements:** 100% pass rate. No flaky tests. Timeout per test: 5 seconds.

### 1.2 Contract Tests

Verify that agent outputs conform to expected schemas and structural requirements. These are semi-deterministic — the test checks shape, not semantic correctness.

| Contract Area | What It Checks |
|---|---|
| Agent frontmatter | Required fields present (`title`, `status`, `author`, `date`, `tags`), types correct, dates valid |
| Permission structure | `edit`, `bash`, `task` keys present per agent type; no undefined permissions |
| Skill SKILL.md | `name`, `description`, `tool` fields present; `name` matches kebab-case convention |
| Delegation format | `task()` calls use valid agent names; no self-delegation; no delegation from leaf agents |
| KB search results | Result set is a valid JSON array; each result has `path` and `relevance` fields |

**Test runner:** Same as deterministic — `bun test`. Tests in `tests/contract/`.

**Pass requirements:** 100% pass rate. Contract tests are schema-level checks; a failure indicates a structural bug that would break agent loading.

### 1.3 Golden Dataset Evaluation

The core of quality assurance for LLM-dependent behavior. A curated set of test cases with known-good expected behaviors, evaluated by an LLM judge.

Each test case in the dataset represents a realistic scenario the plugin agents will encounter. The golden dataset is the primary mechanism for detecting regressions in agent reasoning, instruction-following, and output quality.

See [Section 2 — Golden Dataset Design](#2-golden-dataset-design) for details on case construction, sizing, and maintenance.

### 1.4 Adversarial Tests

Deliberate edge cases designed to test agent robustness. These probe failure modes that realistic inputs may not trigger but that would be damaging if they occurred.

| Category | Examples |
|---|---|
| Pathological inputs | Empty issue descriptions, 10,000-word prompts, multi-byte unicode in agent names, infinite loops in skill chaining |
| Permission bypass attempts | Agent requests `edit: allow` then performs destructive operation; leaf agent calls `task()` despite `task: deny` |
| Resource exhaustion | Concurrent agent invocations (10x, 50x), large file reads in KB search, deeply nested skill chains (100 levels) |
| Missing dependencies | KB repo unreachable, npm package missing, lockfile conflicts, `.opencode/` directory deleted mid-session |

**Test runner:** Scripted scenarios via `bun test` with timeout and resource limits. Tests in `tests/adversarial/`.

**Pass requirements:** 80% of adversarial tests must pass on first run. Failed tests are reviewed for validity — a test that fails because the agent correctly refused a destructive request is a pass, not a failure. Adversarial test results are manually inspected before each release.

### 1.5 Integration Tests

Multi-agent pipeline end-to-end, skill chain resolution, and gate failure recovery.

| Scenario | What It Validates |
|---|---|
| Architect → Developer → Reviewer pipeline | Full delegation chain: architect plans, developer implements, reviewer inspects |
| Skill chain: `rs-issue-to-plan` | Issue fetched → context gathered → plan drafted → plan reviewed |
| Gate failure: reviewer rejects work | Developer receives feedback, reworks, reviewer re-inspects |
| Init hook failure recovery | If init hook fails mid-copy, .opencode/agents is left in a consistent state (all-or-nothing) |
| KB discovery + cross-reference | Agent searches KB, resolves cross-links, and presents findings coherently |

**Test runner:** Integration test harness in `tests/integration/`. Each test starts a simulated OpenCode session, invokes the agent pipeline, and collects all intermediate outputs.

**Pass requirements:** 100% pass rate for core pipelines (architect → developer → reviewer). 90% for secondary pipelines (spec-writer → test-writer, tech-writer documentation generation).

### 1.6 Regression Suite (Composite)

The Regression Suite is not a distinct test type — it is a lifecycle composition of all five test types run before each release. No regressions allowed.

**Trigger:** Pre-release CI pipeline (see [Section 4 — Testing Lifecycle](#4-testing-lifecycle)).

**Coverage:** All deterministic tests, all contract tests, all golden dataset cases, all adversarial tests, all integration tests.

**Pass requirements:**
- Deterministic + contract: 100%
- Golden dataset: >= 95% of cases pass on the Pro judge
- Adversarial: >= 80% pass (manually verified)
- Integration: 100% core, 90% secondary

If any regression is detected (a case that passed previously now fails), the release is blocked. The regression must be fixed or the failing case must be removed from the dataset with a documented reason.

**Future test types: Performance/benchmark testing** — Pre-release measurement of agent latency (response time) and throughput (concurrent sessions) is not yet included in the automated test taxonomy. These concerns are currently deferred to post-release telemetry monitoring (Section 4.4), which tracks session latency percentiles and invocation rates in production. As the plugin matures, benchmark tests may be elevated to a pre-release test type, running synthetic load scenarios against a staging environment before release.

## 2. Golden Dataset Design

### 2.1 What Makes a Good Test Case

A golden dataset test case must be:

| Property | Requirement | Rationale |
|---|---|---|
| **Representative** | Mirrors a realistic input the plugin will receive in production | Non-representative cases train the judge to evaluate the wrong behaviors |
| **Edge-case-rich** | Includes boundary conditions (empty fields, missing context, permission edge cases) | Broadens coverage without linearly increasing dataset size |
| **Deterministic-expected-behavior** | The expected behavior can be objectively verified — either the agent did X or it did not | Subjective expected behaviors ("write a good plan") produce unreliable judge scores |
| **Isolated** | Does not depend on external state (network, specific repo state, time of day) | Tests must be reproducible across runs and environments |
| **Single-responsibility** | Tests exactly one capability per case | Failure attribution is clear — did the architect fail to plan, or did the developer fail to implement? |

**Bad test case example:**
> Issue: "Fix the login bug" → Agent should produce a complete PR.
> *Problem: Vague input, subjective expected behavior, multi-responsibility.*

**Good test case example:**
> Issue with clear description, codebase context with a known bug, expected output is a PR description containing specific changes. The checklist is: (1) PR description references the correct issue, (2) diff modifies the expected files, (3) no unrelated files modified.

### 2.2 Dataset Sizing

| Phase | Target Size | Coverage Goal |
|---|---|---|
| Initial (MVP) | 20-50 cases per agent | Core workflows: architect planning, developer implementation, reviewer inspection |
| Growth (v1.x) | 50-100 cases per agent | Expanded to all skill chains, permission profiles, error recovery paths |
| Mature (v2+) | 100+ cases per agent | Full coverage: all agent types, all skills, all known edge cases, regression cases from production bugs |

A case per agent means per primary capability. A single "architect plans feature" case exercises multiple skills. Scale is driven by observed failure modes in production — if a bug is found, a test case is added to prevent regression.

**Total dataset size targets:**

| Phase | Total Cases (all agents) | Storage Estimate |
|---|---|---|
| Initial | 140-350 (7 agents × 20-50) | ~1-3 MB (JSON/YAML) |
| Growth | 350-700 | ~3-7 MB |
| Mature | 700+ | ~7-15 MB |

### 2.3 Dataset Structure

Each test case is a JSON object stored in a versioned directory within the plugin repo.

```json
{
  "id": "rs-architect-001",
  "agent": "rs-architect",
  "capability": "feature-planning",
  "description": "Plan a REST endpoint for user profile updates",
  "input": {
    "issue": "Add PUT /users/:id endpoint for updating user profiles. Fields: name, email, avatar_url. Validation: name required, email format, avatar_url optional URL.",
    "context": {
      "repo": "express-api-starter",
      "files": {
        "src/routes/users.ts": "// existing user routes (GET /users, GET /users/:id)",
        "src/models/user.ts": "interface User { id: string; name: string; email: string; avatar_url?: string; }"
      },
      "kb_results": ["knowledge/tooling/opencode/rest-api-patterns.md"]
    }
  },
  "expected_behavior": {
    "checklist": [
      "Plan includes route definition in src/routes/users.ts",
      "Plan includes validation logic for required name field",
      "Plan includes email format validation",
      "Plan marks avatar_url as optional",
      "Plan includes error handling for missing/invalid fields",
      "Plan does NOT suggest changes to unrelated files"
    ],
    "must_not_include": [
      "Suggestions to modify the database schema",
      "References to authentication (not in scope)"
    ]
  },
  "metadata": {
    "added": "2026-06-09",
    "author": "refactorartist",
    "tags": ["rest-api", "validation", "express"],
    "difficulty": "medium"
  }
}
```

**Directory layout:**

```
golden-dataset/
├── index.json              # Manifest of all cases
├── rs-architect/
│   ├── feature-planning.json
│   ├── error-recovery.json
│   └── ...
├── rs-developer/
│   ├── implementation.json
│   └── ...
├── rs-reviewer/
│   ├── code-review.json
│   └── ...
├── rs-spec-writer/
│   ├── spec-generation.json
│   └── ...
├── rs-test-writer/
│   ├── test-generation.json
│   └── ...
├── rs-tech-writer/
│   ├── documentation.json
│   └── ...
└── rs-devops/
    ├── deployment-plan.json
    └── ...
```

The `index.json` manifest tracks dataset version and provides fast lookup:

```json
{
  "version": "1.0.0",
  "total_cases": 42,
  "agents": {
    "rs-architect": { "cases": 8, "path": "rs-architect/" },
    "rs-developer": { "cases": 10, "path": "rs-developer/" },
    "rs-reviewer": { "cases": 6, "path": "rs-reviewer/" },
    "rs-spec-writer": { "cases": 5, "path": "rs-spec-writer/" },
    "rs-test-writer": { "cases": 5, "path": "rs-test-writer/" },
    "rs-tech-writer": { "cases": 4, "path": "rs-tech-writer/" },
    "rs-devops": { "cases": 4, "path": "rs-devops/" }
  },
  "last_updated": "2026-06-09"
}
```

### 2.4 Dataset Versioning

The golden dataset is versioned alongside the plugin. Dataset versions use semver independently of the plugin version:

- **Major**: Dataset restructuring (cases removed, format changes, scoring rubric changes)
- **Minor**: New cases added, existing cases updated
- **Patch**: Metadata corrections, typo fixes in expected behavior

```json
// In the plugin's package.json
{
  "runesmith": {
    "golden-dataset-version": "1.2.0"
  }
}
```

The dataset lives in a `golden-dataset/` directory at the repository root. It is included in the npm package but excluded from the init hook's file-copy logic (it is only used by the test runner, not deployed to consumers).

### 2.5 Review Process for New Cases

Adding a new golden dataset case follows a structured review process:

1. **Proposal** — Contributor drafts a new case as a PR against the golden dataset.
2. **Review** — At least one other contributor reviews the case for:
   - Representatives (is this a realistic scenario?)
   - Clarity (is the expected behavior checklist unambiguous?)
   - Coverage (does this case overlap with existing cases? Is there a gap it fills?)
   - Determinism (can the expected behavior be objectively verified?)
3. **Validation** — The case is run through the LLM judge against the current plugin version to establish a baseline score.
4. **Merge** — On approval, the case is merged. The dataset minor version is bumped.

**Emergency additions:** Cases derived from production bugs are added on a fast-track: proposed and reviewed within 24 hours of the bug being confirmed. These are added as patch bumps to the dataset version.

## 3. LLM Judge Pattern

The LLM judge evaluates agent outputs against the expected behavior checklist in each golden dataset case. It is the central quality measurement mechanism for non-deterministic agent behavior.

### 3.1 Judge Prompt Design

The judge prompt must be carefully crafted to produce consistent, objective evaluations. A poorly designed judge prompt produces noisy scores that cannot distinguish real regressions from judge variance.

**Core prompt structure:**

```
You are evaluating the output of an AI agent against a set of expected behaviors.
Evaluate each item on the checklist independently. For each item, output:

  PASS: <checklist item text>
  FAIL: <checklist item text>
  REASON: <one-sentence explanation>

Then output a summary:

  SUMMARY: <pass_count>/<total_count> passed
  SCORE: <percentage>

Additional rules:
- A PASS means the agent's output clearly satisfies the checklist item.
- A FAIL means the agent's output does NOT clearly satisfy the item.
- If the item is partially satisfied, it is a FAIL.
- If the item's applicability is unclear based on the output, it is a FAIL.
- Only the agent's output matters — do not consider the input or context.
- If the agent refused to produce output (e.g., "I cannot do that"), all checklist items FAIL.
```

**Scoring rubric:**

| Score Range | Meaning | Action |
|---|---|---|
| 100% | Perfect — all expected behaviors satisfied | No action needed |
| 95-99% | Near-perfect — minor deviation | Flag for review; human decides if regression |
| 80-94% | Acceptable — most behaviors satisfied | Review output; likely needs agent prompt improvement |
| < 80% | Failing — significant deviation | Block release; investigate root cause |

**Additional judge criteria (evaluated after checklist):**

```
After scoring the checklist, evaluate these quality dimensions on a 1-5 scale:

1. Coherence — Is the output well-structured and logically organized?
2. Conciseness — Is the output appropriately detailed (not overly verbose or terse)?
3. Actionability — Can the output be directly used (implemented from a plan, merged from a PR)?
4. Safety — Does the output avoid dangerous suggestions (rm -rf, privilege escalation, data loss)?

Format:

  DIMENSION: <name>
  SCORE: <1-5>
  REASON: <one-sentence explanation>
```

### 3.2 Judge Model Selection

| Model | Strengths | Weaknesses | Use Case |
|---|---|---|---|
| **Flash** (`opencode-go/deepseek-v4-flash`) | Fast (~2s per evaluation), cheap (< 1/10th the cost of Pro), good for bulk screening | Lower accuracy on nuanced tasks, more prone to false positives/negatives on borderline cases | CI merge gate: evaluate all golden dataset cases quickly |
| **Pro** (`opencode-go/deepseek-v4-pro`) | Higher accuracy on complex reasoning, better at detecting subtle deviations, more consistent scoring | Slow (~15s per eval), expensive (5-10x Flash cost) | Pre-release regression suite: final quality check before release |

**Tradeoff analysis:**

For the CI merge gate (which runs on every PR), speed and cost matter. Flash can evaluate 200 cases in ~7 minutes at manageable cost. Pro would take 50+ minutes at 5-10x the cost — not feasible for a per-PR gate.

For the pre-release regression suite (which runs once per release), accuracy matters more. Pro's higher accuracy catches regressions that Flash might miss. The slower speed is acceptable because the suite runs infrequently.

**Hybrid approach:**

```
Pre-PR:        Deterministic + Contract tests only (no LLM judge)
CI Merge Gate: Flash judge on golden dataset (fast screening)
Pre-Release:   Pro judge on golden dataset (thorough check)
```

If the Flash judge flags a borderline case (score 80-94%), that case is automatically re-evaluated by Pro in the CI merge gate. This catches Flash false positives without running Pro on every case.

**Concurrent median evaluation:** When the Pro judge runs 3 evaluations per case for median scoring (Section 3.3), the three calls execute concurrently as parallel API requests. Wall-clock time per case is therefore ~15s (the slowest of three parallel calls), not 45s. This keeps pre-release evaluation time manageable — see Section 4.3 for sharding strategies.

**Circular reasoning safeguard:** When plugin agents configure Pro as their model via `agent.md`, a Pro-based judge creates circular evaluation risk. Rules:

1. CI merge gate (Flash judge) avoids circularity by construction — Flash is always a different model from Pro.
2. Pre-release regression suite: at least one calibration run per quarter must use a judge from a different model family (e.g., Claude, GPT-5). If scores diverge from the Pro-based run by more than 5 points on case pass rate, investigate for circular reasoning bias.

This rule is cross-referenced in the Limitations table (Section 3.5).

### 3.3 Score Aggregation

For a given evaluation run (e.g., all 50 architect cases), scores are aggregated as follows:

| Metric | Calculation | Threshold |
|---|---|---|
| **Case pass rate** | Cases where every checklist item passed / total cases | >= 95% |
| **Checklist pass rate** | All checklist items passed / all checklist items evaluated | >= 97% |
| **Quality dimension avg** | Average of all quality dimension scores across all cases | >= 4.0 / 5.0 |

**Pass/fail decision:**

- If case pass rate >= 95% AND checklist pass rate >= 97% AND quality dimension avg >= 4.0 → **PASS**
- If any metric is below threshold → **FAIL** — evaluate individual failing cases to determine if regression

**Confidence intervals:**

Due to judge variability, a single evaluation run may not be reliable. For the pre-release regression suite, each case is evaluated 3 times by the Pro judge and the median score is used. This reduces variance from judge stochasticity.

```
Case score = median(score_run_1, score_run_2, score_run_3)
```

The three runs execute concurrently as parallel API calls, so wall-clock time per case is ~15s (the slowest of three parallel calls), not 45s. The 3x total token cost remains (affecting cost, not latency). Three runs significantly improve reliability compared to a single evaluation. For the CI merge gate (Flash), single evaluation is acceptable — the lower accuracy is compensated by the hybrid escalation to Pro for borderline cases.

### 3.4 Calibration

Periodic human review is essential to detect judge drift — the gradual degradation of judge accuracy as the plugin evolves and the judge prompt ages.

**Calibration cadence:** Once per month, or immediately after any agent prompt change.

**Calibration process:**

1. Select a random sample of 20 golden dataset cases (stratified across agents).
2. Run the current judge against these cases.
3. A human evaluator (a plugin maintainer) independently scores the same cases.
4. Compare judge scores vs. human scores.
5. If agreement rate (exact match on pass/fail per checklist item) < 90%, investigate and adjust the judge prompt.

**Calibration record:** Each calibration round is documented in the plugin repo:

```
calibration/2026-07-01.md:
  Judge model: deepseek-v4-pro
  Cases sampled: 20 (stratified)
  Agreement rate: 92%
  Drift detected: None
  Adjustments: None
```

**Drill-triggered calibration:** If a production bug is found that the golden dataset did not catch, immediately:
1. Add a test case for the bug scenario.
2. Run calibration on the affected agent's full case set.
3. Determine if judge drift was a contributing factor.

### 3.5 Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| **Judge bias** | The judge model may have preferences (e.g., prefers verbose output, penalizes certain phrasing) that skew scores | Use diverse checklist items focused on objective criteria rather than style preferences |
| **Circular reasoning** | If the judge uses the same underlying model as the agent, evaluations may be self-reinforcing | Use Flash for CI merge gate (avoids circularity when agents use Pro). When plugin agents specify Pro as their model, the pre-release judge must use a model from a different family (e.g., Claude, GPT-5) for at least one calibration run per quarter (see Section 3.2). |
| **Cost at scale** | Running 700+ cases through Pro for each release is expensive (~$5-10 per evaluation run) | Pro evaluation is pre-release only (not per-PR). Flash is used for CI gating. Total monthly cost target: < $50 |
| **Checklist completeness** | A perfect checklist score does not guarantee the agent produced a good output — only that it satisfied the listed criteria | Quality dimensions (coherence, conciseness, actionability, safety) provide secondary signal |
| **False sense of security** | High scores on the golden dataset do not guarantee the agent works well on unseen production inputs | Golden dataset must be regularly refreshed with cases derived from real production usage |

## 4. Testing Lifecycle

Different test types run at different points in the development lifecycle, balancing speed, coverage, and cost.

### 4.1 Pre-Commit / Pre-PR

**Phase:** Developer workstation (local hook or pre-PR script)

**Tests run:**
- Deterministic tests (all)
- Contract tests (all)

**Time budget:** < 2 minutes

**Gate:** Both must pass. The developer cannot commit or open a PR if either fails.

**Trigger:**
- Pre-commit: `bun test tests/deterministic/ tests/contract/`
- Pre-PR: same command, run as part of the PR creation workflow

**Rationale:** These tests are fast, deterministic, and catch structural bugs early. No LLM evaluation is involved, so no cost or latency concerns.

### 4.2 CI Merge Gate

**Phase:** CI pipeline (GitHub Actions) — runs on every PR push

**Tests run:**
- Deterministic tests (all) — rerun for isolation
- Contract tests (all) — rerun for isolation
- Golden dataset evaluation (Flash judge, single run) — all cases

**Time budget:** < 15 minutes

**Gate:** All deterministic and contract tests must pass. Golden dataset case pass rate must be >= 90% on Flash. If a case scores 80-94%, it is automatically escalated to Pro for re-evaluation.

**Trigger:** PR push to any branch that targets `main` (or equivalent default branch).

**Output:**
- Structured JSON report: `ci-artifacts/test-results-${{ github.sha }}.json`
- Summary comment on the PR with pass/fail breakdown per agent
- List of failing cases with judge reasoning for each

**Rationale:** The CI merge gate provides fast feedback on every PR. Flash evaluation keeps cost and latency manageable. Escalation to Pro for borderline cases catches false positives without running Pro on every case.

### 4.3 Pre-Release Regression Suite

**Phase:** Release workflow — runs before a new plugin version is published

**Tests run:**
- Deterministic tests (all)
- Contract tests (all)
- Golden dataset evaluation (Pro judge, 3x per case, median score)
- Adversarial tests (all)
- Integration tests (all)

**Time budget:** < 60 minutes (achieved via concurrent evaluation and parallel sharding)

The 3x median evaluations run concurrently as parallel API calls (Section 3.3), so per-case wall-clock is ~15s, not 45s. For datasets larger than ~200 cases, the golden dataset is split across parallel CI runners (shards). Example shard configurations:

| Dataset size | Shards | Cases per shard | Wall-clock per shard |
|---|---|---|---|
| 140 cases (Initial) | 1 | 140 | ~35 min |
| 350 cases (Growth) | 2 | 175 | ~44 min |
| 700 cases (Mature) | 4 | 175 | ~44 min |
| 1400 cases | 8 | 175 | ~44 min |

Shard count is configured in `release-regression.yml`. Each shard evaluates a disjoint subset. Results are merged by the workflow orchestrator into a single report.

**Gate:**
- Deterministic + contract: 100% pass
- Golden dataset: >= 95% case pass rate on Pro
- Adversarial: >= 80% pass (manually verified)
- Integration: 100% core, 90% secondary

**Trigger:** Manual dispatch of `release-regression` workflow (or automatically on release branch creation).

**Output:**
- Full structured JSON report
- Comparison with previous release's scores (delta report)
- Calibration recommendation if regression detected
- Human-review-required annotations for any failing adversarial or integration tests

**Rationale:** The pre-release suite is the most thorough quality gate. Pro evaluation with 3x median scoring maximizes accuracy. The full suite catches regressions that faster gates might miss. The 60-minute budget allows for thoroughness while keeping release latency manageable.

### 4.4 Post-Release Monitoring

**Phase:** Production — continuously after release

**Activity:** Telemetry analysis for anomaly detection

**Data collected:**
- Agent invocation success/failure rates
- Session latency percentiles (p50, p95, p99)
- Permission denial frequency
- Skill chain completion rates
- Unhandled error counts

**Anomaly detection triggers:**
- Agent failure rate increases by > 5% compared to pre-release baseline
- Session latency p95 exceeds 2x baseline for > 30 minutes
- Permission denial rate spikes by > 10x (may indicate broken permission logic)
- New error type appears (not seen in any pre-release test run)

**Response:** If an anomaly is detected, the plugin maintainer triages:
- If confirmed regression: fast-track a patch release
- If telemetry noise: document and adjust anomaly thresholds
- If data quality issue (missing telemetry): fix instrumentation

**Rationale:** Testing cannot cover every production scenario. Post-release monitoring catches issues that slip through — unusual input distributions, environment-specific failures, timing bugs. Telemetry data also feeds back into the golden dataset: production bugs become new test cases.

### 4.5 Lifecycle Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                     Development Lifecycle                        │
├──────────────┬────────────────┬────────────────┬─────────────────┤
│  Pre-Commit  │  CI Merge Gate │  Pre-Release   │  Post-Release   │
│  (local)     │  (per PR)      │  (per release)  │  (continuous)   │
├──────────────┼────────────────┼────────────────┼─────────────────┤
│ Deterministic│ Deterministic  │ Deterministic  │ Telemetry       │
│ + Contract   │ + Contract     │ + Contract     │ anomaly         │
│ (< 2 min)    │ + Golden       │ + Golden (Pro) │ detection       │
│              │   (Flash)      │ + Adversarial  │                 │
│              │ (< 15 min)     │ + Integration  │                 │
│              │                │ (< 60 min)     │                 │
└──────────────┴────────────────┴────────────────┴─────────────────┘
     ▲                  ▲                ▲                ▲
     │                  │                │                │
  Commit gate        PR merge         Release          Monitor
                     gate             gate
```

## 5. Test Infrastructure

### 5.1 Test Runner

**Primary:** `bun test` — fast, TypeScript-native, compatible with the plugin's existing build tooling.

**Why bun test:**
- Sub-100ms startup time (critical for pre-commit hooks where latency matters)
- Native TypeScript support (no ts-node or tsx required)
- Compatible with the plugin's existing build (the plugin is already TypeScript-based)
- Watch mode for development iteration

**Test file structure:**

```
tests/
├── deterministic/
│   ├── init-hook.test.ts
│   ├── permissions.test.ts
│   ├── version-stamp.test.ts
│   └── cli-commands.test.ts
├── contract/
│   ├── agent-frontmatter.test.ts
│   ├── skill-structure.test.ts
│   ├── permission-schema.test.ts
│   └── delegation-format.test.ts
├── golden/
│   ├── evaluate.ts              # LLM judge evaluator
│   ├── dataset-loader.ts        # Loads golden dataset cases
│   └── reporter.ts              # Generates structured JSON report
├── adversarial/
│   ├── pathological-inputs.test.ts
│   ├── permission-bypass.test.ts
│   └── resource-exhaustion.test.ts
├── integration/
│   ├── architect-developer-reviewer.test.ts
│   ├── skill-chain.test.ts
│   ├── gate-failure.test.ts
│   └── init-hook-recovery.test.ts
└── helpers/
    ├── mock-opencode-session.ts  # Simulates OpenCode session for integration tests
    ├── test-context.ts           # Shared test fixtures and context
    └── judge-client.ts           # Client for LLM judge API calls
```

### 5.2 Test Case Repository

Golden dataset cases are stored as versioned JSON files in the plugin repo:

```
golden-dataset/
├── index.json
├── rs-architect/
│   ├── 001-feature-planning.json
│   ├── 002-error-recovery.json
│   └── ...
├── ...
└── CHANGELOG.md                  # Tracks dataset changes across versions
```

The dataset is git-tracked alongside the plugin source code. Version bumps to the dataset are reflected in the plugin's `package.json` under `runesmith.golden-dataset-version`.

**Access in tests:** The `dataset-loader.ts` helper reads `golden-dataset/index.json` to discover all cases, then loads individual case files on demand.

### 5.3 CI Pipeline Integration

**GitHub Actions workflows:**

| Workflow | Trigger | Tests Run | Timeout |
|---|---|---|---|
| `pre-commit` | `pre-commit` hook (local) | Deterministic + Contract | 2 min |
| `ci-merge-gate` | PR push to `main` | Deterministic + Contract + Golden (Flash) | 15 min |
| `release-regression` | Manual dispatch / release branch | Full suite (Pro + adversarial + integration) | 60 min |
| `post-release` | Release published | Telemetry analysis (no test run) | N/A |

**Workflow structure (ci-merge-gate example):**

```yaml
name: CI Merge Gate
on: pull_request

jobs:
  deterministic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install
      - run: bun test tests/deterministic/ tests/contract/
      - uses: actions/upload-artifact@v4
        with:
          name: deterministic-results
          path: test-results.json

  golden-eval:
    runs-on: ubuntu-latest
    needs: deterministic
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install
      - run: bun run tests/golden/evaluate.ts --judge flash
      - uses: actions/upload-artifact@v4
        with:
          name: golden-results
          path: golden-results.json

  pr-comment:
    runs-on: ubuntu-latest
    needs: [deterministic, golden-eval]
    steps:
      - uses: actions/download-artifact@v4
      - run: bun run tests/helpers/pr-comment.ts
      - uses: actions/github-script@v7
        with:
          script: |
            // Post results summary as PR comment
```

### 5.4 Reporting Format

All test runs produce a structured JSON report. The format is consistent across test types:

```json
{
  "run_id": "ci-merge-gate-20260609-001",
  "timestamp": "2026-06-09T14:30:00Z",
  "workflow": "ci-merge-gate",
  "plugin_version": "1.0.0",
  "golden_dataset_version": "1.2.0",
  "judge_model": "opencode-go/deepseek-v4-flash",
  "results": {
    "deterministic": {
      "passed": 45,
      "failed": 0,
      "skipped": 0,
      "tests": [
        { "name": "initHookCopiesAgentsOnFreshInstall", "status": "passed", "duration_ms": 120 },
        { "name": "initHookSkipsCopyWhenVersionMatches", "status": "passed", "duration_ms": 95 }
      ]
    },
    "contract": {
      "passed": 28,
      "failed": 0,
      "skipped": 0,
      "tests": [
        { "name": "agentFrontmatterRequiredFields", "status": "passed", "duration_ms": 80 }
      ]
    },
    "golden": {
      "case_pass_rate": 96.0,
      "checklist_pass_rate": 98.2,
      "quality_dimension_avg": 4.3,
      "total_cases": 50,
      "passed_cases": 48,
      "failed_cases": 2,
      "cases": [
        {
          "id": "rs-architect-001",
          "status": "passed",
          "checklist_score": 6/6,
          "quality_dimensions": { "coherence": 5, "conciseness": 4, "actionability": 5, "safety": 5 },
          "judge_reasoning": "..."
        },
        {
          "id": "rs-developer-003",
          "status": "failed",
          "checklist_score": 3/5,
          "quality_dimensions": { "coherence": 3, "conciseness": 3, "actionability": 2, "safety": 5 },
          "judge_reasoning": "Implementation did not include error handling for missing fields (checklist item #4). Output structure was somewhat disorganized."
        }
      ]
    },
    "adversarial": {
      "passed": 16,
      "failed": 4,
      "manually_verified": true,
      "tests": []
    },
    "integration": {
      "passed": 8,
      "failed": 0,
      "skipped": 1,
      "tests": []
    }
  },
  "summary": {
    "overall_status": "pass",
    "total_tests": 97,
    "passed": 93,
    "failed": 2,
    "skipped": 1,
    "human_review_required": true
  }
}
```

Reports are uploaded as CI artifacts and archived for 90 days. The release-regression workflow also generates a delta report comparing against the previous release's scores:

```json
{
  "delta": {
    "case_pass_rate": { "previous": 97.0, "current": 96.0, "change": -1.0 },
    "checklist_pass_rate": { "previous": 99.0, "current": 98.2, "change": -0.8 },
    "quality_dimension_avg": { "previous": 4.4, "current": 4.3, "change": -0.1 },
    "regressed_cases": ["rs-developer-003"]
  }
}
```

### 5.5 Golden Dataset Storage

The golden dataset is stored in the plugin repository under `golden-dataset/`. It is:

- **Git-tracked** — all changes are version-controlled
- **Included in the npm package** — the test runner reads from the installed package (or from the local checkout during development)
- **Excluded from init hook copy** — the golden dataset is test infrastructure, not runtime configuration. The init hook copies agent/skill files into `.opencode/` but does not copy the golden dataset.

**Storage format:** JSON files, one per test case. This is preferable to YAML for the golden dataset because:
- JSON is more strictly typed (fewer parsing ambiguities)
- The dataset is machine-read (not typically hand-edited by non-developers)
- JSON supports nested structures (checklist arrays, quality dimension objects) naturally

YAML may be used for the `index.json` manifest if readability for manual inspection is preferred, but JSON consistency across all files is simpler.

## 6. Relationship to Existing Verification

The [verification.md](./verification.md) document defines a manual smoke test checklist for pre-release validation. This testing methodology research defines the automated versions of those checks. The two documents coexist and complement each other.

### 6.1 Mapping Verification Checks to Automated Tests

| Verification Section | Manual Check | Automated Test Type | Notes |
|---|---|---|---|
| Plugin Installation | Add plugin entry, verify npm cache, check auth | Deterministic + Contract | Auth and npm resolution are partially deterministic; manifest checks are contract tests |
| Init Hook | Verify file copy, version stamp, re-copy on update | Deterministic | Core init hook logic is fully deterministic — no LLM needed |
| Agent @mention | Invoke each agent, verify prompt loads, check permissions | Contract + Golden | Permission schema is contract; agent output quality is golden eval |
| Skills | Load each skill, verify instructions, check chaining | Deterministic + Integration | Skill loading is deterministic; chaining success is integration test |
| KB Discovery | Search KB, resolve cross-references, trace pipeline | Integration | End-to-end KB search and resolution requires simulated OpenCode session |
| Permissions | Deny/allow/ask per agent, leaf agent task denial | Deterministic + Adversarial | Permission enforcement is deterministic; bypass attempts are adversarial |
| Update Propagation | CLI update, version detection, re-copy, stamp update | Deterministic | CLI commands and init hook stamp comparison are deterministic |

### 6.2 Coexistence: Manual + Automated

The two approaches serve different purposes:

| Dimension | Manual Verification | Automated Testing |
|---|---|---|
| **Purpose** | Exploratory testing — find unexpected behaviors | Regression testing — prevent known failures from recurring |
| **Execution** | Human follows checklist, observes and interprets | Machine runs tests, compares against expected outputs |
| **Coverage** | Broad, shallow — exercises the whole system | Narrow, deep — exercises specific paths exhaustively |
| **Cost** | High per-run (human time) | Low per-run (compute) |
| **Detects** | UX issues, unexpected interactions, subtle permission leaks | Structural bugs, schema violations, score regressions |
| **Frequency** | Per-release | Pre-commit, per-PR, per-release |

**When to use each:**

- **Use manual verification** during early development (pre-alpha, alpha) where the feature set is unstable and automated tests would require constant updates. Also use it for pre-release exploratory testing — humans find things automated tests miss.
- **Use automated testing** once a feature is stable. Every bug found in production should result in a new automated test case (see [Section 2.5](#25-review-process-for-new-cases)).

**Workflow:**

```
Development → bugs found → bugs fixed → test cases added → regression prevented
                                                                    ↓
Manual verification catches novel issues → new automated tests added
```

### 6.3 Phase-Specific Testing Recommendations

Per the [rollout-strategy.md](./rollout-strategy.md) phased approach:

| Phase | Testing Focus | Primary Test Types |
|---|---|---|
| Phase 1 (Pilot) | Init hook correctness, core agent loop, permission enforcement | Deterministic + Contract + Manual verification |
| Phase 2 (Team) | Skill chaining, multi-agent pipelines, KB discovery | All types, Flash judge on golden dataset |
| Phase 3 (Org) | Full regression suite, production telemetry, all agents and skills | Full suite, Pro judge, post-release monitoring |

Phase 1 may skip the golden dataset entirely and rely on manual verification per [verification.md](./verification.md). The golden dataset is introduced in Phase 2 as the agent suite expands and regression risk increases. The full regression suite with Pro judge is reserved for Phase 3 when the plugin is org-wide infrastructure.

## 7. Related Research

| Document | Relationship |
|---|---|
| [verification.md](./verification.md) | Manual smoke test checklist — this research defines the automated counterparts |
| [rollout-strategy.md](./rollout-strategy.md) | Phase-specific testing recommendations — testing maturity grows with rollout phases |
| [permission-profiles.md](./permission-profiles.md) | Permission schema that deterministic and adversarial tests exercise |
| [update-propagation.md](./update-propagation.md) | Version-stamping logic that deterministic tests validate |
| [init-hook.md](../architecture/init-hook.md) | Init hook file copy logic that deterministic tests cover |
| [cost-observability.md](./cost-observability.md) | Judge cost tracking and budget management for LLM evaluations |

## 8. Conclusion

The RuneSmith testing methodology provides a structured, multi-layered approach to quality assurance for an LLM-powered plugin. Five test types — deterministic, contract, golden dataset, adversarial, and integration — plus the composite Regression Suite, each address a different quality concern, from structural correctness to semantic output quality.

Key design decisions:

1. **Separation of deterministic and LLM-dependent tests** — deterministic tests run on every commit (fast, cheap), while golden dataset evaluation with an LLM judge runs only at key checkpoints (CI merge gate, pre-release).

2. **The golden dataset as the primary quality mechanism** — curated test cases with expected-behavior checklists provide an objective, repeatable way to measure agent output quality. The dataset grows with the plugin, capturing each production bug as a regression test.

3. **Flash + Pro hybrid judge** — Flash for fast CI screening, Pro for thorough pre-release validation, with automatic escalation for borderline cases. This balances cost, speed, and accuracy.

4. **Testing lifecycle aligned with risk** — faster, cheaper tests run earlier and more frequently; slower, more expensive tests run only at release boundaries. Post-release monitoring catches what testing misses.

5. **Manual and automated testing coexist** — [verification.md](./verification.md) provides exploratory manual checks; this research provides automated regression coverage. Both are necessary for a plugin where LLM behavior cannot be fully specified in advance.

The methodology matures alongside the plugin rollout phases: Phase 1 relies on deterministic tests and manual verification, Phase 2 adds the golden dataset and Flash judge, and Phase 3 introduces the full regression suite with Pro evaluation and post-release monitoring.
