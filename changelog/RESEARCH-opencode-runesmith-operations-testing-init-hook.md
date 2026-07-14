---
title: "RuneSmith Init Hook Testing"
status: exploring
author: "refactorartist (Khalid Zubair)"
date: 2026-06-09
tags:
  - opencode
  - runesmith
  - testing
  - init-hook
sources:
  - knowledge: "knowledge/tooling/opencode/plugins/init-hook-lifecycle.md"
  - knowledge: "knowledge/tooling/opencode/plugins/bundling-components.md"
references:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-09
---

# RuneSmith Init Hook Testing

## Init Hook Test Surface

The RuneSmith plugin's init hook (as designed in [init-hook.md](../../architecture/init-hook.md)) currently performs file copying, version-stamping, and basic error handling. This test plan covers both current operations and proposed extensions. Operations marked as **(proposed)** are test scenarios for features not yet implemented in the init hook — they follow a TDD approach where tests are written first to drive future implementation.

| Operation | Description | Test Priority |
|---|---|---|
| File copying | Copy bundled agents to `.opencode/agents/` and skills to `.opencode/skills/` | Critical |
| Version-stamping | Read `package.json`, compare against existing stamp file, decide copy/no-copy | Critical |
| Deprecation warnings **(proposed)** | Log stderr warnings for agents or skills marked as deprecated in the bundle | High |
| Phase-aware copying **(proposed)** | Gate file copying based on rollout phase (Level 2 in rollout-strategy.md) | High |
| Error handling | Recover gracefully from missing sources, permission errors, disk-full scenarios | Critical |
| Cleanup on rollback **(proposed)** | Remove files copied during a failed or reverted init | Medium |

### Key Design Decisions

