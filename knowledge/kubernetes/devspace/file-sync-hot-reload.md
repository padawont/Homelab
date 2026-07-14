---
title: "DevSpace File Sync & Hot Reload"
status: draft
author: padawont
date: 2026-07-13
tags:
  - devspace
  - file-sync
  - hot-reload
  - port-forwarding
  - kubernetes
sources:
  - url: "https://www.devspace.sh/docs/configuration/dev/"
    title: "Dev Configuration — Official Docs"
  - url: "https://www.devspace.sh/docs/configuration/dev/connections/file-sync"
    title: "File Sync Configuration — Official Docs"
  - url: "https://www.devspace.sh/docs/configuration/dev/connections/port-forwarding"
    title: "Port Forwarding — Official Docs"
  - url: "https://www.devspace.sh/docs/getting-started/development"
    title: "Development with DevSpace — Official Docs"
last_audit_date: 2026-07-13
---

# DevSpace File Sync & Hot Reload

DevSpace provides bi-directional file synchronization between your local filesystem and a container running in Kubernetes. This is the core mechanism for hot reloading — edit files locally and see changes reflected in the running container within seconds, without rebuilding images.

## How File Sync Works

1. DevSpace injects a small helper binary into the target container via `kubectl cp` (requires `tar` in the container)
2. Runs an initial sync according to the configured strategy
3. Watches for file changes on both sides (local and container) using inotify by default
4. Syncs changed files according to path mappings
5. Optionally restarts the container or runs post-sync commands

## Sync Path Mapping

Configure sync paths in the `dev` section of `devspace.yaml`:

```yaml
dev:
  app:
    imageSelector: ghcr.io/org/project/image
    sync:
      - path: ./:/app                    # local:remote mapping
      - path: ./config                   # same path name locally and remotely
```

Path format is `localPath:remotePath`. Use `.` to refer to the working directory on either side (e.g., `.:.` syncs the local project root to the container working directory).

## Exclude Paths

Use gitignore-formatted patterns to exclude files:

```yaml
dev:
  app:
    sync:
      - path: ./
        excludePaths:
          - node_modules/
          - logs/
        uploadExcludePaths:
          - build/              # Never upload build artifacts
        downloadExcludePaths:
          - tmp/                # Never download temp files
```

You can also load excludes from a file:

```yaml
dev:
  app:
    sync:
      - path: ./
        excludeFile: .gitignore
        uploadExcludeFile: .uploadignore
        downloadExcludeFile: .downloadignore
```

## Initial Sync Strategies

The `initialSync` option controls what happens when a sync session starts:

| Strategy | Behavior |
|---|---|
| `mirrorLocal` (default) | Deletes container files not on local; uploads missing local files; prefers local on conflict |
| `preferLocal` | Like `mirrorLocal` but skips the delete step |
| `mirrorRemote` | Deletes local files not in container; downloads missing container files; prefers container on conflict |
| `preferRemote` | Like `mirrorRemote` but skips the delete step |
| `preferNewest` | Uploads missing local, downloads missing container; prefers newest on conflict |
| `keepAll` | Uploads missing local, downloads missing container; does not resolve conflicts |
| `disabled` | No initial sync |

Useful pattern for node_modules (download from container, never upload):

```yaml
dev:
  app:
    sync:
      - path: ./
        excludePaths:
          - node_modules/*
      - path: ./node_modules/:/app/node_modules/
        initialSync: preferRemote
```

## Sync-Triggered Actions

### Restart Container

Restart the container whenever files are synced (useful for compiled languages):

```yaml
dev:
  app:
    command: ["my-app-server"]
    sync:
      - path: ./
        onUpload:
          restartContainer: true
```

Requires `command` to be set (so DevSpace knows what to restart). For interpreted languages or frameworks with built-in hot reload (nodemon, React, Rails, Flask), prefer language-native reloading instead of container restart — it's faster.

### Run Commands on Upload

Execute commands after sync completes:

```yaml
dev:
  app:
    sync:
      - path: ./
        onUpload:
          exec:
            - command: npm install
              onChange: ["./package.json"]     # only when package.json changes
            - command: echo 123 > local.txt
              local: true                       # run locally, not in container
            - command: touch abc.txt
              failOnError: false
```

If both `restartContainer` and `exec` are defined, DevSpace runs commands **before** restarting the container.

### Delay Container Start

Wait for initial sync to finish before starting the container:

```yaml
dev:
  app:
    command: ["entrypoint"]
    sync:
      - path: ./
        startContainer: true
```

If multiple sync paths have `startContainer: true`, DevSpace waits for all initial syncs to complete.

## One-Directional Sync

```yaml
dev:
  app:
    sync:
      - path: ./
        disableDownload: true    # local-only changes sent to container
        # disableUpload: true    # container-only changes sent to local
```

## Polling vs Inotify

By default, DevSpace uses inotify to detect changes. If inotify is unsupported (certain environments or filesystem types), enable polling:

```yaml
dev:
  app:
    sync:
      - path: ./
        polling: true
```

Polling increases CPU usage on the container proportional to the number of watched files.

## Bandwidth Limits

```yaml
dev:
  app:
    sync:
      - path: ./
        bandwidthLimits:
          download: 200     # KB/s
          upload: 100       # KB/s
```

## Single File Sync

```yaml
dev:
  app:
    sync:
      - path: "${DEVSPACE_USER_HOME}/.gitconfig:/root/.gitconfig"
        file: true
        disableDownload: true
```

## Port Forwarding

DevSpace forwards ports from the container to localhost, and can reverse-forward from local to container.

### Standard Port Forwarding

```yaml
dev:
  app:
    ports:
      - port: "8080"              # localPort:remotePort (same port)
      - port: "9090:3000"         # local 9090 → container 3000
      - port: "9000"
        bindAddress: "0.0.0.0"    # listen on all interfaces
```

### Reverse Port Forwarding

Make a local port available inside the container (e.g., for a local debugger):

```yaml
dev:
  app:
    reversePorts:
      - port: "2345"              # container port → local port
      - port: "4000:4000"
        bindAddress: "0.0.0.0"
```

## Hot Reload Workflow Summary

The recommended hot reload approach depends on your stack:

| Stack | Recommended Approach |
|---|---|
| Node.js (nodemon, React, Next.js) | Language-native file watcher + DevSpace sync |
| Go | DevSpace `restartContainer` or `air` (Go live reload) |
| Python (Flask, Django, FastAPI) | Language-native reload (`--reload` flag) + DevSpace sync |
| Java (Spring Boot) | DevTools (automatic restart) + DevSpace sync |
| Compiled language, no reload tool | DevSpace `restartContainer: true` |

## Pitfalls

- **`tar` requirement**: The `tar` command must be present in the container for `kubectl cp` to inject the sync helper. If missing, file sync fails.
- **Endless loops**: Post-sync commands that modify synced files can trigger another sync cycle. Use `onChange` to restrict command execution to specific files, or ensure commands do not write to watched paths.
- **Symlinks**: DevSpace sync does not follow symlinks by default. If your project uses symlinks (common in monorepos), test sync behavior.
- **Large file counts**: Initial sync with `mirrorLocal` on a large repository can take time. Consider `preferLocal` or `keepAll` for faster startup, or use `excludePaths` aggressively.
- **DevSpace UI port**: The UI runs on 8090 by default. If you need port 8090 for your application, configure a different UI port or disable the UI with `--show-ui=false`.
