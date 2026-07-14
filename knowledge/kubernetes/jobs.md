---
title: "Jobs and CronJobs"
status: draft
author: padawont
date: 2026-06-18
tags:
  - kubernetes
  - workloads
  - jobs
  - cronjobs
sources:
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/job/"
    title: "Jobs — Kubernetes Documentation"
  - url: "https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/"
    title: "CronJob — Kubernetes Documentation"
last_audit_date: 2026-06-18
---

# Jobs and CronJobs (Jobs/CronJobs)

## Overview

A Job creates one or more pods and ensures they run to completion successfully. Jobs are for batch processing, data migration, backups, and any task that runs to completion rather than staying running. CronJobs create Jobs on a time-based schedule.

## Job Spec

Key fields: `completions` (how many successful pod completions are needed), `parallelism` (how many pods can run concurrently), `backoffLimit` (max retries before marking Job as failed, default 6), `activeDeadlineSeconds` (hard time limit for the Job), `ttlSecondsAfterFinished` (automatically clean up finished Jobs).

## CronJob Spec

CronJobs add scheduling on top of Jobs. Key fields: `schedule` (standard cron syntax, five fields), `jobTemplate` (the Job spec to create), `concurrencyPolicy` (Allow, Forbid, Replace), `startingDeadlineSeconds` (how long to start on a missed schedule), `successfulJobsHistoryLimit` / `failedJobsHistoryLimit` (how many completed Jobs to retain).

## Job Example

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi
spec:
  completions: 1
  parallelism: 1
  backoffLimit: 4
  template:
    spec:
      containers:
      - name: pi
        image: perl:5.34
        command: ["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: Never
```

## CronJob Example

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hello
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox:1.28
            command: ["echo", "Hello from CronJob"]
          restartPolicy: OnFailure
```

## Cross-links

- [`pods.md`](./pods.md)
