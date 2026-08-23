---
name: rs-discover
description: >
  Scan a codebase for structural context: entry points, module
  organisation, test layout, conventions, dependency manifests,
  and CI configuration. Produces a YAML context report.
license: MIT
compatibility: opencode
metadata:
  plugin: "@runicengines/opencode-runesmith"
  workflow: planning
  audience: developers
  trigger: manual+chained
---

## Purpose

Read-only codebase scanner. Turns an unknown repository into a shared mental model.

Key characteristics:

- **Read-only**: Never edits, writes, or modifies any file. Only reads.
- **Deterministic**: Same input → same output (modulo file modifications over time).
- **Session-scoped caching**: Report cached for 60s TTL within the agent session. Repeated calls within TTL return cached report.
- **Agent-agnostic**: Architect, developer, spec-writer — all agents invoke the same skill.

## When to Invoke

Trigger `rs-discover` when:

- A session starts on a repository the agent has not seen before.
- The agent explicitly requests a fresh context refresh (`refresh: true` bypasses cache).
- Structural context is missing or stale.

Do NOT invoke when:

- A valid cached report exists within the 60s TTL (cache hit).
- The agent is already familiar with the codebase.
- The task is purely textual or conceptual with no codebase interaction.

## Workflow Steps

### 1. Read root-level manifests

Inspect `README.md`, `package.json`, `pyproject.toml`, `Cargo.toml`, `Gemfile`, `go.mod`, `composer.json`, `CMakeLists.txt`, `Makefile`, or any equivalent file at the repository root. Extract project name, description, runtime, and version constraints. Determine `project.package_manager` by checking for lock files and manifests: `bun.lock` → bun, `package-lock.json` → npm, `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `Pipfile`/`requirements.txt` → pip, `poetry.lock` → poetry, `Cargo.toml` → cargo, `go.mod` → go-mod.

### 2. Identify project type and framework

Determine whether this is a web application, CLI tool, library, monorepo, or polyglot project. Identify the primary framework (Next.js, FastAPI, Rails, Spring, Actix, etc.) and note any secondary frameworks for sub-projects.

### 3. Map directory structure

Walk the top two levels. Locate:

- **Source code** — `src/`, `lib/`, `app/`, `packages/`
- **Tests** — `tests/`, `spec/`, `__tests__/`, `*.test.ts`, `*.spec.py`
- **Docs** — `docs/`, `wiki/`, `*.md`
- **Configs** — `.env*`, `*config.*`, `tsconfig.json`, `.babelrc`, `.eslintrc.*`
- **CI** — `.github/`, `.gitlab-ci.yml`, `Jenkinsfile`
- **Infra** — `Dockerfile`, `docker-compose.yml`, `terraform/`, `k8s/`
- **Tools** — Linter configs (`.eslintrc.*`, `eslint.config.*`), formatter configs (`.prettierrc*`, `.editorconfig`), type checker configs (`tsconfig.json`, `pyproject.toml` [tool.ty] sections), test configs (jest.config, vitest.config, pytest config in `pyproject.toml`), git hooks (`.git/hooks/`, `.husky/`, `.pre-commit-config.yaml`). Populate `tools.lint`, `tools.format`, and `tools.typecheck` with each tool found and its config path.

### 4. Identify entry points

Locate primary runtime entry points:

- **App servers** — `main.py`, `index.ts`, `app.py`, `server.js`
- **CLI** — `cli.py`, `bin/`, `cmd/`, `package.json` `bin` field
- **Workers** — background job entry points

### 5. List key dependencies

Extract runtime and dev dependencies from the appropriate manifest. Note runtime version (Node 18+, Python 3.11+) and pinned platform requirements. Also detect the test runner from devDependencies or tool configs (bun:test, vitest, jest, pytest, etc.) and populate `tools.test.runner`.

### 6. Detect tools, environment, and git conventions

Scan for file `.env.example` or `.envrc` and extract required environment variable names into `environment.required`. Also parse `.env.example` for optional variables (those with a default value after `=` in comments or after the `=` sign) and populate `environment.optional`. Scan `.git/hooks/` directory, `.husky/`, and `.pre-commit-config.yaml` to detect hooks tool and populate `git.hooks_tool`. Populate `git.hooks` with the list of hook names found (e.g. `pre-commit`, `commit-msg`). Check for commitlint config (`commitlint.config.js`, `.commitlintrc*`) to determine `git.conventional_commits`. Check for an ADR directory (`docs/adr/`, `adr/`) and populate `git.adr_dir`.

### 7. Note custom/unusual configurations

Flag anything non-standard:

- Custom build tooling or task runners
- Unusual project structure (flat source, generated code)
- Monorepo tooling (Turborepo, Nx, Lerna, Bazel)
- Feature flags or environment gating
- Vendor directories or pinned dependencies

### 8. Output structured context report (with confidence scores)

Produce the report in the YAML format below. Cache in session (60s TTL) so downstream agents don't re-scan. Annotate each field with a confidence score: `confirmed` when read directly from a manifest or detected file, `inferred` when derived from naming conventions or directory layout patterns, `unknown` when no evidence is found. Populate the `confidence` map accordingly.

Before returning, populate the `metadata` block: set `generated_at` to the current ISO 8601 timestamp, `schema_version` to `"1.0"`, `generator` to `"opencode-runesmith/rs-discover@1.0.0"`, and `cache_ttl` to `60`.

## Output Format

```yaml
metadata:
  generated_at: "2026-07-11T14:30:00Z"
  schema_version: "1.0"
  generator: "opencode-runesmith/rs-discover@1.0.0"
  cache_ttl: 60

