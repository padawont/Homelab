---
title: "Helm Values Customization"
status: draft
author: padawont
date: 2026-07-11
tags:
  - kubernetes
  - helm
  - values
  - configuration
  - override
sources:
  - url: "https://helm.sh/docs/chart_template_guide/values_files/"
    title: "Values Files — Helm Documentation"
  - url: "https://helm.sh/docs/intro/using_helm/#customizing-the-chart-before-installing"
    title: "Customizing the Chart Before Installing — Helm Documentation"
last_audit_date: 2026-07-11
---

# Helm Values Customization

Helm charts provide default values in `values.yaml`. Users customize these values at install/upgrade time using `--values`, `--set`, `--set-string`, and `--set-file`.

## --values / -f

Specify one or more YAML files with override values:

```bash
# Single values file
helm install my-release bitnami/nginx --values prod-values.yaml

# Multiple values files (later files merge into earlier)
helm install my-release bitnami/nginx \
  --values common-values.yaml \
  --values env-values.yaml \
  --values secrets-values.yaml

# Shorthand
helm install my-release bitnami/nginx -f prod-values.yaml
```

### Multi-File Merge Precedence

When multiple `--values` files are specified, later files take precedence over earlier ones:

```yaml
# common-values.yaml
replicaCount: 3
service:
  type: ClusterIP
  port: 80

# env-values.yaml
replicaCount: 5
service:
  type: LoadBalancer

# Merge result:
# replicaCount: 5
# service.type: LoadBalancer
# service.port: 80
```

## --set

Override individual values directly on the command line:

```bash
# Simple key-value
helm install my-release bitnami/nginx --set replicaCount=3

# Nested key with dot notation
helm install my-release bitnami/nginx \
  --set service.type=LoadBalancer \
  --set service.port=443

# Multiple values in one --set (comma-separated)
helm install my-release bitnami/nginx \
  --set replicaCount=3,service.type=LoadBalancer

# Lists with braces
helm install my-release bitnami/nginx \
  --set "ports[0].name=http,ports[0].containerPort=80" \
  --set "ports[1].name=https,ports[1].containerPort=443"

# Array values
helm install my-release bitnami/nginx \
  --set "hosts={example.com,api.example.com}"

# Nested objects with dot notation (preferred)
helm install my-release bitnami/nginx \
  --set resources.requests.cpu=100m,resources.requests.memory=128Mi
```

## --set-string

Force values to be treated as strings (prevents type coercion):

```bash
# Without --set-string: size=1024 becomes integer 1024
# With --set-string: size="1024" stays string "1024"
helm install my-release bitnami/nginx \
  --set-string size=1024 \
  --set-string version=1.25.0

# Useful for config values that must be strings
helm install my-release bitnami/nginx \
  --set-string service.type=LoadBalancer
```

## --set-json

Set values from a JSON expression:

```bash
helm install my-release bitnami/nginx \
  --set-json 'replicaCount=5' \
  --set-json 'resources={"requests":{"cpu":"100m","memory":"128Mi"}}'
```

## --set-literal

Set a literal string value without type inference or escape sequence processing. Unlike `--set-string`, characters like `\n`, `\t`, `\\` are passed through as-is rather than interpreted:

```bash
helm install my-release bitnami/nginx \
  --set-literal version=1.25.0
```

## --set-file

Inject file content as a value. Reads the file and uses its contents as the value:

```bash
# Inject TLS certificate as a value
helm install my-release bitnami/nginx \
  --set-file tls.crt=tls.cert \
  --set-file tls.key=tls.key

# Inject Docker config
helm install my-release bitnami/nginx \
  --set-file dockerconfigjson=.docker/config.json

# Inject multi-line values
helm install my-release bitnami/nginx \
  --set-file config.custom=./custom-config.cfg
```

## Values Precedence (Highest to Lowest)

1. `--set` / `--set-string` / `--set-json` / `--set-literal` / `--set-file` (highest)
2. `--values` files (later files over earlier)
3. Chart's `values.yaml` (base defaults, lowest)

```bash
# Final precedence example
helm upgrade --install my-release bitnami/nginx \
  --values common-values.yaml \    # Layer 1 (overrides chart defaults)
  --values prod-values.yaml \      # Layer 2 (overrides common)
  --set replicaCount=5 \           # Layer 3 (overrides prod)
  --set-string version=1.25.0      # Layer 3 (same priority as --set)
```

## Values File Patterns

### Environment-Specific Files

```
helm/
├── values.yaml              # Base defaults
├── values-dev.yaml          # Development overrides
├── values-staging.yaml      # Staging overrides
└── values-prod.yaml         # Production overrides
```

```bash
helm upgrade --install my-release ./mychart \
  --values values.yaml \
  --values values-prod.yaml
```

### Layered Override Pattern

```
values.yaml           → global defaults
region-values.yaml    → region-specific (us-east vs eu-west)
env-values.yaml       → environment-specific (dev/staging/prod)
secrets-values.yaml   → encrypted secrets (not committed)
```

```bash
helm upgrade --install my-release ./mychart \
  --values values.yaml \
  --values region-values.yaml \
  --values env-values.yaml \
  --values secrets-values.yaml \
  --set replicaCount=5
```

## Supplied Values vs Computed Values

When inspecting what values a release actually uses:

```bash
# Show only user-supplied overrides
helm get values my-release

# Show all values (defaults + overrides merged)
helm get values my-release --all

# Show values from specific revision
helm get values my-release --revision 3
```

## Values Validation

### JSON Schema

Charts can include `values.schema.json` to validate values at install/upgrade time:

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100
    },
    "image": {
      "type": "object",
      "properties": {
        "tag": {
          "type": "string",
          "pattern": "^[a-zA-Z0-9._-]+$"
        }
      }
    }
  },
  "required": ["replicaCount"]
}
```

### Template-Level Validation

See [templating.md](templating.md#template-level-functions) for template-level validation using `required` and `fail`.

## Global Values

Global values are accessible from all subcharts in a dependency tree:

```yaml
# Parent chart values.yaml
global:
  imageRegistry: internal-registry:5000
  imagePullSecrets:
    - name: regcred
  environment: production
```

```yaml
# Accessible in subcharts as .Values.global.imageRegistry
# Values override priority: subchart --set > global value > subchart values.yaml
```

## Values Type Handling

| Type | YAML Example | CLI --set | Notes |
|---|---|---|---|
| String | `name: "nginx"` | `--set name=nginx` | Quotes optional for simple strings |
| Integer | `count: 3` | `--set count=3` | No quotes |
| Float | `cpu: 0.5` | `--set cpu=0.5` | |
| Boolean | `enabled: true` | `--set enabled=true` | Use --set-string if you need "true" as string |
| Null | `config: null` | `--set config=null` | |
| List | `ports: [80, 443]` | `--set "ports={80,443}"` | |
| Object | `resources: {limits: {cpu: 1}}` | `--set resources.limits.cpu=1` | Dot notation for nested |

## References

- [Helm Values Files](https://helm.sh/docs/chart_template_guide/values_files/)
- [Customizing the Chart Before Installing](https://helm.sh/docs/intro/using_helm/#customizing-the-chart-before-installing)
- [Helm Best Practices — Values](https://helm.sh/docs/chart_best_practices/values/)
