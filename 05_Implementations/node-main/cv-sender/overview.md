---
title: "cv sender outreach worker"
status: draft
author: "padawont"
date: 2026-10-13
tags: [kubernetes, automation, playwright, email, outreach]
technologies: [python, playwright, kubernetes, sqlite, smtplib, imaplib]
related_docs:
  - "./04_ADRs/612-cv-sender.md"
  - "./05_Implementations/node-main/k3s/overview.md"
references:
  online:
    - url: "https://playwright.dev/python/docs/docker"
      title: "Playwright Python — Docker"
    - url: "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/"
      title: "Kubernetes Deployments"
  repo:
    - "./04_ADRs/612-cv-sender.md"
    - "./rollback.md"
node: node-main
---

# cv sender outreach worker

A containerised, long-running Python worker on the `node-main` k3s cluster. It
scrapes Aarhus Kommune's *Erhvervspraktik* company list, keeps computer-branch
companies in Viby J / Aarhus N / Aarhus C / Aarhus V, validates and enriches
emails, sends one Danish *Folkeskolepraktik uge 45* application with the CV
attached, and monitors replies. Governed by ADR-612 (`./04_ADRs/612-cv-sender.md`).

## Prerequisites

- Working single-node k3s cluster on `node-main` — see
  `./05_Implementations/node-main/k3s/overview.md`.
- Docker on the build host to produce the `cv-sender:0.1` image.
- Secret `cv-sender-secrets` holding `GMAIL_APP_PASSWORD`; ConfigMap
  `cv-sender-config` from `configs/config.yaml` (never committed to git).
- The CV file copied onto the PVC at `/app/config/cv/cv.pdf`.
- Outbound HTTPS to the TARGIT view and `selskabsinfo.dk`, plus SMTP/IMAP access
  to the mailbox `RyanHarrisZubair@gmail.com`.

## Deployment

### Pre-deploy checks

```bash
kubectl config current-context      # node-main k3s
kubectl get nodes
```

Confirm `configs/config.yaml` has `dry_run: true` for the first rollout, and that
the CV is present locally before copying it onto the PVC.

### Deploy

Build the image on the host, import it into k3s `containerd`, then apply the
manifests in dependency order (namespace → Secret → ConfigMap → PVC → Deployment):

```bash
docker build -t cv-sender:0.1 .
docker save cv-sender:0.1 | sudo k3s ctr images import -
kubectl apply -f configs/
```

### Post-deploy verification

```bash
kubectl -n cv-sender get pods
kubectl -n cv-sender logs deploy/cv-sender -f
```

Expect the `cv-sender` pod `Running`/`Ready`; with `dry_run: true` the logs show
candidates selected but no mail sent.

## Configuration

| Resource | Name | Notes |
|---|---|---|
| Namespace | `cv-sender` | |
| Secret | `cv-sender-secrets` | holds `GMAIL_APP_PASSWORD` |
| ConfigMap | `cv-sender-config` | from `configs/config.yaml` |
| PVC | `cv-sender-data` | 1Gi — holds `state.db` + caches |
| Deployment | `cv-sender` | 1 replica, always-on, image `cv-sender:0.1` |

- **Source view**: `https://ledelsesinformation.aarhuskommune.dk/Embed#vfs://global/AARHUS-I-TAL/UDDANNELSE_I_TAL-Erhvervspraktik-Virksomhedsliste.xview`
  — a Blazor WebAssembly view, client-rendered and anonymous. The grid is
  row-capped, so the worker uses **Export to Excel** rather than DOM scraping.
- **Enrichment**: `selskabsinfo.dk` then
  `https://selskabsinfo.dk/virksomheder-i/aarhus`; if no email is found the
  company is skipped. Both sit behind a Vercel bot challenge and need the real
  browser.
- **CV**: `/app/config/cv/cv.pdf`, copied onto the PVC at deploy time.
- **Rate**: 400/day, 20s delay between sends.
- **Rollout**: `dry_run: true` → pilot of 3 → full run, all driven from
  `configs/config.yaml`.

## Operations

```bash
# Scale / restart
kubectl -n cv-sender scale deployment/cv-sender --replicas=0
kubectl -n cv-sender rollout restart deployment/cv-sender

# Logs
kubectl -n cv-sender logs deploy/cv-sender -f
```

- **State**: idempotent SQLite `state.db` on the PVC so restarts and rolling
  updates resume without double-sending.
- **Monitoring**: the worker polls IMAP for replies and bounces on
  `RyanHarrisZubair@gmail.com`; notifications go to the same address.
- **Backup**: copy `state.db` off the PVC before destructive changes.
- Rollback is documented in `./rollback.md`.
