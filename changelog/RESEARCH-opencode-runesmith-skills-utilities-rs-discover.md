---
title: "Discover Skill Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - skills
  - discover
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/overview.md"
  - knowledge: "knowledge/tooling/opencode/skills/discovery-patterns.md"
references:
  - url: "https://opencode.ai/docs/skills"
    title: "OpenCode Skills Documentation"
last_audit_date: 2026-06-07
---

# Discover Skill Design (`rs-discover`)

## Overview

`rs-discover` is a read-only utility skill within the `@runicengines/opencode-runesmith` plugin. Its sole responsibility is to scan an unfamiliar codebase and produce a structured context map that any agent can consume at the start of a session. The `rs-` prefix follows the plugin's convention for all runesmith-owned skills, distinguishing them from first-party OpenCode skills and skills defined in other plugins.

The skill is triggered automatically at the beginning of any agent session that needs codebase context — architect, developer, spec-writer, or otherwise. It is the entry point that turns an unknown repository into a shared mental model, eliminating the need for each agent to duplicate discovery work.

## Skill Purpose

A codebase is a living artifact. By the time a developer or agent opens it, months or years of structural decisions, framework choices, and configuration conventions are already embedded. Manually probing directories, guessing the build system, or hunting for entry points is wasteful when repeated across multiple agents. `rs-discover` solves this by codifying the discovery process into a reproducible, structured scan.

The output is a **context report** — a concise summary of what the project is, how it is structured, what it depends on, how to build and test it, and how it is deployed. This report serves as the shared context that all downstream agents (architect, developer, reviewer, spec-writer) reference rather than re-discovering.

Key characteristics:

- **Read-only**: The skill never edits, writes, or modifies any file in the codebase. It only reads.
- **Deterministic**: Given the same codebase, the same context report is produced (modulo file modifications over time).
- **Session-scoped**: The report is cached for the duration of the agent session so repeated calls do not re-scan.
- **Agent-agnostic**: Architect, developer, spec-writer — all agents invoke the same skill.

## Skill Instructions

### Trigger Conditions

Invoke `rs-discover` when:
- An agent session starts on a repository the agent has not seen before.
- The agent explicitly requests a fresh context refresh.
- An agent detects that structural context is missing or stale.

### Steps

1. **Read root-level manifests** — Inspect `README.md`, `package.json`, `pyproject.toml`, `Cargo.toml`, `Gemfile`, `go.mod`, `composer.json`, `CMakeLists.txt`, `Makefile`, or any equivalent file at the repository root. Extract project name, description, language runtime, and version constraints.

2. **Identify project type and framework** — From the manifests and directory layout, determine whether this is a web application, CLI tool, library, monorepo, or polyglot project. Identify the primary framework (Next.js, FastAPI, Rails, Spring, Actix, etc.) and note any secondary frameworks for sub-projects.

3. **Map directory structure** — Walk the top two levels of the directory tree. Identify the locations of:
   - Source code (`src/`, `lib/`, `app/`, `packages/`)
   - Tests (`tests/`, `spec/`, `__tests__/`, `*.test.ts`, `*.spec.py`)
   - Documentation (`docs/`, `wiki/`, `*.md`)
   - Configuration files (`.env*`, `*.config.*`, `tsconfig.json`, `.babelrc`, `.eslintrc.*`)
   - CI/CD pipelines (`.github/`, `.gitlab-ci.yml`, `Jenkinsfile`)
   - Infrastructure (Dockerfile, `docker-compose.yml`, `terraform/`, `k8s/`)

4. **Identify entry points** — Locate the primary runtime entry points:
   - Application servers (`main.py`, `index.ts`, `app.py`, `server.js`)
   - CLI entry points (`cli.py`, `bin/`, `cmd/`, entry in `package.json` `bin` field)
   - Worker or background job entry points