- The init hook MUST be idempotent: running it multiple times with the same version stamp produces identical state.
- The init hook MUST NOT delete files it did not create. Only RuneSmith-prefixed files (e.g., `rs-*.md`, `rs-*/`) are eligible for cleanup.
- Version comparison uses strict string equality (`currentVersion === pluginVersion`) after regex validation (`/^\d+\.\d+\.\d+$/`). There is no `semver.gt`/`semver.lt` differentiation — any mismatch triggers a full re-copy regardless of direction (upgrade or downgrade). See the [Downgrade](#downgrade--stamp-higher) section below for a discussion of whether richer semver comparison should be added in a future iteration.

## Test Case Design

### Fresh Install — No Stamp Exists

| Step | Expected Outcome |
|---|---|
| Clear `.opencode/agents/` and `.opencode/skills/` | Directories may be empty or absent |
| Remove any existing `.opencode/.runesmith-version` | Stamp file does not exist |
| Run init hook | All bundled agents copied to `.opencode/agents/` |
| | All bundled skills copied to `.opencode/skills/` |
| | `.opencode/.runesmith-version` created with current package version |

### Same Version — Stamp Matches

| Step | Expected Outcome |
|---|---|
| Set `.opencode/.runesmith-version` to current package version | Stamp matches |
| Run init hook | No files copied |
| | No warnings or errors emitted |
| | Stamp file unchanged |

### Upgrade — Stamp Lower

| Step | Expected Outcome |
|---|---|
| Set `.opencode/.runesmith-version` to `0.1.0` (package is `0.2.0`) | Stamp is lower |
| Run init hook | New/changed agent files copied to `.opencode/agents/` |
| | New/changed skill directories copied to `.opencode/skills/` |
| | Stamp updated to `0.2.0` |
| | Deprecation warnings logged for any deprecated agents/skills in the new version |

### Downgrade — Stamp Higher

**Note:** The current init-hook.md design does not distinguish downgrades from upgrades — any version mismatch triggers a full re-copy. The three options below are **proposed** extensions for a richer semver comparison that treats downgrades differently from upgrades.

| Option | Behaviour | Selected |
|---|---|---|
| Reject | Abort init, log error, leave stamp unchanged | No — prevents testing older versions |
| Copy down | Overwrite with bundled (older) files, update stamp | Yes — allows rollback for debugging |
| Warn and copy down | Log warning, then proceed with Copy down | **Default** — safe but flexible |

| Step | Expected Outcome |
|---|---|
| Set `.opencode/.runesmith-version` to `0.3.0` (package is `0.2.0`) | Stamp is higher |
| Run init hook | Warning logged: "Installed version (0.3.0) is newer than bundle (0.2.0). Downgrading." **(proposed — current init-hook.md does not distinguish downgrade from upgrade)** |
| | Files overwritten with bundled versions |
| | Stamp updated to `0.2.0` |

### Missing Source — Agent .md Not Found in Plugin

**Note:** The current init-hook.md only checks directory-level existence (`if (!existsSync(agentsDir))`), not individual files. Per-file missing-source warnings (below) are **proposed** behavior.

| Step | Expected Outcome |
|---|---|
| Remove one agent `.md` from the plugin bundle | Source file missing |
| Run init hook | Warning logged: "Agent `rs-missing.md` not found in bundle. Skipping." **(proposed — current init-hook.md checks only directory-level existence)** |
| | Init continues — remaining agents copied |
| | Non-zero exit code NOT required (warning is sufficient) |

### Permission Error — Cannot Write to `.opencode/`

| Step | Expected Outcome |
|---|---|
| Set `.opencode/` directory permissions to read-only | Cannot write |
| Run init hook | Error logged: "Failed to write `/path/to/.opencode/agents/rs-architect.md`: EACCES" |
| | Init aborts with non-zero exit code |
| | No partial files left in `.opencode/agents/` or `.opencode/skills/` **(proposed — init-hook.md has no rollback/cleanup; partially copied files may remain)** |
| | Stamp file NOT updated |

### Disk Full

| Step | Expected Outcome |
|---|---|
| Simulate `ENOSPC` error on write | Disk full |
| Run init hook | Error logged with disk-full message |
| | Init aborts with non-zero exit code |
| | Rollback removes any partially copied files **(proposed — init-hook.md has no rollback logic; partially copied files may remain)** |

### Phase Gating — Phase 1 Config

| Step | Expected Outcome |
|---|---|
| Set `opencode.json` plugin config to `{ "phase": 1 }` | Phase 1 active |
| Run init hook | Only Phase 1 agents and skills copied |
| | Phase 2+ agents and skills skipped (with debug log if verbose) |
| | Stamp file written normally |

### Deprecation Warning

| Step | Expected Outcome |
|---|---|
| Include an agent with `deprecated: true` in frontmatter | Deprecated agent in bundle |
| Run init hook (upgrade scenario) | Warning logged: "Agent `rs-old-agent.md` is deprecated. Consider migrating to `rs-new-agent.md`." |
| | Deprecated agent still copied (backward compat) |

## Property-Based Testing

Property-based tests (PBT) verify invariant properties across a wide range of randomly generated inputs. For the init hook, the following properties MUST hold.

### P1: All Agent Files Are Valid Markdown with Required Frontmatter

```
∀ f ∈ .opencode/agents/ after init:
  f is valid .md
  AND f has frontmatter with title, status, author, date, tags
  AND f frontmatter conforms to agent schema
```

Randomly vary: bundle contents, stamp versions, file system states.

### P2: All Skill Directories Contain SKILL.md

```
∀ d ∈ .opencode/skills/ after init:
  ∃ d/SKILL.md
  AND d/SKILL.md has frontmatter with name, description, tools
```

Randomly vary: skill directory structure, missing SKILL.md in bundle.

### P3: Version Stamp Is Valid Semver

```
After init:
  .opencode/.runesmith-version exists
  AND content matches semver 2.0.0
  AND content === bundle package.json version
```

Randomly vary: corrupted stamp files, non-semver stamps, missing stamps.

### P4: Stamp Unchanged → Agent Files Identical

```
If stamp === previous stamp before init:
  ∀ f ∈ .opencode/agents/: content(f) after init === content(f) before init
  ∀ d ∈ .opencode/skills/: content(d) after init === content(d) before init
```

### P5: No Orphaned RuneSmith Files

```
∀ f ∈ .opencode/agents/ after init:
  f is in bundle manifest
  OR f is not rs-* prefixed

∀ d ∈ .opencode/skills/ after init:
  d is in bundle manifest
  OR d is not rs-* prefixed
```

This prevents stale agents/skills from accumulating after downgrades or partial upgrades.

## Test Fixtures

### Mock Plugin Package Directory

```
test/fixtures/plugin-package/
├── package.json          # { "name": "@runicengines/opencode-runesmith", "version": "0.2.0" }
├── agents/
│   ├── rs-architect.md
│   ├── rs-developer.md
│   ├── rs-reviewer.md
│   └── rs-old-agent.md   # deprecated: true
└── skills/
    ├── rs-discover/
    │   └── SKILL.md
    └── rs-issue-to-plan/
        └── SKILL.md
```

### Mock Project `.opencode/` Directory

```
test/fixtures/project-opencode/
├── agents/               # may be empty or contain pre-existing agents
├── skills/               # may be empty or contain pre-existing skills
└── .runesmith-version    # optional, seeded per test
```

### Version Stamp Files

| Fixture | Content | Purpose |
|---|---|---|
| `stamp-absent` | (no file) | Fresh install |
| `stamp-current` | `0.2.0` | Same version |
| `stamp-old` | `0.1.0` | Upgrade |
| `stamp-new` | `0.3.0` | Downgrade |
| `stamp-invalid` | `not-semver` | Corrupted stamp |
| `stamp-empty` | `` | Empty file |

### Corrupted/Missing Scenarios

| Fixture | Description |
|---|---|
| `agents/rs-architect.md` deleted from bundle | Missing source |
| `skills/rs-discover/` missing `SKILL.md` | Missing skill definition |
| `.opencode/` set to read-only | Permission error |
| `.opencode/` disk quota exhausted | Disk full (simulated via mock) |

## Test Automation

### Test Runner

Use **vitest** with the following configuration:

- `@vitest/runner` for test orchestration
- `vitest --reporter verbose` for CI output
- `vitest --coverage` for coverage reporting (via `@vitest/coverage-v8`)

Rationale: vitest is compatible with both Bun and Node.js runtimes, has first-class TypeScript support, and integrates with the existing toolchain.

### Mocking Strategy

File system operations MUST be mocked to avoid touching real disk and to enable error simulation.

| Approach | Tool | Why |
|---|---|---|
| Virtual FS | `memfs` (via `unionfs` + `fs-monkey`) | Full in-memory filesystem, no real I/O |
| Error injection | Custom mock layer on top of `memfs` | Simulate EACCES, ENOSPC, ENOENT |
| Package.json stub | `vi.mock('fs', ...)` at module scope | Redirect all reads to fixture data |

The mock layer should expose a `triggerError(path, errorCode)` helper to inject filesystem errors at specific paths during a test run.

### Test File Structure

```
src/__tests__/
├── init-hook/
│   ├── fresh-install.test.ts
│   ├── same-version.test.ts
│   ├── upgrade.test.ts
│   ├── downgrade.test.ts
│   ├── missing-source.test.ts
│   ├── permission-error.test.ts
│   ├── disk-full.test.ts
│   ├── phase-gating.test.ts
│   └── deprecation.test.ts
├── init-hook-properties.test.ts   # property-based tests
└── fixtures/
    ├── plugin-package/
    ├── project-opencode/
    └── stamp-fixtures/
```

### Property-Based Testing Library

Use **fast-check** (`@fast-check/vitest`) for property-based tests. Each property (P1–P5 above) becomes a `fc.property` test that generates random inputs from its parameter space.

```
import { test, fc } from '@fast-check/vitest';

test.prop([fc.string(), fc.option(fc.semver(), { nil: undefined })])
  ('P3: Version stamp is valid semver', (bundlePath, stampVersion) => {
    // setup: create fixture from generated inputs
    // run: init hook
    // assert: stamp is semver
  });
```

### CI Integration

| Trigger | Action |
|---|---|
| Every PR against `main` | `bun run test -- --coverage` |
| Every push to `main` | Same as PR |
| Nightly (optional) | Extended property-based test run (10x iterations) |

### Coverage Targets

| Metric | Target | Notes |
|---|---|---|
| Line coverage | >= 90% | Measured for init hook source files only |
| Branch coverage | >= 85% | All if/else branches in init hook logic |
| Function coverage | >= 95% | Every exported and internal function |
| Property coverage | 5 properties | P1–P5 must be implemented in PBT suite |

Coverage exclusions:
- Type definitions and interfaces
- Error type declarations
- Test fixture files and mocks themselves

## Dependencies on Existing Research

This testing strategy builds upon:

- **init-hook.md** (`research/opencode-runesmith/architecture/init-hook.md`) — the init hook implementation design that specifies what the hook does. Tests must verify every operation documented there.
- **verification.md** (`research/opencode-runesmith/operations/verification.md`) — the high-level verification checklist. Unit tests provide the automated verification layer; the checklist becomes the integration and manual testing layer.
- **rollout-strategy.md** (`research/opencode-runesmith/operations/rollout-strategy.md`) — phase definitions that determine which agents/skills get copied at each phase. Phase-gating tests must match the phase definitions exactly.

## Recommendations

1. **Implement tests before the init hook** (TDD approach) — write the test cases first, then implement the init hook to make them pass. This ensures all operations are testable from the start.
2. **Use `memfs` for all filesystem tests** — never touch real disk in unit tests. This keeps tests fast (< 100ms per test file) and deterministic.
3. **Run property-based tests with reduced iterations in CI** (100 iterations per property) and extended iterations nightly (10,000 iterations) to catch edge cases without slowing CI.
4. **Add a `dryRun: true` option to the init hook** — when enabled, the hook logs what it would do without making changes. Useful for debugging and for integration tests that validate the decision logic without executing file operations.
5. **Pin the fast-check version** in package.json to avoid upstream changes breaking the property-based test suite.
