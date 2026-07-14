# ADR-0001: Use Devbox and Direnv

## README.md

# ADR 0001: Use Devbox with direnv for Development Environments

Adopt Devbox (with direnv) as the standard development environment tool across all RunicEngines repositories for reproducible, portable dev shells.

See [overview.md](./overview.md) for the full decision record.

## overview.md

---
adr: 0001
title: Use Devbox with direnv for Development Environments
author: Khalid
status: final
topic: developer-tooling
technology: ["Devbox", "direnv"]
date: 2026-05-24
date-proposed: 2026-05-24
history: "https://github.com/RunicEngines/knowledge-base/pull/2"
context: >
  Each RunicEngines repo has ad-hoc README setup instructions. Tool versions
  drift across projects, contributors hit "works on my machine" issues, and
  onboarding requires deciphering manual install steps.
decision: >
  All RunicEngines repositories MUST adopt Devbox (devbox.json + devbox.lock)
  to declare and pin exact toolchain versions. direnv MUST be configured via
  `devbox generate direnv` for automatic environment activation on directory
  entry. Devbox Scripts SHOULD replace ad-hoc Makefile targets and README
  setup instructions.
consequences: >
  Reproducible pinned toolchains across projects; instant onboarding
  (clone → direnv allow); IDE integration via direnv; Devbox services
  for databases and background processes; CI/local parity via devbox run.
  Trade-off: new dependency (Devbox + direnv) for all contributors; shell
  aliases and functions from init_hook unavailable under direnv (use Devbox
  Scripts instead).
sources:
  - "https://www.jetify.com/docs/devbox/"
  - "https://direnv.net/"
  - "../knowledge/tooling/dev-environments/devbox/"
  - "../knowledge/tooling/dev-environments/direnv/"
references: []
---

# ADR 0001: Use Devbox with direnv for Development Environments

## Status

Final (2026-05-24)

## Context and Problem Statement

Each RunicEngines repository documents its required toolchain in README files with ad-hoc installation instructions. This leads to several problems:

- Tool versions drift across projects — one repo requires Go 1.21, another Go 1.23, with no standardized way to manage this.
- Contributors must manually install and version-manage each tool in their host environment.
- "Works on my machine" issues arise from subtle OS or shell configuration differences.
- Onboarding requires deciphering and executing manual setup steps before making a first contribution.
- PRs may introduce new tool dependencies without any enforcement or documentation.

We need a standardized, reproducible development environment that works across Linux and macOS, integrates with IDEs, and is simple enough that new contributors can get started with minimal friction.

## Decision

All RunicEngines repositories MUST adopt Devbox as the standard development environment tool, with direnv as the recommended activation mechanism.

Specifically:

1. **Every repo MUST contain a `devbox.json`** declaring all required tools with pinned versions, and a committed `devbox.lock` for lockfile reproducibility.
2. **direnv MUST be configured** via `devbox generate direnv` so the environment activates automatically when a contributor `cd`s into the project directory. The generated `.envrc` MUST be committed.
3. **Devbox Scripts** (defined in `devbox.json` under `shell.scripts`) SHOULD replace ad-hoc Makefile targets and README setup instructions for common tasks (build, test, lint, format).
4. **Devbox services** SHOULD be used for background processes such as databases and caches where applicable, replacing Docker Compose for local development.
5. **CI pipelines SHOULD use `devbox run`** to execute commands, ensuring parity between local and CI environments.

This approach was chosen because Devbox provides Nix-grade reproducibility without requiring contributors to learn the Nix language, and direnv makes the experience seamless — clone, `direnv allow`, and start contributing.

## Consequences

**Positive:**

- Pinned, reproducible toolchains across every project — no version drift.
- Instant onboarding: `git clone` → `direnv allow` → start contributing.
- IDE integration via the direnv VS Code extension (or Devbox extension).
- Devbox services for databases, caches, and other background processes.
- CI/local environment parity via `devbox run`.
- No Docker daemon required for local development.
- Each repo's toolchain is self-documenting via `devbox.json`.

**Negative:**

- All contributors must install Devbox and direnv on their machines.
- Shell aliases and functions defined in `devbox.json` `init_hook` are not available under direnv (use Devbox Scripts instead).
- `$PS1` modifications in `init_hook` do not work with direnv.
- Devbox CLI is not supported natively on Windows (requires WSL2).
- Contributors using `devbox shell` instead of direnv will need to remember to enter the shell manually.

## Considered Options

### Devbox + direnv (chosen)

- **Pros**: Nix-grade reproducibility without Nix language; automatic activation via direnv; services support; CI parity; IDE extensions available; free and open source (Apache 2.0).
- **Cons**: New tooling dependency; direnv limitations with `init_hook`; Windows requires WSL2.

### Docker Compose

- **Pros**: Widely adopted; container-level isolation; Windows native support.
- **Cons**: Docker daemon overhead (CPU/memory); slower startup; more complex networking; no automatic environment activation on `cd`; filesystem permission issues across host/container; overkill for tools-only use cases.

### Ad-hoc README instructions (current state)

- **Pros**: No new tooling to install.
- **Cons**: Drift-prone; manual setup; no reproducibility; "works on my machine" inherent; no version enforcement.

### Nix flakes

- **Pros**: Maximum reproducibility; no direnv limitation issues; full Nix ecosystem.
- **Cons**: Steep Nix language learning curve; smaller pool of contributors familiar with it; overkill for the toolchain-only needs of most RunicEngines projects.
