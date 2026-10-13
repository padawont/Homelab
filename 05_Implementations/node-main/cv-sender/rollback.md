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

Stop the worker, or remove it from the cluster entirely. Scaling the Deployment
to zero is the non-destructive stop: it retains the image, the Secret, and the
`state.db` on the PVC, so a later restart resumes without re-sending. Only the
explicit destructive steps below remove the PVC and its `state.db`.

## Prerequisites

- `kubectl` access to the `node-main` k3s cluster.
- Confirmation that no run is mid-send; a clean stop avoids a half-processed row.
- A backup copy of `state.db` before any step that removes the PVC — it records
  what has already been sent.

## Rollback steps

### 1. Non-destructive stop — retain state

Scale the Deployment to zero. This stops the pod but keeps the PVC, `state.db`,
the image and the Secret; deleting the Deployment *on its own* likewise does
**not** delete the PVC:

```bash
kubectl -n cv-sender scale deployment/cv-sender --replicas=0
```

### 2. Full teardown — destructive, discards `state.db`

Delete the namespaced resources by explicit name. Do **not** use
`kubectl delete -f configs/`: that directory contains `namespace.yaml`, so a
directory delete would remove the whole `cv-sender` Namespace and cascade to
the PVC — destroying `state.db`. Secondary reasons: the same directory also
holds `config.yaml` (not a manifest) and `secret.yaml.example` (never applied),
so a directory delete is both wrong and incomplete:

```bash
kubectl -n cv-sender delete deploy/cv-sender configmap/cv-sender-config pvc/cv-sender-data
```

Deleting the PVC `cv-sender-data` permanently discards `state.db` — the k3s
default `local-path` StorageClass uses `reclaimPolicy: Delete`, so the backing
volume goes with it. Back it up first (Prerequisites).

### 3. Remove the Secret — separate, credential handling

Step 2 does not touch `cv-sender-secrets`. Delete it only if the app password
must be discarded or rotated:

```bash
kubectl -n cv-sender delete secret cv-sender-secrets
```

### 4. Optional — remove the namespace

If the whole `cv-sender` Namespace should go, delete it directly. This cascades
to **every** namespaced object it still contains, including the PVC and thus
`state.db`; use this step *or* the PVC deletion in step 2, not both:

```bash
kubectl delete namespace cv-sender
```

## Verification

```bash
# Only meaningful while the namespace still exists (i.e. step 4 was NOT run):
kubectl -n cv-sender get deploy,pods     # no running pods after scale to 0
kubectl -n cv-sender get pvc             # present after step 1; gone if step 2 ran

# If the namespace was removed (step 4), the namespaced checks above fail with
# "namespace not found" — verify with a non-namespaced check instead:
kubectl get namespace cv-sender          # "NotFound" once removed
kubectl get pvc -A                       # no cv-sender-data PVC remains
```

Scaling back to `--replicas=1` resumes from the same `state.db` on the PVC
without re-sending. If the resources were removed (step 2), re-apply them
explicitly in dependency order rather than with a bare directory apply, and
recreate the Secret from the untracked `configs/secret.yaml` (see
`configs/secret.yaml.example`):

```bash
kubectl apply -f configs/namespace.yaml -f configs/configmap.yaml -f configs/pvc.yaml -f configs/deployment.yaml
```
