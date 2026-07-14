---
title: "DevSpace Architecture & Pipeline Model"
status: draft
author: padawont
date: 2026-07-13
tags:
  - devspace
  - architecture
  - pipeline
  - devspace-yaml
  - kubernetes
sources:
  - url: "https://www.devspace.sh/docs/configuration/reference"
    title: "devspace.yaml Config Reference — Official Docs"
  - url: "https://www.devspace.sh/docs/configuration/images/"
    title: "Images Configuration — Official Docs"
  - url: "https://www.devspace.sh/docs/configuration/deployments/"
    title: "Deployments Configuration — Official Docs"
  - url: "https://www.devspace.sh/docs/configuration/profiles/"
    title: "Profiles Configuration — Official Docs"
  - url: "https://www.devspace.sh/docs/configuration/pipelines/"
    title: "Pipelines Configuration — Official Docs"
last_audit_date: 2026-07-13
---

# DevSpace Architecture & Pipeline Model

## `devspace.yaml` Top-Level Schema

Every DevSpace project requires a `devspace.yaml` at the project root. The supported version is `v2beta1` (the latest; older versions are auto-converted).

```yaml
version: v2beta1
name: my-project
```

| Field | Type | Required | Description |
|---|---|---|---|
| `version` | string | yes | Config version (e.g., `v2beta1`). Older versions auto-converted. |
| `name` | string | yes | Unique project identifier. No two active projects with the same name in the same namespace. Defaults to the directory name. |
| `imports` | array | no | Merge configs from local paths, git repos, or URLs |
| `functions` | map | no | POSIX functions reusable in pipelines |
| `pipelines` | map | no | Workflow definitions executed by CLI commands; DevSpace provides built-in defaults for dev, deploy, build, and purge |
| `images` | map | no | Image build configuration |
| `deployments` | map | no | Deployment configuration (Helm, kubectl, kustomize) |
| `dev` | map | no | Development mode configuration |
| `vars` | map | no | Config variables |
| `commands` | map | no | Custom reusable commands (`devspace run <name>`) |
| `dependencies` | map | no | References to other DevSpace projects |
| `profiles` | array | no | Profile overrides for environments/teams |
| `hooks` | array | no | Lifecycle hooks |
| `pullSecrets` | array | no | Registry pull secrets |
| `localRegistry` | object | no | Local registry for in-cluster builds |
| `require` | object | no | Required tools/plugins |

## Imports

Configs can be split across multiple files and composed:

```yaml
imports:
  - path: ./common-config.yaml        # local path
  - git: https://github.com/org/shared-configs.git
    subPath: ./team-a
    branch: main
```

## Pipelines Model

Pipelines are POSIX shell scripts with built-in DevSpace functions. Four pipelines have special meaning (they override default command behavior):

| Pipeline | Triggered By | Default Behavior |
|---|---|---|---|
| `dev` | `devspace dev` | Dependencies → Pull secrets → Build → Deploy → Start dev |
| `deploy` | `devspace deploy` | Dependencies → Pull secrets → Build → Deploy |
| `build` | `devspace build` | Dependencies (build pipeline) → Build images |
| `purge` | `devspace purge` | Stop dev → Purge deployments → Dependencies (purge pipeline) |

### Pipeline Built-In Functions

| Function | Purpose |
|---|---|
| `build_images [names...]` | Build images in parallel; `--all`, `--tag`, `--force-rebuild`, `--skip-push` |
| `create_deployments [names...]` | Deploy manifests in parallel; `--all`, `--force-redeploy`, `--render` |
| `start_dev [names...]` | Start dev mode; `--disable-sync`, `--disable-port-forwarding` |
| `stop_dev [names...]` | Stop dev mode |
| `run_dependencies --all` (alias for `run_dependency_pipelines --all`) | Deploy dependencies |
| `run_pipelines [names...]` | Run other pipelines (supports `--background` and `--sequential`) |
| `run_default_pipeline [name]` | Run a pipeline's default behavior |
| `ensure_pull_secrets --all` | Create pull secrets for all images |
| `purge_deployments [names...]` | Remove deployments |
| `exec_container [cmd]` | Execute a command in a selected container |
| `select_pod` | Return a pod name matching selectors |
| `wait_pod [cmd]` | Wait for a pod to become ready |
| `get_image [name]` | Return the most recently built image/tag |
| `get_config_value [json-path]` | Read a value from the loaded config |
| `get_flag [name]` | Read a custom pipeline flag value |
| `is_equal`, `is_empty`, `is_in`, `is_os`, `is_true` | Condition checks |
| `run_watch [cmd]` | Watch files and rerun a command on changes |
| `cat`, `sleep`, `xargs` | Utility functions |

### Custom Pipeline Flags

Pipelines can define custom CLI flags:

```yaml
pipelines:
  deploy:
    flags:
      - name: dockerfile
        short: d
        type: string
        description: "Override the Dockerfile path"
    run: |-
      if ! is_empty $(get_flag dockerfile); then
        run_default_pipeline deploy --set "images.my-image.dockerfile=$(get_flag dockerfile)"
      else
        run_default_pipeline deploy
      fi
```