5. **List key dependencies** — Extract runtime and development dependencies from the appropriate manifest file. Note the runtime version (Node 18+, Python 3.11+, etc.) and any pinned platform requirements.

6. **Note custom or unusual configurations** — Flag anything non-standard:
   - Custom build tooling or task runners
   - Unusual project structure (e.g., flat source, generated code)
   - Monorepo tooling (Turborepo, Nx, Lerna, Bazel)
   - Feature flags or environment gating
   - Vendor directories or pinned dependencies

7. **Output structured context report** — Produce a report following the format below. Write it to the agent's context (ephemeral, session-scoped) so downstream agents can reference it without re-scanning.

### Output Format: Context Report

```yaml
project:
  name: "project-name"
  type: "web-app | cli-tool | library | monorepo | polyglot"
  runtime:
    language: "python | node | rust | go | ..."
    version: ">=3.11"
  framework:
    primary: "FastAPI"
    secondary: []
structure:
  source: "src/"
  tests: "tests/"
  docs: "docs/"
  configs:
    - ".env.example"
    - "tsconfig.json"
  ci: ".github/workflows/"
  infra:
    - "Dockerfile"
    - "docker-compose.yml"
entry_points:
  app: "src/main.py"
  cli: ""
  worker: "src/worker.py"
dependencies:
  runtime:
    - name: "fastapi"
      version: "^0.104.0"
  dev:
    - name: "pytest"
      version: "^7.4.0"
build:
  system: "poetry | npm | cargo | ..."
  commands:
    build: "npm run build"
    test: "npm test"
    run: "npm start"
deployment:
  platform: "docker | vercel | aws-ecs | ..."
  config: "Dockerfile + docker-compose.yml"
anomalies: []
```

### When NOT to Use

- The agent already has a valid context report from the current session (session-scoped cache hit).
- The agent is already familiar with the codebase and does not require a fresh scan.
- The task is purely textual or conceptual with no codebase interaction.

## Permission Requirements

`rs-discover` operates with minimal, read-only permissions:

| Permission | Required | Purpose |
|---|---|---|
| `read` | Yes | Read manifest files, configs, and source structure |
| `glob` | Yes | Pattern-match against source, test, and config directories |
| `grep` | Yes | Search for entry-point patterns and framework signatures |
| `bash` | No (optional) | Run detection commands (e.g., `node --version`, `python --version`) if manifests lack version info |
| `edit` | No | Never modifies files |
| `write` | No | Never creates files |

The skill explicitly **denies** `edit` and `write` permissions. It is purely observational.

## Design Rationale

### Why a Separate Skill Rather Than Inline Agent Instructions

Discovery is a cross-cutting concern. Every agent needs it, but no single agent should own it. By isolating discovery in a dedicated skill, we achieve:

- **Single source of truth** — The context report format and scan logic live in one place. If the format evolves, all agents benefit without individual updates.
- **Reusability** — Non-runesmith agents and future plugins can invoke `rs-discover` as long as they have permission.
- **Auditability** — The read-only constraint is enforced at the skill level, not at the agent level. This makes it impossible for discovery to accidentally mutate state.

### The `rs-` Prefix Convention

The `rs-` prefix scopes the skill namespace within the `@runicengines/opencode-runesmith` plugin. This prevents naming collisions with:
- First-party OpenCode skills (no prefix)
- Skills from other plugins (`kb-*` for knowledge-base, etc.)

Other runesmith utility skills follow the same convention: `rs-query`, `rs-validate`, `rs-context`, etc.

## Future Considerations

- **Incremental re-scanning**: Future iterations could diff the previous scan against the current filesystem and update only the changed sections.
- **Custom plugins**: Projects may contribute their own discovery extensions (e.g., a Django plugin adds `manage.py` and `migrations/` detection).
- **Confidence scoring**: The report could annotate each field with a confidence rating — `confirmed` (read from manifest), `inferred` (from naming conventions), `unknown` (not found).
