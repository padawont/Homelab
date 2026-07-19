---
title: "Kiwix Deployment Procedure"
status: completed
author: padawont
date: 2026-07-18
tags:
  - kiwix
  - deployment
  - k3s
  - kubernetes
sources:
  - url: "https://github.com/kiwix/kiwix-tools"
    title: "kiwix/kiwix-tools — GitHub"
  - url: "https://kiwix-tools.readthedocs.io/en/stable/kiwix-serve.html"
    title: "kiwix-serve CLI Documentation"
  - url: "https://download.kiwix.org/zim/wikipedia/"
    title: "Kiwix ZIM Download"
last_audit_date: 2026-07-18
related_configs:
  - "configs/node-main/kubernetes/kiwix.yaml"
  - "configs/node-main/kubernetes/kiwix-copy-job.yaml"
---

# Kiwix Deployment Procedure

## Overview

Step-by-step guide to deploy kiwix-serve on the node-1 K3s cluster, serving English Wikipedia offline via a LoadBalancer at 192.168.111.101.

## Prerequisites

- kubectl configured to access the node-1 K3s cluster
- SSH access to node-1 (192.168.111.10)
- Sufficient disk space for ZIM file download and Longhorn PVC

## Step 1: Download ZIM File

Download the desired ZIM file from the [Kiwix ZIM library](https://download.kiwix.org/zim/wikipedia/). For English Wikipedia full with images:

```
wget https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2025-08.zim
```

Note: The official kiwix-serve Docker image (3.8.2, libzim 9.5.0) does NOT support ZIM v4.6 files (mid-2025+). A nightly binary with libzim 9.8.1 is required — see Step 3.

## Step 2: Transfer ZIM to node-1

Copy the ZIM file to the node-1 host path expected by the copy Job:

```
scp wikipedia_en_all_maxi_2025-08.zim nixos@192.168.111.10:/home/nixos/kiwix-zim/
```

The directory `/home/nixos/kiwix-zim` must exist on node-1 before copying:

```
ssh nixos@192.168.111.10 "mkdir -p /home/nixos/kiwix-zim"
```

## Step 3: Install Nightly kiwix-serve Binary

The official kiwix-serve Docker image (libzim 9.5.0) does not support ZIM v4.6 files. A nightly binary with libzim 9.8.1 is required:

```bash
ssh nixos@192.168.111.10
curl -sL 'https://mirror.download.kiwix.org/nightly/2026-07-18/kiwix-tools_linux-x86_64-2026-07-18.tar.gz' -o /tmp/kiwix-nightly.tar.gz
cd /tmp && tar xzf kiwix-nightly.tar.gz
sudo cp kiwix-tools_linux-x86_64-2026-07-18/kiwix-serve /opt/kiwix-serve
sudo chmod +x /opt/kiwix-serve
```

## Step 4: Generate Library XML

kiwix-serve with libzim 9.8.1 requires a library XML to serve large ZIM files:

```bash
ssh nixos@192.168.111.10
echo '<?xml version="1.0" encoding="UTF-8"?><library></library>' > /tmp/library.xml
/tmp/kiwix-tools_linux-x86_64-2026-07-18/kiwix-manage /tmp/library.xml add /home/nixos/kiwix-zim/wikipedia_en_all_maxi_2025-08.zim
sudo cp /tmp/library.xml /opt/kiwix-library.xml
```

## Step 5: Deploy kiwix Namespace and PVC

```
kubectl apply -f configs/node-main/kubernetes/kiwix.yaml
```

This creates:
- `kiwix` namespace
- `kiwix-data` PersistentVolumeClaim (200Gi, Longhorn storage class)
- `kiwix` Deployment (single replica, uses nightly binary from hostPath)
- `kiwix` Service (LoadBalancer, 192.168.111.101:80)

## Step 6: Copy ZIM to PVC via Job

```
kubectl apply -f configs/node-main/kubernetes/kiwix-copy-job.yaml
```

This runs a one-shot Job (`copy-zim`) in the `kiwix` namespace that copies all `.zim` files from the host path `/home/nixos/kiwix-zim` to the PVC at `/data`.

Monitor the copy:

```
kubectl -n kiwix logs job/copy-zim
```

Expected output:
```
total <size>
-rw-r--r--  ...  wikipedia_en_all_maxi_2025-08.zim
```

## Step 7: Verify Deployment

Check pod status:

```
kubectl -n kiwix get pods
```

Wait for the pod to reach `Running` and `READY 1/1`. Verify the Service IP:

```
kubectl -n kiwix get svc kiwix
```

The `EXTERNAL-IP` should show `192.168.111.101`. Verify HTTP response:

```
curl -s -o /dev/null -w "%{http_code}" http://192.168.111.101/
```

Expected: `200`. Open http://192.168.111.101/ in a browser to confirm Wikipedia content loads.

## Step 8: Update ZIM Files

To switch to a different ZIM file:

1. Download and transfer the new ZIM file to `/home/nixos/kiwix-zim` on node-1
2. Delete the old copy Job: `kubectl -n kiwix delete job copy-zim`
3. Re-apply the copy Job to copy the new file: `kubectl apply -f configs/node-main/kubernetes/kiwix-copy-job.yaml`
4. Regenerate the library XML on node-1: `echo '<?xml version="1.0"?><library></library>' > /tmp/zl.xml && /tmp/kiwix-manage /tmp/zl.xml add /home/nixos/kiwix-zim/*.zim && sudo cp /tmp/zl.xml /opt/kiwix-library.xml`
5. Delete the running pod to force a restart: `kubectl -n kiwix delete pod -l app=kiwix`

To serve multiple ZIM files, pass all paths to `kiwix-manage add` and they will all be added to the library XML.

## Verification Checklist

- [ ] Pod is `Running` with `READY 1/1`
- [ ] Service has `EXTERNAL-IP` 192.168.111.101
- [ ] `curl http://192.168.111.101/` returns HTTP 200
- [ ] Wikipedia content renders in browser
- [ ] Liveness and readiness probes are green (`kubectl -n kiwix describe pod`)
- [ ] Resource usage is within limits (CPU 1000m, memory 2Gi)