project:
  name: "project-name"
  type: "web-app | cli-tool | library | monorepo | polyglot"
  runtime:
    language: "python | node | rust | go | ..."
    version: ">=3.11"
    manager: "devbox | nvm | asdf | mise | pyenv | null"
    lock_file: "bun.lock | package-lock.json | Cargo.lock | null"
  framework:
    primary: "FastAPI"
    secondary: []
  package_manager: "bun | npm | pnpm | yarn | pip | poetry | cargo | go-mod | null"

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

tools:
  test:
    runner: "bun:test | vitest | pytest | go-test | cargo-test | null"
    framework: ""
    coverage:
      enabled: true
      threshold: 0.65
  lint:
    - name: "eslint"
      config: "eslint.config.js"
  format:
    - name: "prettier"
      config: ".prettierrc"
  typecheck:
    tool: "tsc"
    config: "tsconfig.json"
    strict: true

build:
  system: "poetry | npm | cargo | bun | ..."
  commands:
    build: "npm run build"
    test: "npm test"
    lint: "npm run lint"
    format: "npm run format"
    typecheck: "tsc --noEmit"
    clean: ""
    dev: "npm run dev"
    run: "npm start"

deployment:
  platform: "docker | vercel | aws-ecs | ..."
  config: "Dockerfile + docker-compose.yml"

environment:
  required:
    - name: "GITHUB_TOKEN"
      description: "GitHub personal access token with read:packages"
      source: ".envrc"
  optional:
    - name: "NODE_ENV"
      default: "development"

git:
  hooks:
    - "pre-commit"
    - "commit-msg"
  hooks_tool: "husky | lefthook | pre-commit | null"
  conventional_commits: true
  adr_dir: "docs/adr/ | null"

confidence:
  project.name: "confirmed"
  project.type: "confirmed"
  project.runtime.language: "confirmed"
  project.runtime.version: "confirmed"
  structure.source: "confirmed"
  structure.tests: "confirmed"
  entry_points.app: "confirmed"
  deployment.platform: "inferred"

anomalies: []
```

## Required Permissions

The calling agent must have these tools available:

| Tool     | Required      | Scope               | Purpose                                               |
| -------- | ------------- | ------------------- | ----------------------------------------------------- |
| read     | Yes           | All files           | Read manifests, configs, source structure             |
| glob     | Yes           | Source tree         | Pattern-match source, test, config directories        |
| grep     | Yes           | Source tree         | Search for entry-point patterns, framework signatures |
| bash     | No (optional) | Node/python version | Run version detection if manifests lack version info  |
| edit     | No            | —                   | Never modifies files                                  |
| write    | No            | —                   | Never creates files                                   |
| delegate | No            | —                   | Never delegates to KB agents; pure codebase scanner   |

## Chained Skills

None.

## See Also

- `rs-consult` — domain expertise skill
- `rs-issue-to-plan` — consumer of this skill's output
