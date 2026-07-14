# DevSpace

Reference notes on [DevSpace](https://www.devspace.sh/) — an open-source, client-only developer tool for Kubernetes by Loft Labs. These notes cover installation, configuration (`devspace.yaml`), core workflows (`devspace dev`, `devspace deploy`), development features (file sync, hot reload, port forwarding), and cleanup procedures.

Prerequisites: A Kubernetes cluster (local or remote) with a valid kube-context, and [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl). See the [Kubernetes](../) notes for prerequisite concepts (Pods, Deployments, Services, ConfigMaps, RBAC).

## Getting Started

| File | Description |
|---|---|
| [installation-config.md](installation-config.md) | Install DevSpace via brew, curl, scoop, or VS Code extension; initialize a project with `devspace init`; understand the scaffolded `devspace.yaml` |
| [core-workflows.md](core-workflows.md) | `devspace dev` and `devspace deploy` — pipeline execution, port forwarding, DevSpace UI, cluster and namespace selection |

## Configuration

| File | Description |
|---|---|
| [architecture-pipeline-model.md](architecture-pipeline-model.md) | `devspace.yaml` schema (version, name, imports, functions, pipelines, images, deployments, dev, profiles, variables); pipeline lifecycle and profile composition |

## Development Features

| File | Description |
|---|---|
| [file-sync-hot-reload.md](file-sync-hot-reload.md) | Bi-directional file sync, sync path mappings, exclude patterns, initial sync strategies, `onUpload` exec/restartContainer, polling vs inotify, bandwidth limits, port forwarding and reverse port forwarding |

## DevBox Integration

| File | Description |
|---|---|
| [integration-with-devbox.md](integration-with-devbox.md) | How DevBox and DevSpace compose together — toolchain provisioning, shell_hook automation, architecture diagram |
| [combined-workflow.md](combined-workflow.md) | Runnable end-to-end workflow from repo clone to live development: `devbox shell → devspace dev` |

## Cleanup

| File | Description |
|---|---|
| [cleanup-teardown.md](cleanup-teardown.md) | `devspace purge`, `devspace reset pods`, `devspace reset vars`, `devspace cleanup images`, `devspace cleanup local-registry` |
