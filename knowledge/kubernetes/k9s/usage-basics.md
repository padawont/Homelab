---
title: "k9s Usage Basics"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k9s
  - kubernetes
  - tooling
  - usage
  - shortcuts
sources:
  - url: "https://k9scli.io/topics/commands"
    title: "k9s — Commands"
  - url: "https://k9scli.io/topics/aliases"
    title: "k9s — Aliases"
  - url: "https://k9scli.io/topics/hotkeys"
    title: "k9s — HotKeys"
last_audit_date: 2026-07-10
---

# k9s Usage Basics

## CLI Arguments

Launch k9s with various options to set the initial view, namespace, context, or mode.

```bash
# List all available CLI options
k9s help

# Get info about k9s runtime (logs, configs, paths)
k9s info

# Launch in a specific namespace
k9s -n mycoolns

# Launch directly into pod view
k9s -c pod

# Start with a specific KubeConfig context
k9s --context coolCtx

# Start in read-only mode (all modification commands disabled)
k9s --readonly
```

Source: [k9s Commands — CLI Arguments](https://k9scli.io/topics/commands)

## Key Bindings Reference

| Key | Action | Notes |
|---|---|---|
| `?` | Show keyboard help | Lists all active key bindings |
| `ctrl-a` | Show all resource aliases | Lists every available resource short name |
| `:q` / `ctrl-c` | Quit k9s | |
| `:`pod`⏎` | View pods | Accepts singular, plural, or short name |
| `:`pod `ns-x``⏎` | View pods in namespace | |
| `:`pod `/fred``⏎` | View pods filtered by "fred" | Regex filter on resource name |
| `:`pod `app=fred,env=dev``⏎` | View pods matching labels | Label selector |
| `:`pod `@ctx1``⏎` | View pods in context ctx1 | Switches context temporarily |
| `/`filter`⏎` | Filter current view | Regex2 supported (`fred\|blee`) |
| `/!`filter`⏎` | Inverse regex filter | Keeps everything that does not match |
| `/-l `label-selector``⏎` | Filter by labels | |
| `/-f `filter``⏎` | Fuzzy find a resource | |
| `<esc>` | Exit command/filter mode | |
| `:ctx`⏎ | View and switch contexts | |
| `:ctx `context-name``⏎ | Switch directly to a context | Retains last-used view |
| `:ns`⏎ | View and switch namespaces | |
| `:screendump` or `:sd` | View all saved screen dumps | |
| `ctrl-d` | Delete resource | Requires TAB + ENTER to confirm |
| `ctrl-k` | Kill resource | No confirmation (like `kubectl delete --now`) |
| `:pulses` or `:pu` | Launch Pulses dashboard | Cluster-level health overview |
| `:xray `RESOURCE `[NAMESPACE]``⏎ | Launch XRay view | Resource dependency graph |

Source: [k9s Commands — Key Bindings](https://k9scli.io/topics/commands)

## Resource View Navigation

Once in a resource view (e.g. pod list), these keys operate on the selected row:

| Key | Action |
|---|---|
| `d` | Describe resource |
| `v` | View YAML |
| `e` | Edit resource (opens in `$KUBE_EDITOR`) |
| `l` | View logs |
| `s` | Shell into pod |
| `Shift-F` | Port-forward |
| `b` | Run benchmark |
| `ctrl-d` | Delete (with confirm) |
| `ctrl-k` | Kill (no confirm) |

Source: [k9s Commands — Key Bindings](https://k9scli.io/topics/commands)

## Custom Aliases

Define shortcuts for frequently accessed resources or custom queries in `$XDG_CONFIG_HOME/k9s/aliases.yaml`. Aliases map a short name to a GVR (Group/Version/Resource) or to a command.

```yaml
# $XDG_CONFIG_HOME/k9s/aliases.yaml
aliases:
  pp: v1/pods                        # Alias "pp" for pods
  dep: apps/v1/deployments           # Alias "dep" for deployments
  fred: acme.io/v1alpha1/fredericks  # Alias for a CRD
  pos: pod kube-system app=fred,blee=duh  # Alias for a filtered command
```

Context-specific aliases go in `$XDG_DATA_HOME/k9s/clusters/<cluster>/<context>/aliases.yaml`.

Source: [k9s Aliases page](https://k9scli.io/topics/aliases)

## Custom HotKeys

Create `$XDG_DATA_HOME/k9s/hotkeys.yaml` to bind navigation commands to key shortcuts. Hotkeys appear in the help view (`?`) and reload automatically.

```yaml
# $XDG_DATA_HOME/k9s/hotkeys.yaml
hotKeys:
  shift-0:
    shortCut: Shift-0
    description: Viewing pods with label app=kindnet
    command: pods app=kindnet
  shift-1:
    shortCut: Shift-1
    description: View deployments
    command: dp
  shift-2:
    shortCut: Shift-2
    description: XRay Deployments
    command: xray deploy
```

Source: [k9s HotKeys page](https://k9scli.io/topics/hotkeys)

## Configuration File

Main config at `$XDG_CONFIG_HOME/k9s/config.yaml`. Key settings:

```yaml
k9s:
  refreshRate: 2                     # UI poll interval in seconds
  readOnly: false                    # Disable modification commands
  noExitOnCtrlC: false               # When true, use :q to quit
  portForwardAddress: localhost      # Default port-forward host
  ui:
    enableMouse: false               # Mouse support
    headless: false                  # Hide header
    noIcons: false                   # Disable icons (if terminal does not support them)
  logger:
    tail: 100                        # Lines to show initially
    buffer: 5000                     # Max log lines in view
    sinceSeconds: 300                # Go back N seconds (-1 = tail)
    fullScreen: false                # Full-screen log view
    showTime: false                  # Show timestamps in logs
  thresholds:                        # Alert thresholds for CPU/memory
    cpu:
      critical: 90
      warn: 70
    memory:
      critical: 90
      warn: 70
```

Source: [k9s Config page](https://k9scli.io/topics/config)
