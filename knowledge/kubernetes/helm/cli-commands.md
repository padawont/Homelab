---
title: "Common Helm CLI Commands"
status: draft
author: padawont
date: 2026-07-11
tags:
  - kubernetes
  - helm
  - cli
  - commands
sources:
  - url: "https://helm.sh/docs/helm/helm/"
    title: "Helm CLI Reference — Helm Documentation"
  - url: "https://helm.sh/docs/intro/using_helm/"
    title: "Using Helm — Helm Documentation"
last_audit_date: 2026-07-11
---

# Common Helm CLI Commands

> These commands and flags target **Helm 4**. Some flags differ from Helm 3 (e.g. `--force-replace` replaced `--force`; `--dry-run` accepts enum values).

## helm install

Install a chart, creating a new release.

```bash
# Basic install from a repo
helm install my-release bitnami/nginx

# Install with custom values file
helm install my-release bitnami/nginx --values custom-values.yaml

# Install with --set flags
helm install my-release bitnami/nginx \
  --set replicaCount=5 \
  --set service.type=LoadBalancer

# Install with atomic mode (rollback on failure)
helm install my-release bitnami/nginx \
  --atomic \
  --wait \
  --timeout 5m

# Install from a local chart directory
helm install my-release ./mychart

# Install from a packaged chart
helm install my-release ./mychart-0.1.0.tgz

# Dry run — render templates without installing
helm install my-release bitnami/nginx --dry-run --debug

# Generate a name automatically
helm install bitnami/nginx --generate-name
```

### Install Flags

| Flag | Description |
|---|---|
| `--values`, `-f` | Specify values file (can be used multiple times) |
| `--set` | Override a single value |
| `--set-string` | Override a value as string |
| `--set-file` | Inject file content as a value |
| `--set-json` | Set value from JSON expression |
| `--set-literal` | Set a literal string value (no type inference) |
| `--atomic` | Automatically rollback if install fails |
| `--wait` | Wait for resources to be ready |
| `--timeout` | Time to wait (default 5m) |
| `--dry-run` | Simulate install (none|client|server), output rendered templates |
| `--debug` | Enable verbose output |
| `--create-namespace` | Create release namespace if it does not exist |
| `--description` | Add a description to the release |
| `--name-template` | Template for release name with --generate-name |

## helm upgrade

Upgrade an existing release to a new chart version or configuration.

```bash
# Basic upgrade
helm upgrade my-release bitnami/nginx

# Upgrade with new values
helm upgrade my-release bitnami/nginx --values new-values.yaml

# --install: install if release does not exist (upsert)
helm upgrade --install my-release bitnami/nginx

# Atomic upgrade with rollback on failure
helm upgrade --install my-release bitnami/nginx \
  --values prod-values.yaml \
  --atomic \
  --wait \
  --timeout 10m \
  --cleanup-on-fail

# Reuse previous values (merge with --values)
helm upgrade my-release bitnami/nginx --reuse-values

# Reset to default values
helm upgrade my-release bitnami/nginx --reset-values

# Force replace resources (deletes + recreates)
helm upgrade my-release bitnami/nginx --force-replace
```

### Upgrade Flags

| Flag | Description |
|---|---|
| `--install` | Install if release does not exist |
| `--reuse-values` | Reuse last release's values |
| `--reset-values` | Reset to chart defaults before merging |
| `--set-json` | Set value from JSON expression |
| `--set-literal` | Set a literal string value (no type inference) |
| `--force-replace` | Force resource replacement |
| `--atomic` | Rollback on failure |
| `--cleanup-on-fail` | Delete resources created during upgrade on failure |
| `--wait` | Wait for resources to be ready |
| `--timeout` | Time to wait |
| `--dry-run` | Simulate upgrade |

### Values Precedence

See [values-customization.md](values-customization.md#values-precedence-highest-to-lowest) for the full precedence order and override patterns.

## helm rollback

Roll back a release to a previous revision.

```bash
# Rollback to revision 1
helm rollback my-release 1

# Rollback with flags
helm rollback my-release 3 \
  --wait \
  --timeout 5m \
  --cleanup-on-fail

# Dry run
helm rollback my-release 1 --dry-run
```

### Rollback Flags

| Flag | Description |
|---|---|
| `--wait` | Wait for resources to be ready |
| `--cleanup-on-fail` | Clean up resources if rollback fails |

## helm uninstall

Delete a release and its resources.

```bash
# Uninstall release
helm uninstall my-release

# Keep history (allows rollback to pre-uninstall revision)
helm uninstall my-release --keep-history

# Dry run
helm uninstall my-release --dry-run

# Prevent hooks from running during uninstallation
helm uninstall my-release --no-hooks
```

## helm list

List deployed releases.

```bash
# List all releases in current namespace
helm list

# List all namespaces
helm list --all-namespaces

# List all releases including uninstalled (with --keep-history)
helm list --all

# List deployed only (default)
helm list --deployed

# List pending releases
helm list --pending

# List failed releases
helm list --failed

# List uninstalled releases
helm list --uninstalled

# List superseded releases
helm list --superseded

# Show max results
helm list --max 50

# Output as JSON
helm list --output json

# Output as YAML
helm list --output yaml

# Filter by name
helm list --filter "my-release"

# Reverse sort
helm list --reverse

# Sort by release date
helm list --date
helm list -d
```

## helm get

Retrieve information about a release.

```bash
# Get rendered values (merged --values + --set)
helm get values my-release

# Get all values including computed defaults
helm get values my-release --all

# Get values from a specific revision
helm get values my-release --revision 3

# Get rendered manifests (Kubernetes YAML)
helm get manifest my-release

# Get NOTES.txt output
helm get notes my-release

# Get hooks
helm get hooks my-release

# Get metadata
helm get metadata my-release
```

## helm history

Show release revision history.

```bash
# Show history
helm history my-release

# Show max revisions
helm history my-release --max 20

# Output as JSON
helm history my-release --output json
```

## helm create

Scaffold a new chart directory.

```bash
helm create mychart
# Creates: mychart/Chart.yaml, values.yaml, templates/, templates/tests/, charts/, .helmignore
```

## helm lint

Validate chart for issues.

```bash
# Lint chart directory
helm lint ./mychart

# Lint with strict mode (warnings become errors)
helm lint ./mychart --strict

# Lint with values file
helm lint ./mychart --values test-values.yaml

# Suppress non-error messages
helm lint ./mychart --quiet
```

## helm dependency

Manage chart dependencies.

```bash
# Update dependencies from Chart.yaml
helm dependency update ./mychart

# Build dependencies (reuse lock file, do not fetch)
helm dependency build ./mychart

# List dependencies
helm dependency list ./mychart
```

## helm template

Render templates locally without installing:

```bash
helm template my-release ./mychart \
  --values prod-values.yaml \
  --set replicaCount=5

# Output to file
helm template my-release ./mychart > rendered.yaml

# Include CRDs
helm template my-release ./mychart --include-crds

# Validate against cluster (server-side dry run)
helm template my-release ./mychart --dry-run server
```

## helm show

Inspect chart information:

```bash
helm show chart ./mychart
helm show values ./mychart
helm show readme ./mychart
helm show crds ./mychart
helm show all ./mychart
```

## References

- [Helm CLI Reference](https://helm.sh/docs/helm/helm/)
- [Using Helm](https://helm.sh/docs/intro/using_helm/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
