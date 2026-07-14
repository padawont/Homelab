---
title: "DevSpace Core Workflows: devspace dev and devspace deploy"
status: draft
author: padawont
date: 2026-07-13
tags:
  - devspace
  - workflows
  - dev
  - deploy
  - kubernetes
sources:
  - url: "https://www.devspace.sh/docs/getting-started/development"
    title: "Development with DevSpace — Official Docs"
  - url: "https://www.devspace.sh/docs/getting-started/introduction"
    title: "What is DevSpace — Official Docs"
  - url: "https://www.devspace.sh/docs/configuration/pipelines/"
    title: "Pipelines — Official Docs"
  - url: "https://www.devspace.sh/docs/cli"
    title: "CLI Reference — Official Docs"
last_audit_date: 2026-07-13
---

# DevSpace Core Workflows: devspace dev and devspace deploy

## Cluster & Namespace Selection

Before running any workflow, point DevSpace to the right cluster and namespace:

```shell
devspace use context                  # select Kubernetes cluster
devspace use namespace my-namespace   # creates namespace if it doesn't exist
```

These commands can be run anytime to switch between clusters or namespaces.

## `devspace dev` — Development Mode

`devspace dev` executes the `dev` pipeline defined in `devspace.yaml`. See [architecture-pipeline-model.md](architecture-pipeline-model.md) for the full pipeline model, built-in functions, and profile composition. It deploys dependencies, creates deployments, and starts an interactive development session.

### Example `dev` Pipeline

A typical custom `dev` pipeline (from the getting-started guide):

```yaml
pipelines:
  dev:
    run: |-
      run_dependencies --all           # 1. Deploy dependent projects
      create_deployments --all         # 2. Deploy Helm charts / manifests
      start_dev app                    # 3. Start dev mode "app"
```

This example runs three commands:
1. **`run_dependencies --all`** — deploys all dependencies (other microservices, possibly from separate repos with their own `devspace.yaml`)
2. **`create_deployments --all`** — deploys everything in the `deployments` section
3. **`start_dev app`** — starts the dev mode named `app` from the `dev` section; this enables file sync, port forwarding, terminal, and an SSH server

See [Default Pipeline Behaviors](#default-pipeline-behaviors) below for the actual built-in default if no custom pipeline is defined.

### What Happens During `devspace dev`

1. Selects the target container (via `imageSelector` or `labelSelector`)
2. Optionally swaps the container image with a `devImage` (prebuilt dev image with tooling)
3. Starts bi-directional file sync between local project and container — see [file-sync-hot-reload.md](file-sync-hot-reload.md) for sync configuration, strategies, and hot reload options
4. Forwards ports from the container to localhost (and optionally reverse-forwards local ports into the container)
5. Opens a terminal to the dev container (or streams logs)
6. Starts the DevSpace UI on localhost (default port 8090)

### Starting Your Application

Once the terminal opens to the dev container, start the application:

```shell
npm start              # Node.js
python main.py         # Python
go run main.go         # Go
dotnet run             # ASP.NET
```

### DevSpace UI

When `devspace dev` runs, DevSpace starts a client-only localhost UI. By default it binds to `http://localhost:8090`. If the port is in use, DevSpace picks the next available port and prints the URL in the terminal output.

The UI provides a real-time development dashboard with:
- **File sync panel** — shows active sync paths, transfer progress, and recent file changes
- **Port forwarding table** — lists all forwarded ports with their local-to-remote mapping
- **Pod logs** — streaming logs from the selected container
- **Terminal access** — in-browser terminal to the dev container
- **Resource overview** — status of deployments, pods, and services in the active namespace

The UI is purely client-side — no data leaves your machine. It reads cluster state through your existing kube-context. To disable the UI, pass `--show-ui=false` to `devspace dev`.

To access the UI explicitly (even when not running `devspace dev`):
```shell
devspace dev --show-ui
```

### Useful `devspace dev` Flags

| Flag | Description |
|---|---|---|
| `-b, --force-build` | Forces to build every image |
| `-d, --force-deploy` | Forces to deploy every deployment |
| `--skip-build` | Skips building of images |
| `--skip-deploy` | If enabled will skip deploying |
| `--skip-push` | Skips image pushing, useful for minikube deployment |
| `-t, --tag` | Use the given tag for all built images |
| `--pipeline` | The pipeline to execute (default "dev") |
| `-p, --profile` | The DevSpace profiles to apply. Multiple profiles are applied in the order they are specified |
| `--render` | If true will render manifests and print them instead of deploying |

## `devspace deploy` — Deployment Mode

`devspace deploy` executes the `deploy` pipeline. It builds images, pushes them, and deploys to the cluster — without starting an interactive dev session.

### Example `deploy` Pipeline

A typical custom `deploy` pipeline:

```yaml
pipelines:
  deploy:
    run: |-
      run_dependencies --all                          # 1. Deploy dependencies
      build_images --all -t $(git describe --always)  # 2. Build and tag all images
      create_deployments --all                        # 3. Deploy manifests
```

This example runs:
1. **`run_dependencies --all`** — deploys dependencies
2. **`build_images --all`** — builds all images defined in the `images` section; `-t $(git describe --always)` tags images with the git commit hash
3. **`create_deployments --all`** — deploys all deployments

See [Default Pipeline Behaviors](#default-pipeline-behaviors) below for the actual built-in default.

### Useful `devspace deploy` Flags

Same flags as `devspace dev` (see [table above](#useful-devspace-dev-flags)).

## Default Pipeline Behaviors

If you do not define a custom pipeline, DevSpace uses built-in defaults. See the [default pipeline table in architecture-pipeline-model.md](architecture-pipeline-model.md#pipelines-model) for the complete reference. At a glance:

| Command | Default Pipeline Summary |
|---|---|
| `devspace dev` | Dependencies → Pull secrets → Build → Deploy → Start dev |
| `devspace deploy` | Dependencies → Pull secrets → Build → Deploy |
| `devspace build` | Dependencies (build pipeline) → Build images |
| `devspace purge` | Stop dev → Purge deployments → Dependencies (purge pipeline) |

## Running Multiple `devspace dev` Instances

Running `devspace dev` multiple times in parallel for the same project (same `name` in `devspace.yaml`) fails because port forwarding and file sync instances conflict. Running `devspace dev` for different projects (different `devspace.yaml` files with different `name` values) works seamlessly.

## Cross-Platform Pipeline Execution

Pipelines are written in POSIX shell syntax but executed via an emulated bash that works identically on Linux, macOS, and Windows. You can use `if`, `&&`, `||`, `for` loops, and variable substitution.

## Pitfalls

- **Config variables**: Use `--var MYVAR=MYVALUE` or `${VARIABLES}` in `devspace.yaml` to handle environment-specific differences (e.g., subdomains, namespaces). Variables can be sourced from environment, user input, or commands.
- **Parallel dev sessions**: You cannot run `devspace dev` twice for the same project simultaneously. Use different projects or work on different branches.
- **Pipeline order matters**: `build_images` must run before `create_deployments` if deployments reference the freshly built images. The default pipelines handle this correctly.
