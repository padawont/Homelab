---
title: "Helm Chart Structure"
status: draft
author: padawont
date: 2026-07-11
tags:
  - kubernetes
  - helm
  - chart-structure
  - packaging
sources:
  - url: "https://helm.sh/docs/topics/charts/"
    title: "Helm Chart Structure — Helm Documentation"
  - url: "https://helm.sh/docs/helm/helm_create/"
    title: "helm create — Helm Documentation"
last_audit_date: 2026-07-11
---

# Helm Chart Structure

A Helm chart is a collection of files that describe a related set of Kubernetes resources. A chart is created as a directory tree with a well-defined structure.

## Directory Layout

```
mychart/
├── Chart.yaml              # Chart metadata (required)
├── values.yaml             # Default configuration values (required)
├── values.schema.json      # Optional JSON Schema for values validation
├── charts/                 # Subchart dependencies
│   └── mychart-subchart-0.1.0.tgz
├── crds/                   # Custom Resource Definitions
│   └── my-crd.yaml
├── templates/              # Kubernetes manifest templates (required)
│   ├── NOTES.txt           # Post-install help text (optional)
│   ├── _helpers.tpl        # Named template definitions
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── serviceaccount.yaml
│   └── tests/
│       └── test-connection.yaml
└── .helmignore             # File patterns to exclude from packaging
```

## Chart.yaml

The chart metadata file. Required fields and common optional fields:

```yaml
apiVersion: v2            # v2 for Helm 3+, v1 deprecated
name: mychart             # Chart name
description: A Helm chart for Kubernetes
version: 0.1.0            # Chart version (semver 2)
appVersion: "1.16.0"      # Application version being packaged
type: application         # application or library
keywords:
  - web
  - nginx
maintainers:
  - name: The Maintainer
    email: maintainer@example.com
dependencies:
  - name: postgresql
    version: ">=10.0.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
    tags:
      - database
icon: https://example.com/icon.png
```

### Chart Types

- **application** — Standard chart for deployable applications (default)
- **library** — Chart providing helpers/functions only, no resources

### Version Constraints

Dependencies use semver constraints:

| Constraint | Meaning |
|---|---|
| `>=1.2.3` | Greater than or equal |
| `<1.2.3` | Less than |
| `>1.2.3` | Greater than |
| `=1.2.3` | Exactly |
| `!=1.2.3` | Not equal |
| `~1.2.3` | Compatible (patch-level) |
| `^1.2.3` | Compatible (minor-level) |

## values.yaml

Default configuration values. Users override these at install/upgrade time.

```yaml
# Scalar values
replicaCount: 3
image:
  repository: nginx
  tag: "1.25.0"
  pullPolicy: IfNotPresent

# String values (explicit)
service:
  name: web
  type: ClusterIP
  port: 80

# Boolean
autoscaling:
  enabled: false

# Nested objects
ingress:
  enabled: true
  host: myapp.example.com
  tls: true

# Lists
ports:
  - name: http
    containerPort: 80
  - name: https
    containerPort: 443

# Template reference values
nameOverride: ""
fullnameOverride: ""

# Global values (accessible from subcharts)
global:
  environment: production
  imagePullSecrets:
    - name: regcred
```

## values.schema.json

Optional JSON Schema that validates user-supplied values at install/upgrade time. See [values-customization.md](values-customization.md#json-schema) for schema examples and validation patterns.

## templates/

Contains Go template files that render to Kubernetes manifests. Each file becomes a valid YAML document. Files prefixed with `_` are not rendered as standalone documents (they exist for inclusion via named templates). See [templating.md](templating.md) for templating syntax, functions, and directives, and [values-customization.md](values-customization.md) for overriding values at install/upgrade time.

### NOTES.txt

A free-text template rendered after install/upgrade. Shown to the user:

```text
Thank you for installing {{ .Chart.Name }}.

Release: {{ .Release.Name }}
Namespace: {{ .Release.Namespace }}
Chart version: {{ .Chart.Version }}
Application version: {{ .Chart.AppVersion }}

Get the application URL by running these commands:
  export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "mychart.fullname" . }})
  export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT
```

## _helpers.tpl

Named template definitions shared across templates. Convention: prefix names with the chart name. See [templating.md](templating.md#named-templates) for full documentation on named templates, `define`, `include`, and `template` directives.

## charts/

Dependencies as packaged `.tgz` files or unpacked subchart directories. Managed by `helm dependency update`.

## crds/

Custom Resource Definitions installed before template rendering. CRDs are installed only once per cluster (not per release). CRD files must not contain `{{ template }}` directives — they are installed before template rendering.

## .helmignore

Same semantics as `.dockerignore` — excludes files from `helm package`:

```
.git
.gitignore
*.md
*.tgz
.DS_Store
```

## Chart Packaging

Charts are packaged as versioned `.tgz` archives:

```bash
cd chart-dir/
helm package .
# Creates mychart-0.1.0.tgz
```

## References

- [Helm Chart Structure — Official Docs](https://helm.sh/docs/topics/charts/)
- [Chart Best Practices Guide](https://helm.sh/docs/chart_best_practices/)
