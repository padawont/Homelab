---
title: "Devbox — Usage"
status: exploring
author: "Ryan Harris (padawont)"
date: 2026-06-17
tags: ["devbox", "usage", "workflow", "docker", "openchoreo"]
sources:
  - "https://www.jetify.com/docs/devbox/quickstart/"
  - "https://www.jetify.com/docs/devbox/cli-reference/devbox-run/"
  - "https://www.jetify.com/docs/devbox/cli-reference/devbox-shell/"
  - "https://www.jetify.com/docs/devbox/cli-reference/devbox-generate-dockerfile/"
  - "https://www.jetify.com/docs/devbox/cli-reference/devbox-generate-devcontainer/"
last_audit_date: 2026-06-17
---

# Devbox — Usage

## End-to-End Project Workflow

Start a new project, add tools, develop, and share.

```bash
devbox init                          # creates devbox.json
devbox search go                     # find available versions
devbox add go@1.23 golangci-lint     # add packages with optional version pin
devbox install                       # install all declared packages
devbox shell                         # enter isolated environment
go version                           # use the tools
exit                                 # leave the shell
```

### Adding and Removing Packages

```bash
devbox add go@1.23                  # pin exact version
devbox add ripgrep@latest           # latest available
devbox rm golangci-lint             # remove a package
```

Use `devbox search <pkg>` to list available versions before adding.

### Shell Modes

- `devbox shell` -- interactive subshell with declared packages on `$PATH`
- `devbox shell --pure` -- isolated shell inheriting almost no host variables (retains `HOME`, `USER`, `DISPLAY`)
- `devbox shell --env MY_VAR=value` -- inject additional env vars

### Running Commands

Define named scripts in `devbox.json` (see [configuration.md](./configuration.md)):

```bash
devbox run test                      # runs script from devbox.json
```

Run arbitrary commands without a script definition:

```bash
devbox run go build ./...
devbox run -q lsof -i :8080         # quiet mode, suppresses logs
devbox run --env MY_VAR=value --env-file .env.prod ./deploy.sh
```

### Exiting

- From a shell: type `exit` or press CTRL-D
- From a running script/command: CTRL-C terminates the process and exits the shell

### Source Control

Commit both `devbox.json` and `devbox.lock` to source control. The lock file pins exact Nix commit hashes so all contributors get identical environments.

### Cleanup

Devbox has no `devbox clean` command. For Nix store garbage collection and disk cleanup, see [troubleshooting.md](./troubleshooting.md).

---

## Docker / Container Integration

Devbox can generate container images or Dev Container configurations from any `devbox.json`, keeping the toolchain definition as the single source of truth.

### Dockerfile

```bash
devbox generate dockerfile
```

Flags:

| Flag | Description |
|---|---|
| `--root-user` | Use root as container user; installs Nix in single-user mode |
| `-f, --force` | Overwrite existing files |
| `-c, --config string` | Path to directory containing `devbox.json` |

Use cases:
- CI/CD images that match the local dev environment exactly
- Production images built from the same toolchain definition

See [devbox-ci/dockerfile.md](../../operations/ci-cd/devbox-ci/dockerfile.md) for CI-specific usage and caching strategies.

### Dev Container

```bash
devbox generate devcontainer
```

Generates `.devcontainer/Dockerfile` and `.devcontainer/devcontainer.json` for VS Code Remote -- Containers.

Flags:

| Flag | Description |
|---|---|
| `--root-user` | Use root as container user |
| `-f, --force` | Overwrite existing files |

---

## Global vs Project-Level Usage

| Scope | Use for | Command |
|---|---|---|
| **Project** | Runtime-specific tools (language runtimes, linters, build tools) | `devbox add <pkg>` in project directory |
| **Global** | System-wide tools (ripgrep, htop, git, shell utilities) | `devbox global add <pkg>` |

**Decision framework:** Project-level is the default and should be used for everything a contributor needs to build, test, and run the project. Global is reserved for tools the developer wants in every shell regardless of project context.

See [global-packages.md](./global-packages.md) for global setup, `shellenv`, and config sharing.

---

## OpenChoreo Pilot (P-03) Integration Patterns

Within the OpenChoreo pilot (ADR 0008), Devbox serves as the toolchain declaration layer. The sample Go service uses devbox to express the exact Go version, linter, and build tooling.

### Recommended devbox.json for the Sample Go Service

```json
{
  "packages": ["go@1.23", "golangci-lint@latest"],
  "env": {
    "GOFLAGS": "-mod=mod"
  },
  "shell": {
    "scripts": {
      "build": "go build -o bin/service ./cmd/service",
      "test": "go test -v -race -count=1 ./...",
      "lint": "golangci-lint run ./..."
    }
  }
}
```

### Build/Test Matching CI

Define scripts in `devbox.json` that match the CI pipeline exactly. The same tools and versions run locally and in CI:

```bash
devbox run build
devbox run test
devbox run lint
```

### Direnv for Auto-Loading

```bash
devbox generate direnv
```

Entry into the project directory automatically loads the Go toolchain. See [ide-integration.md](./ide-integration.md) for direnv setup and limitations.

### Service Sidecars via process-compose

For components that depend on sidecar services (caches, databases), define them in `process-compose.yml`. This maps to the OpenChoreo Component + Endpoint model where a component may declare dependencies on endpoints provided by other components:

```yaml
version: "0.5"
processes:
  redis:
    command: redis-server
    availability:
      restart: "always"
```

See [services.md](./services.md) for the full service management reference.

### Related

- ADR 0008: [Pilot OpenChoreo as an IDP](../../../adr/0008-pilot-openchoreo-idp/overview.md) — full pilot scope and go/no-go criteria
