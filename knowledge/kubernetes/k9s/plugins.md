---
title: "k9s Plugins"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k9s
  - kubernetes
  - tooling
  - plugins
  - extensibility
sources:
  - url: "https://k9scli.io/topics/plugins"
    title: "k9s — Plugins"
  - url: "https://github.com/derailed/k9s/tree/master/plugins"
    title: "k9s Community Plugins — GitHub"
last_audit_date: 2026-07-10
---

# k9s Plugins

k9s allows extending the command palette by defining custom cluster commands via plugins. Plugins are YAML files that associate a keyboard shortcut with a shell command, scoped to specific resource views.

## Plugin Locations

k9s scans these directories for plugin definitions (in order):

| Path | Scope |
|---|---|
| `$XDG_CONFIG_HOME/k9s/plugins.yaml` | Global — single file |
| `$XDG_CONFIG_HOME/k9s/plugins/` | Global — directory of files |
| `$XDG_DATA_HOME/k9s/plugins/` | Global — directory of files |
| `$XDG_DATA_DIRS/k9s/plugins/` | Global — directory of files |
| `$XDG_DATA_HOME/k9s/clusters/<cluster>/<context>/plugins.yaml` | Per-context override |

Source: [k9s Plugins — Overview](https://k9scli.io/topics/plugins)

## Plugin Definition Fields

| Field | Type | Description |
|---|---|---|
| `shortCut` | string | Key combination to trigger the plugin (e.g. `Ctrl-L`, `Shift-B`) |
| `description` | string | Label shown in the k9s help menu |
| `scopes` | array | Resource views where the plugin is active (e.g. `["po"]`, `["all"]`) |
| `command` | string | Shell command to run (can use krew plugins) |
| `background` | boolean | Run in background mode (no visible output) |
| `args` | array | Arguments passed to the command |

Source: [k9s Plugins — Overview](https://k9scli.io/topics/plugins)

## Available Environment Variables

Plugins receive these environment variables at runtime:

| Variable | Description |
|---|---|
| `$NAME` | Selected resource name |
| `$NAMESPACE` | Selected resource namespace |
| `$POD` | Pod name (while in container view) |
| `$CONTAINER` | Container name |
| `$FILTER` | Current active filter |
| `$KUBECONFIG` | Path to the active KubeConfig |
| `$CLUSTER` | Active cluster name |
| `$CONTEXT` | Active context name |
| `$USER` | Active user |
| `$GROUPS` | Active groups |
| `$RESOURCE_GROUP` | Selected resource API group |
| `$RESOURCE_VERSION` | Selected resource API version |
| `$RESOURCE_NAME` | Selected resource name (same as `$NAME`) |
| `$COL-<COLUMN_NAME>` | Value of a specific column in the current view |

Source: [k9s Plugins — Overview](https://k9scli.io/topics/plugins)

## Examples

### Single Plugin (plugins.yaml)

```yaml
# $XDG_CONFIG_HOME/k9s/plugins.yaml
plugins:
  fred:
    shortCut: Ctrl-L
    description: Pod logs
    scopes:
      - po
    command: kubectl
    background: false
    args:
      - logs
      - -f
      - $NAME
      - -n
      - $NAMESPACE
      - --context
      - $CONTEXT
```

### Multiple Plugins in One File

```yaml
# $XDG_DATA_HOME/k9s/plugins/misc-plugins/blee.yaml
fred:
  shortCut: Shift-B
  description: Bozo
  scopes:
    - deploy
  command: bozo

zorg:
  shortCut: Shift-Z
  description: Pod logs
  scopes:
    - svc
  command: zorg
```

### Plugin Snippet (file name becomes plugin name)

```yaml
# $XDG_DATA_HOME/k9s/plugins/schtuff/bozo.yaml
shortCut: Shift-B
description: Bozo
scopes:
  - deploy
  command: bozo
```

Source: [k9s Plugins — Examples](https://k9scli.io/topics/plugins)

## Community Plugins

The k9s repository hosts a collection of community-contributed plugins for common use cases:

- [GitHub: derailed/k9s/plugins](https://github.com/derailed/k9s/tree/master/plugins)

Source: [k9s Plugins — Community Plugins](https://k9scli.io/topics/plugins)
