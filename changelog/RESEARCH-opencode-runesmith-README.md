# OpenCode RuneSmith Plugin — Research

Analysis of implementation approaches for the `@runicengines/opencode-runesmith` plugin — an internal OpenCode plugin bundling role-based agents, reusable skills, and MCP servers for the RunicEngines cooperative.

## Files

### Architecture

| File | Description |
|---|---|---|
| [distribution-comparison.md](architecture/distribution-comparison.md) | npm plugin vs global vs submodule — comparison and recommendation |
| [distribution-questions-resolved.md](architecture/distribution-questions-resolved.md) | Resolves 5 open distribution questions — versioning, backward compat, release automation, multi-version coexistence, offline dev |
| [init-hook.md](architecture/init-hook.md) | Plugin init lifecycle — file copying, version-stamping, error handling |
| [mcp-registration.md](architecture/mcp-registration.md) | MCP server bundling approaches |
| [package-structure.md](architecture/package-structure.md) | Directory layout, package.json, naming conventions, consumer setup |
| [security-supply-chain.md](architecture/security-supply-chain.md) | Supply chain security analysis for the plugin's npm dependencies, GitHub Packages trust model, SBOM considerations |

### Agents

| File | Description |
|---|---|---|
| [spec-writer.md](agents/spec-writer.md) | Issue → plan conversion agent |
| [architect.md](agents/architect.md) | Hub orchestrator — role, permissions, model |
| [architect-orchestration.md](agents/architect-orchestration.md) | Delegation flow, phase gates, error recovery |
| [developer.md](agents/developer.md) | Code implementation agent |
| [reviewer.md](agents/reviewer.md) | Code review agent (read-only) |
| [test-writer.md](agents/test-writer.md) | Test writing and execution agent |
| [tech-writer.md](agents/tech-writer.md) | Documentation agent |
| [devops.md](agents/devops.md) | CI/CD and infrastructure agent |
| [rs-debugger.md](agents/rs-debugger.md) | Debugging agent — reproduce, analyse, report (read-only) |

### Skills — Workflows

| File | Description |
|---|---|
| [issue-to-plan.md](skills/workflows/issue-to-plan.md) | Decompose GitHub issues into implementation plans |
| [pr-packager.md](skills/workflows/pr-packager.md) | Generate PR descriptions from commits (ADR 0002) |
| [changelog-manager.md](skills/workflows/changelog-manager.md) | Maintain CHANGELOG.md (keepachangelog.com 2.0.0) |
| [rs-doc-architect.md](skills/workflows/rs-doc-architect.md) | Diataxis-based documentation audit and restructuring plan |
| [rs-commit-writer.md](skills/workflows/rs-commit-writer.md) | Generate Conventional Commit messages from staged diff |
| [rs-pr-writer.md](skills/workflows/rs-pr-writer.md) | Generate PR body from issue/spec (forward workflow) |
| [test-helper-run.md](skills/workflows/test-helper-run.md) | Run test suites and collect results |
| [test-helper-diagnose.md](skills/workflows/test-helper-diagnose.md) | Interpret failures and suggest fixes |

### Skills — Reviews

| File | Description |
|---|---|
| [review-methodology.md](skills/reviews/review-methodology.md) | Structured review process (ADR 0002 §5) |
| [review-severity.md](skills/reviews/review-severity.md) | Severity classification (S1–S5) |
| [review-security.md](skills/reviews/review-security.md) | Security-specific review patterns |
| [rs-doc-auditor.md](skills/reviews/rs-doc-auditor.md) | Documentation compliance auditor (Diataxis, structure, content) |

### Skills — Utilities

| File | Description |
|---|---|
| [rs-discover.md](skills/utilities/rs-discover.md) | Codebase scanning and context mapping |
| [rs-consult.md](skills/utilities/rs-consult.md) | SME consultation pattern |
| [rs-scratchpad.md](skills/utilities/rs-scratchpad.md) | Session scratchpad lifecycle (init, clear, status) |
| [rs-doc-llm-txt.md](skills/utilities/rs-doc-llm-txt.md) | Generate llms.txt per llmstxt.org spec |
| [rs-env-validator.md](skills/utilities/rs-env-validator.md) | Validate .env files against .env.example |
| [dependency-checker.md](skills/utilities/dependency-checker.md) | Vulnerability and outdated dependency scanning |

### KB Discovery

| File | Description |
|---|---|
| [discovery-mechanism.md](kb-discovery/discovery-mechanism.md) | Locate the Knowledge Base from any code repo |
| [search-patterns.md](kb-discovery/search-patterns.md) | Full-text search, cross-reference, pipeline tracing |

### Operations

| File | Description |
|---|---|---|
| [agent-skills-mapping.md](operations/agent-skills-mapping.md) | Which agents call which skills |
| [cost-observability.md](operations/cost-observability.md) | API cost projections, token budgets, logging/tracing, monitoring, debugging pipeline failures |
| [maintenance-governance.md](operations/maintenance-governance.md) | Maintainer model, contribution process, deprecation policy, release cadence, changelog conventions |
| [open-questions-resolved.md](operations/open-questions-resolved.md) | All decisions captured |
| [permission-profiles.md](operations/permission-profiles.md) | Full YAML comparison across all agents |
| [rollout-strategy.md](operations/rollout-strategy.md) | Three-phase rollout plan (pilot → team → org-wide) with success metrics, rollback criteria, feature gating |
| [testing-agent-behavior.md](operations/testing-agent-behavior.md) | Per-agent behavioral evaluation using golden datasets, adversarial testing, and LLM judge |
| [testing-agent-pipeline.md](operations/testing-agent-pipeline.md) | End-to-end integration tests for multi-agent pipeline, skill chains, gate failures |
| [testing-init-hook.md](operations/testing-init-hook.md) | Deterministic unit and property-based tests for init hook and version-stamping |
| [testing-methodology.md](operations/testing-methodology.md) | Overall testing framework: golden dataset design, LLM judge, evaluation lifecycle |
| [update-propagation.md](operations/update-propagation.md) | Version-stamping and cache management |
| [verification.md](operations/verification.md) | Smoke test checklist |

## References

- [GitHub Issue #19](https://github.com/RunicEngines/knowledge-base/issues/19) — Research ticket
- [Idea: Org-Wide Agent Plugin](../../ideas/organisation/tools/org-wide-agent-plugin/) — Originating idea
- [ADR 0005: KB Agents and Skills](../../adr/0005-knowledge-base-agents-and-skills/) — Related architecture decision
- [opencode-swarm](https://github.com/zaxbysauce/opencode-swarm) — Reference implementation for multi-agent patterns
