---
title: "k9s terminal Kubernetes UI — Rollback"
status: active
author: "padawont"
date: 2026-10-02
tags: [kubernetes, k9s, rollback]
technologies: [k9s, helm, kubectl]
related_docs:
  - "./overview.md"
  - "./05_Implementations/node-main/k3s/overview.md"
references:
  online:
    - url: "https://k9scli.io/"
      title: "k9s documentation"
  repo:
    - "./overview.md"
node: node-main
---

# k9s terminal Kubernetes UI — Rollback

Remove the k9s binary (and optionally Helm/kubectl) from `node-main`. This does
not affect the k3s cluster.

## Prerequisites

- `sudo` on `node-main`.
- Confirmation that no automation depends on the tools being removed.

## Rollback steps

1. Remove the k9s binary:

```bash
sudo rm -f /usr/local/bin/k9s
```

2. Optionally remove Helm and `kubectl`:

```bash
sudo rm -f /usr/local/bin/helm
sudo rm -f /usr/local/bin/kubectl
```

   Note: `/usr/local/bin/kubectl` is a symlink to the k3s binary. Removing it does
   **not** remove k3s; `k3s kubectl` still works.

## Verification

```bash
which k9s        # no output
k9s version      # command not found
```

The k3s cluster remains running and unaffected.
