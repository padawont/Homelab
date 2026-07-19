---
title: "Kiwix"
status: completed
tags:
  - kiwix
  - offline
  - wikipedia
  - zim
sources:
  - url: "https://www.kiwix.org/en/"
    title: "Kiwix — Offline Browser"
  - url: "https://github.com/kiwix/kiwix-tools"
    title: "kiwix/kiwix-tools — GitHub"
last_audit_date: 2026-07-18
related_knowledge:
  - "kubernetes/deployments"
  - "kubernetes/services"
  - "kubernetes/storage"
  - "kubernetes/jobs"
related_configs:
  - "configs/node-main/kubernetes/kiwix.yaml"
  - "configs/node-main/kubernetes/kiwix-copy-job.yaml"
---

# Kiwix

## Overview

Kiwix is a free and open-source offline content browser. It reads ZIM files — highly compressed archives of web content — and serves them over HTTP so any device on the local network can access the content without an internet connection.

Kiwix is primarily used to distribute Wikipedia offline, but it supports any content packaged in the ZIM format (Wiktionary, Wikisource, Stack Exchange dumps, TED talks, etc.).

> **Source**: [Kiwix — Offline Browser](https://www.kiwix.org/en/)

## ZIM Format

ZIM is an open file format designed for storing web content in a single compressed file. Key characteristics:

- **Single file** — An entire website (thousands of pages, images, assets) is bundled into one `.zim` file
- **Compressed** — Uses zstd compression (default since 2021); also supports LZMA2 via xz for backward compatibility
- **Random access** — Allows seeking into specific articles without decompressing the entire file
- **Metadata** — Stores title, language, date, creator, and description in the file header

ZIM files are the standard format for Kiwix and are used by the offline Wikipedia distribution project.

## Wikipedia ZIM Files

English Wikipedia is available in three variants from `download.kiwix.org/zim/wikipedia/`:

| Variant | Description | Approx Size |
|---|---|---|
| `maxi` | Full articles with images | ~115 GB |
| `nopic` | Full articles without images | ~48 GB |
| `mini` | Article introductions only | ~12 GB |

## Architecture

Kiwix server (kiwix-serve) follows a simple architecture:

```
┌─────────────┐     HTTP :8080
│  kiwix-serve │◄──────────────── Client browser
│  container   │
├─────────────┤
│   /data/     │
│  *.zim files │
└─────────────┘
```

- kiwix-serve is a single static binary that reads ZIM files and serves them over HTTP
- No database, no external dependencies
- All ZIM files in the `/data` directory are served automatically via globbing
- The service is stateless with respect to the binary — all state is in the ZIM files on the volume

## Deployment on Homelab

Kiwix is deployed on the node-1 K3s cluster as a single-replica Deployment in the `kiwix` namespace. The deployment uses:

- **Container image**: `ghcr.io/kiwix/kiwix-serve` (kiwix-tools 3.8.2, libzim 9.5.0)
- **Storage**: Longhorn PVC `kiwix-data` (200Gi) mounted at `/data`
- **Service**: LoadBalancer with static IP 192.168.111.101, port 80 → container port 8080
- **ZIM file**: `wikipedia_en_all_maxi_2025-08.zim` (~111 GB)

The Kubernetes manifests are in `configs/node-main/kubernetes/kiwix.yaml`. ZIM files are initially copied from the node-1 host path `/home/nixos/kiwix-zim` to the PVC via a one-shot Job (`configs/node-main/kubernetes/kiwix-copy-job.yaml`).
