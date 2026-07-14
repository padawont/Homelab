---
title: "k9s Debugging Workflows"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k9s
  - kubernetes
  - tooling
  - debugging
  - logging
sources:
  - url: "https://k9scli.io/topics/commands"
    title: "k9s — Commands"
  - url: "https://k9scli.io/topics/shell"
    title: "k9s — NodeShell"
  - url: "https://k9scli.io/topics/bench"
    title: "k9s — Benchmarking"
  - url: "https://k9scli.io/topics/config"
    title: "k9s — Configuration"
last_audit_date: 2026-07-10
---

# k9s Debugging Workflows

## Tail Logs for a Pod

1. Navigate to pod view: `:pod`⏎
2. Select the target pod using arrow keys
3. Press `l` to view logs
4. Use `/` to filter log lines by keyword
5. Adjust log configuration in `$XDG_CONFIG_HOME/k9s/config.yaml`:
   ```yaml
   k9s:
     logger:
       tail: 100          # Initial lines shown
       buffer: 5000       # Max lines stored in view
       sinceSeconds: -1   # -1 = tail (follow); 300 = last 5 minutes
       fullScreen: true   # Full-screen log view
       showTime: true     # Prepend timestamps
       textWrap: false    # Toggle line wrapping
   ```

To exit log view: press `<esc>`.

Source: [k9s Commands — Key Bindings](https://k9scli.io/topics/commands), [k9s Config — Logger](https://k9scli.io/topics/config)

## Exec into a Pod

1. Navigate to pod view: `:pod`⏎
2. Select the target pod
3. Press `s` to open a shell

By default, k9s launches a BusyBox container (`busybox:1.35.0`) on the target node. Customize the shell pod image in `config.yaml`:

```yaml
k9s:
  shellPod:
    image: ubuntu:22.04          # Custom image with your tools
    namespace: default            # Namespace for the shell pod
    limits:
      cpu: 100m
      memory: 100Mi
    tty: true
```

Source: [k9s Commands — Key Bindings](https://k9scli.io/topics/commands), [k9s Config — ShellPod](https://k9scli.io/topics/config)

## Port-Forward to a Pod

1. Navigate to pod view and select a pod
2. Press `Shift-F` to open the port-forward dialog
3. Enter the container port and optional local address
4. View active port-forwards: `:pf`⏎ (PortForward view)
5. To stop a forward, select it and press `ctrl-d`

Port-forwards persist for the duration of the k9s session and terminate on exit. The default forwarding address is `localhost`; override globally with `portForwardAddress` in config or per-cluster with `K9S_DEFAULT_PF_ADDRESS` env var.

Source: [k9s Commands — Key Bindings](https://k9scli.io/topics/commands), [k9s Config — portForwardAddress](https://k9scli.io/topics/config)

## Node Shell

Access a shell directly on a cluster node. Requires the `nodeShell` feature gate.

1. Enable per-context in `$XDG_DATA_HOME/k9s/clusters/<cluster>/<context>/config.yaml`:
   ```yaml
   k9s:
     featureGates:
       nodeShell: true
   ```
2. Global override: `export K9S_FEATURE_GATE_NODE_SHELL=true`
3. Navigate to node view: `:nodes`⏎
4. Select a node and press `s`
5. k9s launches a shell pod (default `busybox:1.35.0`) on the selected node

Source: [k9s NodeShell page](https://k9scli.io/topics/shell)

## Error Drill-Down

When a pod is in `CrashLoopBackOff`, `Error`, or `Pending`:

1. Select the pod and press `d` to describe — shows events, conditions, and recent pod status transitions
2. Press `v` to view the full YAML manifest — check `status.containerStatuses` for the last termination state and exit code
3. Press `l` to view logs from the last failed attempt
4. Navigate to related resources: press `:` then type the resource name to jump to events, configmaps, secrets

The Pulses view (`:pulses`) provides a top-level dashboard of cluster health. The XRay view (`:xray po`) visualizes pod dependencies.

Source: [k9s Commands — Key Bindings](https://k9scli.io/topics/commands)

## Benchmark HTTP Endpoints

k9s integrates [Hey](https://github.com/rakyll/hey) for benchmarking HTTP services and port-forwards.

### Benchmark a Port-Forward

1. Set up a port-forward (`Shift-F` on a pod)
2. Navigate to PortForward view: `:pf`⏎
3. Select the active forward and press `b`

### Benchmark Configuration

Each context has its own `benchmarks.yaml` at `$XDG_DATA_HOME/k9s/clusters/<cluster>/<context>/benchmarks.yaml`:

```yaml
benchmarks:
  defaults:
    concurrency: 1
    requests: 1000
  containers:
    default/nginx:nginx:
      concurrency: 1
      requests: 10000
      http:
        path: /bozo
        method: POST
        body: '{"fred":"blee"}'
        header:
          Content-Type: ["application/json"]
  services:
    default/nginx:
      concurrency: 5
      requests: 500
      http:
        method: GET
        host: 1.2.3.4
        path: /
```

Results are stored in `$XDG_STATE_HOME/k9s/clusters/<cluster>/<context>/` as text files. View benchmark history: `:be`⏎.

Source: [k9s Benchmarking page](https://k9scli.io/topics/bench)

## Diagnostics

```bash
k9s info
```
Shows active config directory, log path, KubeConfig location, and context. Use this to:
- Confirm k9s is reading the expected KubeConfig
- Find log files for troubleshooting plugin or config errors
- Verify the active cluster and namespace

Source: [k9s Commands — CLI Arguments](https://k9scli.io/topics/commands)
