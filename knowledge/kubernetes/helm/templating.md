---
title: "Helm Templating"
status: draft
author: padawont
date: 2026-07-11
tags:
  - kubernetes
  - helm
  - templating
  - go-templates
  - sprig
sources:
  - url: "https://helm.sh/docs/chart_template_guide/"
    title: "Chart Template Guide — Helm Documentation"
  - url: "https://masterminds.github.io/sprig/"
    title: "Sprig Function Documentation"
last_audit_date: 2026-07-11
---

# Helm Templating

Helm uses Go templates extended with Sprig functions to generate Kubernetes manifests. Templates live in the `templates/` directory and are rendered with values from `values.yaml`, `--set`, and `--values` flags.

## Template Syntax

### Delimiters

| Delimiter | Purpose |
|---|---|
| `{{ }}` | Template directive |
| `{{- ` | Trim whitespace before |
| ` -}}` | Trim whitespace after |
| `{{- -}}` | Trim both sides |
| `{{/* comment */}}` | Template comment (not rendered) |

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.service.name | default "web" | quote }}
  labels:
    app: {{ .Chart.Name }}
    release: {{ .Release.Name }}
```

### Whitespace Chomping

```yaml
# Without chomping — adds newline
containers:
  - name: {{ .Values.name }}

# With chomping — removes whitespace on both sides
containers:
  - name: {{- .Values.name -}}
```

## Built-in Objects

| Object | Description |
|---|---|
| `.Values` | User-supplied values from values.yaml, --values, --set |
| `.Chart` | Chart metadata from Chart.yaml |
| `.Release` | Release metadata (Name, Namespace, Service, Revision, IsInstall, IsUpgrade) |
| `.Files` | Access to chart files (not templates) |
| `.Capabilities` | Kubernetes cluster capabilities (APIVersions, KubeVersion) |
| `.Template` | Template metadata (Name, BasePath) |
| `.Subcharts` | Access to subchart scopes (.Values, .Charts, .Releases) |

### Common Built-in Patterns

```yaml
# Release info
metadata:
  name: {{ .Release.Name }}-{{ .Chart.Name }}
  namespace: {{ .Release.Namespace }}
  labels:
    heritage: {{ .Release.Service }}
    revision: "{{ .Release.Revision }}"

# Chart info
  annotations:
    chart-version: {{ .Chart.Version }}
    app-version: {{ .Chart.AppVersion | quote }}

# Conditional at install vs upgrade
{{- if .Release.IsInstall }}
  annotations:
    "helm.sh/hook": post-install
{{- end }}
```

## Flow Control

### if/else

```yaml
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: {{ .Values.autoscaling.minReplicas }}
{{- else }}
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: {{ .Values.replicaCount | default 1 }}
{{- end }}
```

### range

Iterate over lists and maps:

```yaml
# Iterate over list of ports
ports:
{{- range .Values.ports }}
  - name: {{ .name }}
    containerPort: {{ .containerPort }}
    protocol: TCP
{{- end }}

# Iterate over map (key-value)
{{- range $key, $value := .Values.labels }}
  {{ $key }}: {{ $value | quote }}
{{- end }}

# Iterate with index
{{- range $index, $port := .Values.ports }}
  - name: port-{{ $index }}
    port: {{ $port }}
{{- end }}

# Empty check with range
{{- range .Values.items }}
{{- else }}
  # .Values.items is empty
  items: []
{{- end }}
```

### with

Set scope (dot) to a specific object, reducing repetition:

```yaml
{{- with .Values.service }}
apiVersion: v1
kind: Service
spec:
  type: {{ .type | default "ClusterIP" }}
  ports:
    - port: {{ .port }}
      targetPort: {{ .targetPort | default .port }}
  {{- if .loadBalancerIP }}
  loadBalancerIP: {{ .loadBalancerIP }}
  {{- end }}
{{- end }}
```

## Variables

Variables capture values for reuse within a template:

```yaml
{{- $replicaCount := .Values.replicaCount | default 1 }}
{{- $fullName := include "mychart.fullname" . }}

apiVersion: apps/v1
kind: Deployment
spec:
  replicas: {{ $replicaCount }}
  selector:
    matchLabels:
      app: {{ $fullName }}
```

### Scope and Root Access

`with` and `range` change the current scope (`.`). Use `$` to access root scope:

```yaml
{{- with .Values.database }}
apiVersion: v1
kind: ConfigMap
data:
  host: {{ .host }}           # .Values.database.host
  port: {{ $.Values.global.port }}  # root scope access
{{- end }}
```

### Global Values

Global values are accessible from subcharts and parent charts:

```yaml
# In parent chart's values.yaml
global:
  imageRegistry: docker.io/mirror
  imagePullSecrets:
    - name: regcred