## Images Configuration

The `images` section defines how DevSpace builds container images:

```yaml
images:
  app:
    image: myregistry.com/org/app
    tags: ["latest"]
    dockerfile: ./Dockerfile
    context: ./
    rebuildStrategy: default  # default | always | ignoreContextChanges
    skipPush: false
    createPullSecret: true
```

### Build Engines

DevSpace supports four build engines:

| Engine | Where | Use Case |
|---|---|---|
| `docker` | Local Docker daemon | Fastest for local dev; falls back to kaniko if Docker is unavailable |
| `buildKit` | Local or in-cluster | Docker buildx; supports `preferMinikube` |
| `kaniko` | In-cluster pod | No Docker daemon required; good for CI |
| `custom` | External script | Custom build tools (jib, bazel, etc.) |

```yaml
images:
  app:
    image: myregistry.com/org/app
    docker: {}                          # local Docker daemon
    # or
    kaniko:                             # in-cluster with kaniko
      cache: true
      namespace: devspace-builds
    # or
    buildKit:
      inCluster: {}                     # in-cluster BuildKit
    # or
    custom:
      command: "jib build -i ${runtime.images.app.image}:${runtime.images.app.tag}"
```

### In-Memory Image Overrides

DevSpace can modify the Dockerfile in memory during build:

```yaml
images:
  app:
    entrypoint: ["sleep", "99999"]     # Override entrypoint
    cmd: ["server"]                     # Override CMD
    appendDockerfileInstructions:       # Append raw instructions
      - "RUN apt-get update && apt-get install -y curl"
```

## Deployments Configuration

The `deployments` section defines how to deploy resources:

```yaml
deployments:
  api-server:
    helm:
      chart:
        name: my-chart
        repo: https://charts.example.com
        version: "1.2.3"
      values:
        replicas: 3
      valuesFiles:
        - values.yaml
      namespace: my-namespace
    updateImageTags: true
```

### Deployment Methods

| Method | Description |
|---|---|
| `helm` | Deploy via Helm charts (from repos, local paths, or git) |
| `kubectl` | Apply raw manifests (files, folders, or inline YAML) |
| `kustomize` | Apply via kustomize (set `kustomize: true` under `kubectl`) |

```yaml
deployments:
  raw-manifests:
    kubectl:
      manifests:
        - ./k8s/namespace.yaml
        - ./k8s/deployment.yaml
      applyArgs: ["--server-side"]

  kustomized:
    kubectl:
      manifests:
        - ./k8s/overlays/prod
      kustomize: true
```

### Patches

Both `kubectl` deployments and `dev` configurations support JSON patches:

```yaml
deployments:
  app:
    kubectl:
      manifests:
        - ./deployment.yaml
      patches:
        - target:
            kind: Deployment
            name: my-app
          op: replace
          path: /spec/replicas
          value: 5
```

## Dev Configuration

The `dev` section defines the development experience. See [file-sync-hot-reload.md](file-sync-hot-reload.md) for detailed sync and port forwarding configuration.

Key fields:
- `imageSelector` or `labelSelector` — selects the target pod
- `devImage` — swaps the container image for a dev-optimized one
- `command`/`args`/`workingDir`/`env` — container overrides
- `ports` — port forwarding
- `sync` — file sync configuration
- `terminal`/`logs`/`attach` — foreground dev workflow
- `ssh` — SSH tunnel for IDE integration
- `proxyCommands` — proxy local commands (e.g., kubectl, helm) into the container
- `open` — auto-open URLs when the dev container is ready

## Profiles

Profiles allow environment-specific or team-specific overrides:

```yaml
profiles:
  - name: production
    patches:
      - op: replace
        path: /images/app/image
        value: myregistry.com/org/app:prod
  - name: debug
    patches:
      - op: replace
        path: /dev/app/command
        value: ["sleep", "99999"]
```

Apply profiles with:

```shell
devspace dev -p debug
devspace dev -p production -p debug  # multiple profiles applied in order
```

Profile activation can be automatic based on context (e.g., kube-context name). Profile patches use JSON Patch semantics (add, remove, replace).

## Config Variables

Variables (`vars`) make configs dynamic per developer or environment:

```yaml
vars:
  MY_DOMAIN:
    question: "Enter your subdomain"
    default: "dev"
  REGISTRY:
    source: env
    default: "ghcr.io"
```

Referenced as `${MY_DOMAIN}` in any config field. Set via `--var MY_VAR=value` at runtime.

## Pitfalls

- **YAML anchors vs JSON Patch**: Use YAML anchors (`&`, `<<:`) for simple repetition, but prefer **profiles** with JSON Patch for environment-specific overrides. Profiles compose cleanly; YAML anchors can have ordering issues.
- **Image tag collisions**: If `tags` is empty, DevSpace generates a random tag each build. For CI/CD, always pass `-t $(git describe --always)` or a meaningful tag.
- **Kaniko namespace**: The kaniko build pod runs in the namespace specified under `kaniko.namespace` (defaults to the active namespace). Ensure the service account has sufficient permissions.
