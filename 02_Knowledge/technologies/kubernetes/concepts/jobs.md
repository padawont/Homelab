---
title: "Jobs and CronJobs in Kubernetes"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, workloads, jobs, cronjob, batch]
sources:
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/job/"
    title: "Kubernetes Jobs"
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/"
    title: "Kubernetes CronJobs"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/concepts/deployments.md"
---

# Jobs and CronJobs in Kubernetes

## Overview

A Job runs one or more pods to completion — backups, migrations, batch processing. Unlike Deployments, the Job tracks success: it finishes when the required number of pods complete successfully. A CronJob wraps a Job and schedules it on a cron expression. In a homelab, Jobs are the natural fit for scheduled database backups and maintenance tasks.

## Details

### Completions and parallelism

- `completions` — how many successful pods the Job needs in total.
- `parallelism` — how many pods run at the same time.
- Default `completions: 1` and `parallelism: 1`; for a fan-out batch, raise parallelism and keep completions high.

### backoffLimit

Pods that fail are restarted by the Job up to `backoffLimit` times (default 6) before the Job is marked Failed. Use `activeDeadlineSeconds` to cap total runtime of the Job itself.

### TTL

`ttlSecondsAfterFinished` auto-deletes finished Jobs (and their pods) after the given time. Set it on one-shot Jobs so completed pods do not accumulate on small homelab nodes.

### CronJob schedule syntax

Standard 5-field cron: `minute hour day-of-month month day-of-week` (UTC). Examples: `0 3 * * *` runs daily at 03:00 UTC; `*/15 * * * *` every 15 minutes. The CronJob creates a Job per scheduled run; `startingDeadlineSeconds` controls how late a missed run may start.

Example — abstract:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 3 * * *"
  startingDeadlineSeconds: 300
  jobTemplate:
    spec:
      backoffLimit: 3
      ttlSecondsAfterFinished: 3600
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: postgres:16
              command: ["pg_dump", "-h", "db", "-U", "backup", "app"]
```

Note: Job pod templates require `restartPolicy: Never` or `OnFailure` (never `Always`).

## Sources / Further Reading

- [Kubernetes Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [Kubernetes CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Deployments note](./02_Knowledge/technologies/kubernetes/concepts/deployments.md)
