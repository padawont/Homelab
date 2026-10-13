---
title: "cv sender outreach worker — Rollback"
status: draft
author: "padawont"
date: 2026-10-13
tags: [kubernetes, automation, rollback, teardown]
technologies: [python, playwright, kubernetes]
related_docs:
  - "./overview.md"
  - "./04_ADRs/612-cv-sender.md"
references:
  online:
    - url: "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"
      title: "Kubernetes Deployments"
  repo:
    - "./overview.md"
node: node-main
---

# cv sender outreach worker — Rollback

Stop the worker and, if needed, remove it from the cluster. The image and the
`state.db` on the PVC are retained by a Deployment-level rollback, so a later
restart resumes without re-sending. The Secret and PVC are **not** deleted by a
Deployment rollback.

## Prerequisites

- `kubectl` access to the `node-main` k3s cluster.
- Confirmation that no run is mid-send; a clean stop avoids a half-processed row.
- A backup copy of `state.db` if the PVC is to be deleted (it records what has
  already been sent).

## Rollback steps

1. Stop the worker without discarding state — scale the Deployment to zero:

```bash
kubectl -n cv-sender scale deployment/cv-sender --replicas=0
```

2. Full removal of the workload and its manifests (namespace, ConfigMap, PVC,
   Deployment):

```bash
kubectl delete -f configs/
```

3. Only if state must be discarded — **destructive**, loses send history:

```bash
kubectl -n cv-sender delete secret cv-sender-secrets
kubectl -n cv-sender delete pvc cv-sender-data
```

## Verification

```bash
kubectl -n cv-sender get deploy,pods     # no running pods after scale to 0
kubectl -n cv-sender get pvc             # retained unless step 3 was run
```

Scaling back to `--replicas=1` (or re-applying `configs/`) resumes from the same
`state.db` on the PVC without re-sending.
