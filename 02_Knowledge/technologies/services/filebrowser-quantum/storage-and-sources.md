---
title: "FileBrowser Quantum — sources and Kubernetes storage"
status: draft
author: "padawont"
date: 2026-11-08
tags: [filebrowser, filebrowser-quantum, kubernetes, storage, volumes, self-hosted]
sources:
  - url: "https://filebrowserquantum.com/en/docs/configuration/sources/"
    title: "FileBrowser Quantum — Sources configuration"
  - url: "https://filebrowserquantum.com/en/docs/advanced/source-configuration/sources/"
    title: "FileBrowser Quantum — Advanced source configuration"
  - url: "https://filebrowserquantum.com/en/docs/advanced/source-configuration/conditional-rules/"
    title: "FileBrowser Quantum — Conditional rules"
  - url: "https://filebrowserquantum.com/en/docs/changelog/stable/"
    title: "FileBrowser Quantum — Stable changelog"
  - url: "https://kubernetes.io/docs/concepts/storage/volumes/#hostpath"
    title: "Kubernetes — Volumes (hostPath)"
  - url: "https://kubernetes.io/docs/concepts/storage/persistent-volumes/"
    title: "Kubernetes — Persistent Volumes"
last_audit_date: 2026-11-10
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/storage.md"
  - "./02_Knowledge/technologies/kubernetes/longhorn/overview.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/overview.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/installation.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/configuration.md"
  - "./05_Implementations/node-main/k3s/overview.md"
---

# FileBrowser Quantum — sources and Kubernetes storage

## Overview

A **source** is a filesystem directory FileBrowser Quantum exposes in its UI; one
instance can declare several, each an independent entry under `server.sources` with
its own name, path, and per-source rules. The classic-Filebrowser single-root
contrast is owned by `./02_Knowledge/technologies/services/filebrowser-quantum/overview.md`.

On Kubernetes the source path is only as real as the volume mounted into the pod.
This note covers the config shape, include/exclude rules, the three homelab source
types mapped to Kubernetes volumes, and the RWO consequence.

Verified against **v2.0.2-stable** (released 2026-10-23); docs read 2026-11-08.

## Details

### Source configuration shape

`sources` is a list under `server`; each entry takes a required `path` and an
optional `name`. Multiple entries produce multiple roots in one UI.

Example — abstract:

```yaml
server:
  sources:
    - path: "/data/media"          # unique real filesystem path
      name: "Media"                # defaults to the path's base name
      config:
        defaultEnabled: true       # granted to all users (default: false)
        denyByDefault: false
        rules:
          - folderName: "node_modules"
          - fileEndsWith: ".tmp"
    - path: "/data/shared"
      name: "Shared"
      config: { defaultEnabled: false }
```

- `path` must be unique and resolve to a real, readable directory; sources are
matched by resolved path, so renaming `name` is safe.
- `path` is resolved inside the container's filesystem namespace: an absolute
container path that exists in the pod and is readable by the process. Relative paths
are allowed but not appropriate for production. The source sees only pod mounts.
- `defaultEnabled: true` grants the source to all users on creation and, from v2.0.1,
merges it for existing users on startup. Default is `false`; `false` means manual.
- Other `config` keys include: `denyByDefault`, `disabled`, `useLogicalSize`, `rules`.
- Do not use `/` as a source or include `/var`; point at a dedicated subdirectory.

### Include/exclude rules

Rules live in `config.rules`. For exclusion rules the match is **OR-based**: if any rule
matches an item, the item is excluded from the index/UI. `includeRootItem` is the inverse
— it is an allowlist. Path selectors are relative to the source root.

| Selector | Matches |
|---|---|
| `folderPath`, `filePath` | Exact path relative to source root |
| `folderName`, `fileName` | Exact name anywhere in the source |
| `folderStartsWith` / `folderEndsWith` | Name prefix/suffix, folders only |
| `fileStartsWith` / `fileEndsWith` | Name prefix/suffix, files only |
| `includeRootItem` | Keep only the listed root items visible |
| `neverWatchPath` | Index once, then stop rescanning that folder |
| `viewable` | Show in UI but exclude from search and size calculations |

Flags `ignoreHidden`, `ignoreZeroSizeFolders`, and `ignoreSymlinks` apply per rule;
set them on a `folderPath: "/"` rule to make them global. A global rule with
`viewable: true` disables indexing while keeping the source browsable.

### Three source types → Kubernetes volume types

The `path` in config is a **container-visible path**. Whatever the pod does not
mount, the source cannot see; the process sees only its own mount namespace.

| Source type | Kubernetes volume | What the mount looks like |
|---|---|---|
| Selected host directories | `hostPath` (or a `local-path` PVC) | Host dir mounted at a chosen container path |
| Existing Longhorn PVC | `persistentVolumeClaim` referencing it | Existing claim mounted at a chosen path |
| Dedicated shared volume | A new PVC | New claim mounted at a chosen path |

`hostPath` and the `local-path` PVC both bind the data to one node, so a pod needing it
must land there; `local-path` adds a claim in front of the same node-local directory.
Volume theory lives in `./02_Knowledge/technologies/kubernetes/concepts/storage.md`.

Example — abstract (paths are illustrative, not cluster values):

```yaml
spec:
  containers:
    - name: filebrowser-quantum
      volumeMounts:
        - { name: media, mountPath: /data/media }     # hostPath
        - { name: docs, mountPath: /data/docs }       # existing Longhorn PVC
        - { name: shared, mountPath: /data/shared }   # new PVC
  volumes:
    - { name: media, hostPath: { path: /srv/media, type: Directory } }
    - { name: docs, persistentVolumeClaim: { claimName: cv-sender-data } }
    - { name: shared, persistentVolumeClaim: { claimName: filebrowser-shared } }
```

Each `mountPath` must match (or be a parent of) the source `path`: `mountPath:
/data/media` supports `path: "/data/media"` and `"/data/media/photos"`, not `"/media"`.

### RWO consequence

Longhorn volumes are ReadWriteOnce unless a PVC explicitly requests RWX — access mode is
declared on the claim, not defaulted by the driver. The consequence here is that RWO is
node-scoped, not pod-scoped: on this single-node k3s cluster, several pods on `node-main`
can mount the same RWO PVC at once, for example FileBrowser Quantum and the service that
owns the claim. A second node could not mount it while the first node holds it. Cross-node
sharing needs an RWX-capable volume or separate per-node volumes.

## Sources / Further Reading

- [Sources configuration](https://filebrowserquantum.com/en/docs/configuration/sources/)
- [Advanced source configuration](https://filebrowserquantum.com/en/docs/advanced/source-configuration/sources/)
- [Conditional rules](https://filebrowserquantum.com/en/docs/advanced/source-configuration/conditional-rules/)
- [Stable changelog](https://filebrowserquantum.com/en/docs/changelog/stable/)
- [Kubernetes Volumes — hostPath](https://kubernetes.io/docs/concepts/storage/volumes/#hostpath)
- [Kubernetes Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
