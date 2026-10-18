---
title: "cv sender — staged cluster rollout runbook"
status: draft
author: "padawont"
date: 2026-10-14
tags: [kubernetes, automation, deployment, rollout, pilot]
technologies: [python, playwright, kubernetes]
related_docs:
  - "./overview.md"
  - "./rollback.md"
  - "./04_ADRs/612-cv-sender.md"
references:
  online:
    - url: "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"
      title: "Kubernetes Deployments"
  repo:
    - "./05_Implementations/node-main/cv-sender/overview.md"
node: node-main
---

# cv sender — staged cluster rollout runbook

Execution companion to the Deployment section of `./overview.md` for GitHub issue
#616. It adds the two things `overview.md` does not spell out: **seeding the PVC
before the Deployment starts** and the **gates** between dry run, pilot and full
run. Sending is irreversible, so every gate must pass before the next stage.

## Prerequisites

- `node-main` (192.168.111.7) reachable and `kubectl` bound to its k3s context
  (`KUBECONFIG=/etc/rancher/k3s/k3s.yaml`, or `sudo k3s kubectl` on the node).
- The build host holds `data/cv/cv.pdf` (the CV) and the pilot `data/state.db`
  (the 3 sends from the local pilot, so the cluster cannot re-send them).
- `configs/config.yaml` has `dry_run: true`.
- The Gmail App Password and applicant signature name/phone are to hand.

## Stage 0 — Pre-deploy checks

```bash
kubectl config current-context      # node-main k3s
kubectl get nodes
```

Confirm the target is `node-main`, namespace `cv-sender`, image `cv-sender:0.1`.

## Stage 1 — Build and import the image

```bash
docker build -t cv-sender:0.1 .
docker save cv-sender:0.1 | sudo k3s ctr images import -
```

The Deployment uses `imagePullPolicy: Never`, so the import is mandatory.

## Stage 2 — Namespace, Secret, ConfigMap, PVC

```bash
kubectl apply -f configs/namespace.yaml
cp configs/secret.yaml.example configs/secret.yaml   # untracked; fill the real values
kubectl apply -f configs/secret.yaml
kubectl apply -f configs/configmap.yaml
kubectl apply -f configs/pvc.yaml
```

Do **not** `kubectl apply -f configs/`: `config.yaml` is not a manifest,
`secret.yaml.example` is skipped by extension, and lexical order breaks the
namespace → Secret → ConfigMap → PVC → Deployment dependency chain.

The PVC declares no `storageClassName`, so it binds to the cluster default. This
cluster carries **two** defaults (`local-path` and `longhorn`), and the PVC bound
to `longhorn`; pin `storageClassName` if a specific class is required.

## Stage 3 — Seed the PVC (before the Deployment)

The Deployment mounts the PVC subPath `cv` read-only at `/app/config/cv`; if
`cv/cv.pdf` is absent the pod will not start. Seeding the pilot `state.db` is what
stops the cluster re-sending the 3 pilot companies.

```bash
kubectl -n cv-sender run seed --image=busybox --restart=Never \
  --overrides='{"spec":{"containers":[{"name":"seed","image":"busybox","command":["sleep","3600"],"volumeMounts":[{"name":"d","mountPath":"/data"}]}],"volumes":[{"name":"d","persistentVolumeClaim":{"claimName":"cv-sender-data"}}]}}'
kubectl -n cv-sender wait --for=condition=Ready pod/seed
kubectl -n cv-sender cp data/cv/cv.pdf seed:/data/cv/cv.pdf
kubectl -n cv-sender cp data/state.db  seed:/data/state.db
# kubectl cp preserves the source uid (1000). The worker drops ALL capabilities,
# so its root lacks CAP_DAC_OVERRIDE and cannot write a file it does not own —
# it fails with "attempt to write a readonly database". chown to root (0:0).
kubectl -n cv-sender exec seed -- chown 0:0 /data/state.db /data/cv/cv.pdf
kubectl -n cv-sender exec seed -- ls -ln /data /data/cv   # expect uid 0
kubectl -n cv-sender delete pod seed
```

## Stage 4 — Deploy dry (Gate A)

```bash
kubectl apply -f configs/deployment.yaml
kubectl -n cv-sender get pods
kubectl -n cv-sender logs deploy/cv-sender -f
```

**Gate A:** pod `Running`/`Ready`; one validation pass writes `data/preview.csv`
(one row per candidate with `status`/`reason`, per-status totals only logged);
no mail leaves the container.

## Stage 5 — Pilot verification

The pilot of 3 was already sent and verified locally (companies, recipients,
attachment and audit trail recorded on #616). In-cluster, confirm the seeded
`state.db` still lists those 3 with their `sent_at`/`message_id`, so the full run
resumes from row 4 and never duplicates them.

## Stage 6 — Flip to live (Gate B)

Edit `dry_run: false` in **both** `configs/config.yaml` and `configs/configmap.yaml`
(the T8 drift guard fails if only one is changed), then:

```bash
kubectl apply -f configs/configmap.yaml
kubectl -n cv-sender rollout restart deployment/cv-sender
```

**Gate B:** sends resume after the 3 pilot rows; `state.db` shows no duplicates;
the 400/day cap and 20s inter-send delay hold.
**Gate C:** observe one reply notification (`RyanHarrisZubair@gmail.com`) and one
daily digest.

## Rollback

See `./rollback.md`. Non-destructive stop:
`kubectl -n cv-sender scale deployment/cv-sender --replicas=0` (keeps PVC and
`state.db`). Never `kubectl delete -f configs/` — it contains `namespace.yaml` and
would cascade-delete the PVC.

## Notes

- Never commit `secret.yaml`, `cv.pdf`, `state.db` or `preview.csv`.
- The gitignored `.env` holds a live Gmail App Password in plaintext; rotate it
  and inject the fresh value only into the `cv-sender-secrets` Secret.