```

```yaml
# Accessed anywhere in any chart
image: {{ .Values.global.imageRegistry }}/{{ .Values.image.repository }}
```

## Named Templates

Defined in files prefixed with `_` (commonly `_helpers.tpl`).

### Define

```yaml
{{- define "mychart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "mychart.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "mychart.labels" -}}
helm.sh/chart: {{ include "mychart.name" . }}-{{ .Chart.Version | replace "+" "_" }}
{{ include "mychart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
```

### Include vs Template

| Directive | Returns | Used For |
|---|---|---|
| `template` | String output | Simple includes (cannot pipe) |
| `include` | String value | Can pipe to other functions |

```yaml
# template — direct inclusion
{{- template "mychart.fullname" . }}

# include — piped result
name: {{ include "mychart.fullname" . | trunc 63 | quote }}
```

## Sprig Functions

Helm includes Masterminds Sprig, providing over 70 template functions.

### String Functions

```yaml
{{ upper "hello" }}         # "HELLO"
{{ lower "HELLO" }}         # "hello"
{{ title "hello world" }}   # "Hello World"
{{ repeat 3 "a" }}          # "aaa"
{{ quote "hello" }}         # "\"hello\""
{{ squote "hello" }}        # "'hello'"
{{ trunc 5 "hello world" }} # "hello"
{{ substr 0 5 "hello" }}    # "hello"
{{ trim "  hello  " }}      # "hello"
{{ nospace "hello world" }} # "helloworld"
{{ hasPrefix "hel" "hello" }} # true
{{ hasSuffix "lo" "hello" }}  # true
{{ contains "ell" "hello" }}  # true
```

### Type Functions

```yaml
{{ default "default" "" }}     # "default"
{{ empty .Values.name }}       # true if nil/0/""/false/empty collection
{{ coalesce nil "" "fallback" }} # "fallback" (first non-empty)
{{ typeOf .Values.name }}      # Type name
{{ kindOf .Values.name }}      # Kind name
```

### Math Functions

```yaml
{{ add 1 2 }}     # 3
{{ sub 5 3 }}     # 2
{{ mul 2 3 }}     # 6
{{ div 10 3 }}    # 3
{{ mod 10 3 }}    # 1
{{ max 1 10 5 }}  # 10
{{ min 1 10 5 }}  # 1
```

### List and Dict Functions

```yaml
# Lists
{{ list "a" "b" "c" }}                   # [a b c]
{{ first .Values.ports }}                 # First element
{{ last .Values.ports }}                  # Last element
{{ append .Values.ports "d" }}            # Append
{{ prepend .Values.ports "z" }}           # Prepend
{{ uniq .Values.ports }}                  # Remove duplicates
{{ without .Values.ports "remove-me" }}   # Remove by value

# Dictionaries
{{ dict "key1" "val1" "key2" "val2" }}   # Create dict
{{ hasKey .Values "enabled" }}            # Check key exists
{{ keys .Values.service }}                # List keys
{{ values .Values.service }}              # List values
{{ merge .Values.defaults .Values.overrides }}  # Merge dicts
{{ omit .Values.service "tls" }}          # Remove key
{{ pick .Values.service "type" "port" }}  # Select keys
```

### Type Conversions

```yaml
{{ toString 123 }}        # "123"
{{ toInt "123" }}         # 123
{{ float64 "1.5" }}       # 1.5
{{ toJson .Values }}      # JSON string
{{ fromJson "{}" }}       # Object from JSON
{{ toYaml .Values }}      # YAML string
{{ fromYaml "key: val" }} # Object from YAML
```

### YAML Formatting

```yaml
# toYaml — format object as YAML
env:
  {{- toYaml .Values.envVars | nindent 2 }}

# nindent — add newline + indent
envFrom:
  - configMapRef:
      name: {{ include "mychart.fullname" . }}
  {{- with .Values.secrets }}
  - secretRef:
      name: {{ include "mychart.fullname" . }}
  {{- end }}

# indent — add spaces to each line
  {{- range .Values.configMapData }}
  {{ .key }}: {{ .value | quote }}
  {{- end }}
```

### Regex

```yaml
{{ regexMatch "^[a-z]+$" .Values.name }}     # Match test
{{ regexReplaceAll "old" .Values.name "new" }} # Replace all
{{ regexFind "\\d+" .Values.version }}         # Find first match
```

### Date Functions

```yaml
{{ now }}                                     # Current time
{{ date "2006-01-02" now }}                    # Format date
{{ dateInZone "2006-01-02" now "UTC" }}        # Format in zone
{{ unixEpoch .Values.timestamp }}             # Parse Unix timestamp
```

## Pipelines

Values pipe through functions left-to-right:

```yaml
# Nested function calls without pipes
{{ quote (upper (default "default" .Values.name)) }}

# Same with pipes (more readable)
{{ .Values.name | default "default" | upper | quote }}

# Common pipelines
name: {{ .Values.name | default "app" | trunc 24 | trimSuffix "-" | quote }}
replicas: {{ .Values.replicaCount | default 1 | int | toString }}
```

## Type Coercion in Comparisons

Helm templates coerce types in `if` conditions:

```yaml
# Falsy values (evaluate to false)
#   false (boolean)
#   0 (integer/float)
#   "" (empty string)
#   nil
#   empty collection

# Truthy values
{{- if .Values.enabled }}    # enabled: true → renders
{{- if .Values.replicas }}   # replicas: 0 → does NOT render
{{- if not .Values.paused }} # paused: false → renders
```

## Template-Level Functions

| Function | Purpose |
|---|---|
| `fail` | Abort rendering with error message |
| `required` | Fail if value is not provided |
| `lookup` | Look up Kubernetes resource at runtime |

```yaml
{{- required "A valid .Values.ingress.host is required!" .Values.ingress.host }}

{{- if not .Values.requiredField }}
  {{- fail ".Values.requiredField is required" }}
{{- end }}

{{- $existing := lookup "v1" "ConfigMap" .Release.Namespace "my-config" }}
```

## References

- [Helm Chart Template Guide](https://helm.sh/docs/chart_template_guide/)
- [Sprig Function Documentation](https://masterminds.github.io/sprig/)
- [Helm Built-in Objects](https://helm.sh/docs/chart_template_guide/builtin_objects/)
