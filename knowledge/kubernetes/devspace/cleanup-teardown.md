---
title: "DevSpace Cleanup & Teardown"
status: draft
author: padawont
date: 2026-07-13
tags:
  - devspace
  - cleanup
  - teardown
  - kubernetes
sources:
  - url: "https://www.devspace.sh/docs/getting-started/cleanup"
    title: "Cleanup — Official Docs"
last_audit_date: 2026-07-13
---

# DevSpace Cleanup & Teardown

DevSpace provides several commands to clean up resources, both in-cluster and locally.

## Reset Dev Container

Reverse changes made by the `start_dev` pipeline command. This reverts container image swaps (restoring the original production image), stops file sync, terminates port forwarding, and closes terminal sessions:

```shell
devspace reset pods
```

This is useful when you want to exit dev mode without removing the deployed application. The pod is restored to its original (non-dev) state — the deployment itself remains intact and continues running.

### `devspace reset pods` vs `devspace purge`

| Scenario | Command |
|---|---|
| You finished coding but want the app to keep running | `devspace reset pods` |
| You want to tear down everything DevSpace deployed | `devspace purge` |
| You want to stop sync/forwarding but leave the pod in dev mode | Exit `devspace dev` with Ctrl+C (sync stops, pod unchanged) |

## Purge Project From Cluster

Remove all deployments created by DevSpace from the cluster:

```shell
devspace purge
```

This executes the `purge` pipeline — see [core-workflows.md](core-workflows.md) for the default pipeline overview and [architecture-pipeline-model.md](architecture-pipeline-model.md) for the full pipeline reference. The default purge flow:

```yaml
pipelines:
  purge:
    run: |-
      stop_dev --all
      purge_deployments --all
      run_dependencies --all --pipeline purge
```

This stops all dev modes, purges all deployments, and recursively purges dependencies.

## Reset Variables

If you provided variable values during configuration (via `--var` or interactive prompts), the cached values can be reset:

```shell
devspace reset vars
```

After running this, DevSpace will re-prompt for variable values on the next run.

## Cleanup Images

When building images with DevSpace (e.g., via `devspace build`), many tagged images accumulate in the local Docker daemon. Clean them up:

```shell
devspace cleanup images
```

## Cleanup Local Registry

If a local registry was used for pushing images to the cluster (common with local Kubernetes clusters like kind or k3d), clean it up:

```shell
devspace cleanup local-registry
```

## Cleanup Table

| Command | What It Does | When To Use |
|---|---|---|
| `devspace reset pods` | Reverts dev mode changes on pods (image swap, command override) | After `devspace dev` — when you want to exit dev mode but keep the app running |
| `devspace purge` | Removes all DevSpace-created deployments from the cluster | To fully tear down the project |
| `devspace reset vars` | Clears cached variable values | When configuration changes require fresh variable input |
| `devspace cleanup images` | Removes locally built Docker images | When local disk is cluttered with dev tags |
| `devspace cleanup local-registry` | Cleans up local container registry | After using local registry for in-cluster image pushing |

## Pitfalls

- **`purge` removes everything**: There is no "undo" for `devspace purge`. If you only want to stop development but keep the application running, use `devspace reset pods` instead.
- **Dependency purge**: The default `purge` pipeline calls `run_dependencies --all --pipeline purge`. Be aware that this can remove deployments from dependent DevSpace projects.
- **Image cleanup is local only**: `devspace cleanup images` only affects your local Docker daemon. It does not remove images pushed to remote registries. Use your registry's own cleanup policies for that.
- **Namespace**: `purge` does not delete the namespace itself — only the resources DevSpace created within it. If you want to remove the namespace entirely, use `kubectl delete namespace <name>`.
