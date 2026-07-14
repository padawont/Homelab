---
title: "DevSpace Installation & Project Configuration"
status: draft
author: padawont
date: 2026-07-13
tags:
  - devspace
  - installation
  - configuration
  - kubernetes
sources:
  - url: "https://www.devspace.sh/docs/getting-started/installation"
    title: "Install DevSpace — Official Docs"
  - url: "https://www.devspace.sh/docs/getting-started/initialize-project"
    title: "Initialize Project — Official Docs"
  - url: "https://www.devspace.sh/docs/ide-integration/visual-studio-code"
    title: "VS Code Integration — Official Docs"
  - url: "https://github.com/loft-sh/devspace"
    title: "DevSpace GitHub Repository"
last_audit_date: 2026-07-13
---

# DevSpace Installation & Project Configuration

## Installation

DevSpace is a client-only binary with no server-side component or dependencies. It communicates with your Kubernetes cluster using your existing kube-context.

### macOS

```shell
# Homebrew
brew install devspace

# Intel
curl -L -o devspace "https://github.com/loft-sh/devspace/releases/latest/download/devspace-darwin-amd64" && sudo install -c -m 0755 devspace /usr/local/bin

# Apple Silicon
curl -L -o devspace "https://github.com/loft-sh/devspace/releases/latest/download/devspace-darwin-arm64" && sudo install -c -m 0755 devspace /usr/local/bin
```

### Linux

```shell
# AMD64
curl -L -o devspace "https://github.com/loft-sh/devspace/releases/latest/download/devspace-linux-amd64" && sudo install -c -m 0755 devspace /usr/local/bin

# ARM64
curl -L -o devspace "https://github.com/loft-sh/devspace/releases/latest/download/devspace-linux-arm64" && sudo install -c -m 0755 devspace /usr/local/bin
```

### Windows

```powershell
# PowerShell
md -Force "$Env:APPDATA\devspace"; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]'Tls,Tls11,Tls12';Invoke-WebRequest -URI "https://github.com/loft-sh/devspace/releases/latest/download/devspace-windows-amd64.exe" -o $Env:APPDATA\devspace\devspace.exe;$env:Path += ";" + $Env:APPDATA + "\devspace";[Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::User);

# Scoop
scoop install devspace
```

Alternatively, download the binary for any platform from the [GitHub Releases](https://github.com/loft-sh/devspace/releases) page and add it to your PATH.

## VS Code Extension

DevSpace integrates with VS Code via the [Remote - SSH Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh). The workflow is:

1. DevSpace injects an SSH server into the dev container
2. Configures a local SSH host entry in `~/.ssh/config`
3. VS Code connects to the remote container via SSH

This requires:
- DevSpace CLI installed
- A valid kube-context
- VS Code + Remote - SSH Extension + CLI command installed (`code` in PATH)

Run `devspace dev -n my-namespace` inside a project with `ssh.enabled: true` in the dev config. VS Code opens automatically inside the container when the pipeline includes `code --folder-uri vscode-remote://ssh-remote+<hostname>/app`.

Note: Alpine-based images are not supported for VS Code remote development.

## Project Initialization

### Running `devspace init`

From your project root, run:

```shell
devspace init
```

The interactive wizard walks through:

1. **Programming language** — auto-detected or selected (c# dotnet, go, java-gradle, java-maven, javascript, php, python)
2. **Deployment method** — `helm`, `kubectl`, or `kustomize`
3. **Quickstart project?** — confirms whether the project is a DevSpace quickstart project
4. **Development mode** — "develop this project" (source code monitoring) or "deploy only"
5. **Dockerfile** — use existing `./Dockerfile`, specify a different one, use an alternative build tool (e.g. jib, bazel), or skip
6. **Container registry** — skip for local development, or select Docker Hub, GitHub registry, or custom

On completion, DevSpace creates three changes:
- `devspace.yaml` — the declarative config for building, deploying, and developing
- `devspace_start.sh` — startup script shown when the dev container terminal opens
- `.devspace/` added to `.gitignore` (local cache, not committed)

### Scaffolded `devspace.yaml`

A typical initialized config:

```yaml
version: v2beta1
name: my-project

pipelines:
  dev:
    run: |-
      run_dependencies --all
      create_deployments --all
      start_dev app
  deploy:
    run: |-
      run_dependencies --all
      build_images --all -t $(git describe --always)
      create_deployments --all

images:
  app:
    image: ghcr.io/org/app
    dockerfile: ./Dockerfile

deployments:
  app:
    helm:
      chart:
        name: component-chart
        repo: https://charts.devspace.sh
      values:
        containers:
          - image: app
        service:
          ports:
            - port: 8080

dev:
  app:
    imageSelector: ghcr.io/org/app
    devImage: ghcr.io/loft-sh/devspace-containers/go:1.18-alpine
    ports:
      - port: "8080"
    terminal:
      command: ./devspace_start.sh
    sync:
      - path: ./
```

## Pitfalls

- **Project name uniqueness**: DevSpace does not allow multiple active projects with the same name in the same namespace. If you see a conflict, change the `name` field in `devspace.yaml`.
- **`.devspace/` directory**: Do not commit this to version control. It contains machine-local cache data. The `devspace init` wizard adds it to `.gitignore` automatically.
- **VS Code on Alpine**: VS Code Remote-SSH does not support Alpine-based images. Use Debian or Ubuntu-based dev images instead.
