---
title: "Helm Complementary Tools"
status: draft
author: padawont
date: 2026-07-11
tags:
  - kubernetes
  - helm
  - helmfile
  - helm-diff
  - tooling
sources:
  - url: "https://helmfile.readthedocs.io/"
    title: "Helmfile Documentation"
  - url: "https://github.com/databus23/helm-diff"
    title: "helm-diff GitHub Repository"
last_audit_date: 2026-07-11
---

# Helm Complementary Tools

Tools that extend and enhance Helm's capabilities for managing charts at scale.

## Helmfile

[Helmfile](https://helmfile.readthedocs.io/) is a declarative spec for deploying Helm charts. It manages chart repositories, values files, environments, and release ordering in a single `helmfile.yaml`.

### Installation

```bash
# macOS
brew install helmfile

# Linux (binary download)
curl -L https://github.com/helmfile/helmfile/releases/latest/download/helmfile_$(uname -s)_$(uname -m) -o /usr/local/bin/helmfile
chmod +x /usr/local/bin/helmfile
```

### helmfile.yaml Structure

```yaml
# Basic helmfile.yaml
repositories:
  - name: bitnami
    url: https://charts.bitnami.com/bitnami

releases:
  - name: nginx
    namespace: default
    chart: bitnami/nginx
    version: 15.0.0
    values:
      - values/nginx-values.yaml
    set:
      - name: replicaCount
        value: 3
```

### Environments

Define environments for different deployment targets:

```yaml
environments:
  dev:
    values:
      - environments/dev/values.yaml
  staging:
    values:
      - environments/staging/values.yaml
  prod:
    values:
      - environments/prod/values.yaml

releases:
  - name: myapp
    chart: ./charts/myapp
    values:
      - values/common.yaml
      - {{ environmentValues }}

# Use with --environment flag
# helmfile --environment prod apply
```

### Advanced Features

**Release dependencies:**

```yaml
releases:
  - name: postgresql
    chart: bitnami/postgresql
    version: 12.x

  - name: myapp
    chart: ./charts/myapp
    needs:
      - postgresql  # Ensures postgresql deploys first
```

**Conditional releases:**

```yaml
releases:
  - name: metrics-server
    chart: bitnami/metrics-server
    installed: true  # Always install
    labels:
      category: monitoring

  - name: redis
    chart: bitnami/redis
    installed: {{ eq .Environment.Name "prod" | toYaml }}
```

**Defaults:**

```yaml
helmDefaults:
  wait: true
  timeout: 600
  atomic: true
  createNamespace: true
```

### Commands

```bash
# Diff changes before applying
helmfile diff

# Apply (sync) all releases
helmfile apply

# Apply with environment
helmfile --environment prod apply

# Apply specific releases by label
helmfile --selector category=monitoring apply

# Apply specific releases by name
helmfile apply --selector name=nginx

# Sync all releases
helmfile sync

# Destroy all releases
helmfile destroy

# List releases
helmfile list

# Template releases
helmfile template

# Lint helmfile.yaml
helmfile lint

# Build values files
helmfile build
```

### Helmfile vs Helm

| Feature | Helm | Helmfile |
|---|---|---|
| Single chart | Yes | Yes |
| Multiple charts | Manual loop | Declarative |
| Environments | External scripts | Built-in |
| Release ordering | None | `needs:` |
| State management | Individual releases | Release set |
| CI/CD integration | Manual | `helmfile apply` |
| Values layering | Limited | Environment + file + set |

## helm-diff

[helm-diff](https://github.com/databus23/helm-diff) is a Helm plugin that shows the differences between a deployed release and proposed changes.

### Installation

```bash
helm plugin install https://github.com/databus23/helm-diff
```

### Usage

```bash
# Diff upgrade from current release
helm diff upgrade my-release bitnami/nginx

# Diff with custom values
helm diff upgrade my-release bitnami/nginx \
  --values prod-values.yaml \
  --set replicaCount=5

# Diff specific revision
helm diff revision my-release 1 2

# Diff between two different releases
helm diff release my-prod my-stage

# Diff between two revisions of the same release
helm diff revision my-release 3 5

# Context mode (show surrounding lines)
helm diff upgrade my-release bitnami/nginx --context 5

# Show only changes (no unchanged context)
helm diff upgrade my-release bitnami/nginx -C 0
```

### Integration with Helmfile

```bash
# Helmfile uses helm-diff automatically
helmfile diff

# Shows diff for all releases
helmfile --environment prod diff
```

### Use Cases

- **CI/CD preview**: Show what will change before deploying
- **Review**: Validate changes in pull requests
- **Troubleshooting**: Understand drift between revisions
- **Audit**: Document what changed between deployments

## Other Complementary Tools

| Tool | Purpose |
|---|---|
| [Helmsman](https://github.com/Praqma/helmsman) | Declarative Helm chart management with desired state files |
| [ChartMuseum](https://chartmuseum.com/) | Self-hosted Helm chart repository server |
| [Artifact Hub](https://artifacthub.io/) | CNCF-backed chart search and discovery |
| [helm-unittest](https://github.com/helm-unittest/helm-unittest) | Unit test framework for Helm charts |
| [Helm S3](https://github.com/hypnoglow/helm-s3) | S3-backed Helm repository plugin |
| [Helm GCS](https://github.com/viglesiasce/helm-gcs) | Google Cloud Storage-backed Helm repository plugin |

## References

- [Helmfile Documentation](https://helmfile.readthedocs.io/)
- [helm-diff GitHub](https://github.com/databus23/helm-diff)
- [Helm Plugins](https://helm.sh/docs/topics/plugins/)
