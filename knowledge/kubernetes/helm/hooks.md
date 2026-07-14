---
title: "Helm Hooks"
status: draft
author: padawont
date: 2026-07-11
tags:
  - kubernetes
  - helm
  - hooks
  - lifecycle
sources:
  - url: "https://helm.sh/docs/topics/charts_hooks/"
    title: "Helm Hooks — Helm Documentation"
  - url: "https://helm.sh/docs/topics/charts_hooks/#hook-weights"
    title: "Hook Weights — Helm Documentation"
last_audit_date: 2026-07-11
---

# Helm Hooks

Helm hooks allow chart authors to run specific resources at specific points in a release lifecycle. Hooks behave like regular Kubernetes resources but are annotated to define when they execute. See [templating.md](templating.md#named-templates) for the `{{ include }}` and `{{ template }}` directives used in hook annotations.

## Hook Types

| Hook | When It Runs | Common Use Case |
|---|---|---|
| `pre-install` | After templates are rendered, before resources are created | Create ConfigMaps, Secrets, RBAC |
| `post-install` | After all resources are installed | Database migrations, notification |
| `pre-upgrade` | After templates are rendered, before resources are updated | Backup existing data |
| `post-upgrade` | After all resources are upgraded | Health check, notification |
| `pre-rollback` | After templates are rendered, before resources are rolled back | Pre-rollback validation |
| `post-rollback` | After all resources are rolled back | Post-rollback cleanup |
| `pre-delete` | Before deletion of resources | Graceful shutdown |
| `post-delete` | After all resources are deleted | Cleanup external resources |
| `test` | When `helm test` is run | Smoke tests, validation |

## Defining a Hook

Annotate a resource with `helm.sh/hook`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "mychart.fullname" . }}-db-migrate
  annotations:
    "helm.sh/hook": post-install,post-upgrade
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: myapp:latest
          command: ["/bin/sh", "-c", "npm run migrate"]
```

## Hook Execution Order

Hooks are executed in the following order within a lifecycle phase:

1. **Sorted by weight** (ascending, negative to positive)
2. **Same weight** — sorted by resource kind, then name (alphabetical)
3. **Same weight and kind** — sorted by name

```yaml
# Runs first (weight -5)
annotations:
  "helm.sh/hook": pre-install
  "helm.sh/hook-weight": "-5"

# Runs second (weight 0)
annotations:
  "helm.sh/hook": pre-install
  "helm.sh/hook-weight": "0"

# Runs last (weight 5)
annotations:
  "helm.sh/hook": pre-install
  "helm.sh/hook-weight": "5"
```

### Weight Defaults

- If `helm.sh/hook-weight` is not specified, it defaults to `0`.
- Negative weights run before weight 0. Positive weights run after.

## Hook Deletion Policies

Control when hook resources are deleted. Multiple policies can be combined:

| Policy | Behavior |
|---|---|
| `before-hook-creation` | Delete existing hook resource before creating new one (default) |
| `hook-succeeded` | Delete hook resource after it succeeds |
| `hook-failed` | Delete hook resource after it fails |

```yaml
annotations:
  "helm.sh/hook-delete-policy": "before-hook-creation,hook-succeeded"
```

### Default Behavior

If no `helm.sh/hook-delete-policy` annotation is set, the default is `before-hook-creation`. This means:
- On first install, the hook resource persists after running
- On subsequent upgrade, the old hook resource is deleted before the new one is created
- You must manually clean up leftover hook resources if you want to remove them

### Common Patterns

```yaml
# Clean up after success (for Jobs that should not persist)
annotations:
  "helm.sh/hook": post-install
  "helm.sh/hook-delete-policy": hook-succeeded

# Always clean up before re-running
annotations:
  "helm.sh/hook": pre-upgrade
  "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded

# Keep for debugging on failure
annotations:
  "helm.sh/hook": post-install
  "helm.sh/hook-delete-policy": hook-succeeded
  # Hook resource persists if it fails (for inspection)
```

## Hook Lifecycle

### Install Lifecycle

```
1. Helm renders templates
2. Pre-install hooks (sorted by weight)
   2a. Delete existing hook resources (before-hook-creation)
   2b. Create hook resources
   2c. Wait for hook resources to complete (Jobs/Pods)
3. Install release resources
4. Post-install hooks (sorted by weight)
   4a. Delete existing hook resources
   4b. Create hook resources
   4c. Wait for hook resources to complete
5. Release marked as deployed
```

### Upgrade Lifecycle

```
1. Helm renders templates
2. Pre-upgrade hooks (sorted by weight)
3. Upgrade release resources
4. Post-upgrade hooks (sorted by weight)
5. Release marked as deployed
```

## Hook Resources

Hooks work with any Kubernetes resource type, but most commonly:

| Resource Type | Why |
|---|---|
| `Job` | Run one-off tasks (migrations, setup, cleanup) |
| `Pod` | Simple one-shot operations |
| `ConfigMap` / `Secret` | Generate configuration before install |
| `ServiceAccount` | Create temp credentials for hook jobs |
| `CustomResourceDefinition` | Install CRDs before resources that use them |

### Hook Jobs

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "mychart.fullname" . }}-init
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: init
          image: alpine:3.18
          command: ["/bin/sh", "-c"]
          args:
            - |
              echo "Initializing database..."
              # Initialize logic here
```

### Hook Pods

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: {{ include "mychart.fullname" . }}-test
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
    - name: test
      image: alpine:3.18
      command: ["/bin/sh", "-c"]
      args:
        - |
          echo "Running tests..."
          # Test logic here
```

## Hook Resources Are Not Managed

Hook resources are **not managed** by Helm in the same way as regular resources:
- They are not part of the release manifest
- They are not automatically upgraded or rolled back
- They must be cleaned up via `helm.sh/hook-delete-policy`

### Impact on Rollback

When a rollback occurs:
- Regular resources roll back to the previous revision
- Hook resources from the rolled-back revision are NOT automatically recreated
- Only hooks that were part of the rollback operation itself run (pre/post-rollback)

## Hooks vs Subcharts

Hooks in subcharts execute at the same lifecycle points as parent chart hooks:
- Parent pre-install hooks and subchart pre-install hooks both run before install
- Within the same hook type and weight, execution order between parent and subchart is not guaranteed

## Testing with Hooks

The `test` hook type runs with `helm test`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: {{ include "mychart.fullname" . }}-connection-test
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
    - name: test
      image: alpine:3.18
      command: ["/bin/sh", "-c"]
      args:
        - |
          wget -qO- http://{{ include "mychart.fullname" . }}:{{ .Values.service.port }}
```

```bash
# Run tests
helm test my-release

# Run tests with cleanup
helm test my-release --logs

# Run tests with timeout
helm test my-release --timeout 5m
```

## References

- [Helm Hooks Documentation](https://helm.sh/docs/topics/charts_hooks/)
- [Helm Test](https://helm.sh/docs/helm/helm_test/)
