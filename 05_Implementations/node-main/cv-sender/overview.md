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
  - "./02_Knowledge/technologies/kubernetes/concepts/deployments.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/secrets.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/storage.md"
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
- Secret `cv-sender-secrets`, populated from an untracked `secret.yaml`
  (never committed to git), holding `GMAIL_APP_PASSWORD`; ConfigMap
  `cv-sender-config` from the tracked `configs/config.yaml`.
- The CV copied onto the PVC at `cv/cv.pdf`; the `subPath` mount exposes it in
  the pod at `/app/config/cv/cv.pdf`.
- Outbound HTTPS to the TARGIT view and `selskabsinfo.dk`, plus SMTP/IMAP access
  to the sending mailbox `cvsenderworkonly@gmail.com`; notifications still go
  to `RyanHarrisZubair@gmail.com`.

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
# Apply per file in dependency order — a directory apply (`-f configs/`) is
# wrong on three counts: config.yaml has no apiVersion/kind (not a manifest);
# secret.yaml.example has an unrecognised extension (`.example`), so kubectl
# silently skips it and the Secret is never created by a directory apply;
# and lexical order (configmap → deployment → namespace → pvc) does not
# respect the namespace → Secret → ConfigMap → PVC → Deployment order.
kubectl apply -f configs/namespace.yaml
kubectl apply -f configs/secret.yaml    # untracked, from secret.yaml.example
kubectl apply -f configs/configmap.yaml
kubectl apply -f configs/pvc.yaml
kubectl apply -f configs/deployment.yaml
```

### Post-deploy verification

```bash
kubectl -n cv-sender get pods
kubectl -n cv-sender logs deploy/cv-sender -f
```

Expect the `cv-sender` pod `Running`/`Ready`. With `dry_run: true` the worker
performs a single validation pass at startup — scraping the TARGIT view,
classifying each candidate and writing `data/preview.csv` with per-status
counts — then idles. No mail (including the daily digest and reply
notifications) leaves the container, and the live view is not re-scraped on
every poll.

## Configuration

| Resource | Name | Notes |
|---|---|---|
| Namespace | `cv-sender` | |
| Secret | `cv-sender-secrets` | holds `GMAIL_APP_PASSWORD` |
| ConfigMap | `cv-sender-config` | from `configs/config.yaml` |
| PVC | `cv-sender-data` | 1Gi — `state.db`, caches, `cv/cv.pdf` |
| Deployment | `cv-sender` | 1 replica, always-on, image `cv-sender:0.1` |

- **Source view**: `https://ledelsesinformation.aarhuskommune.dk/#vfs://global/AARHUS-I-TAL/UDDANNELSE_I_TAL-Erhvervspraktik-Virksomhedsliste.xview`
  — a Blazor WebAssembly view, client-rendered and anonymous. The grid is
  row-capped, so the worker uses **Export to Excel** rather than DOM scraping.
  The toolbar's export button is `display: none`, so the scraper un-hides it
  before clicking. The full list (~37,319 rows) is exported unfiltered; Branche
  filtering happens in Python, not the browser.
- **Export readiness**: the view hydrates its data model after the grid first
  renders, so a click too early downloads a 0-byte workbook (the `/Embed` URL
  reliably does this, but the non-Embed URL is not immune). The scraper waits
  for the rendered header and row-total before the first click, then retries
  until a non-empty workbook lands — a slow TARGIT hydration can still exhaust
  that retry budget.
- **Workbook**: the company data is on the `Tabel` sheet (the others are empty
  or small summaries). openpyxl 3.1.5 rejects the `defaultColWidthPt` attribute
  TARGIT emits, so `normalize` re-packages the `.xlsx` in memory (stripping it)
  before parsing — the file on disk is never modified.
- **Enrichment**: `selskabsinfo.dk` then
  `https://selskabsinfo.dk/virksomheder-i/aarhus`; if no email is found the
  company is skipped. Both sit behind a Vercel bot challenge and need the real
  browser.
- **CV**: on the PVC at `cv/cv.pdf`, exposed in-pod at `/app/config/cv/cv.pdf`.
- **Rate**: 400/day, 20s delay between sends, 300s poll interval.
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
  `cvsenderworkonly@gmail.com`; notifications go to
  `RyanHarrisZubair@gmail.com`.
- **Backup**: copy `state.db` off the PVC before destructive changes.
- Rollback is documented in `./rollback.md`.
