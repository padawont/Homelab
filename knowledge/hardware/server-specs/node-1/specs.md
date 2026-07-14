---
title: "node-1 Hardware Specs"
status: draft
author: padawont
date: 2026-07-14
tags:
  - hardware
  - server-specs
  - node-1
sources:
  - url: "https://www.asus.com/motherboards-components/motherboards/rog-strix/rog-strix-b550-i-gaming/"
    title: "ASUS ROG STRIX B550-I GAMING"
last_audit_date: 2026-07-14
related_configs:
  - "configs/nixos/node-1/"
  - "configs/kubernetes/node-1/"
---

# node-1 Hardware Specs

## System

| Field | Value |
|---|---|
| **Vendor** | ASUS |
| **Model** | ROG STRIX B550-I GAMING |
| **SKU** | SKU |
| **Firmware** | 1803 (2021-01-25) |
| **Chassis** | Desktop |
| **OS** | NixOS 26.05 (Yarara) |
| **Kernel** | Linux 6.18.34 |

## CPU

| Field | Value |
|---|---|
| **Model** | AMD Ryzen 7 5700G with Radeon Graphics |
| **Cores** | 8 (16 threads) |
| **Sockets** | 1 |
| **Max Frequency** | 3.8 GHz |
| **Min Frequency** | 1.4 GHz |
| **L1d Cache** | 256 KiB (8 instances) |
| **L1i Cache** | 256 KiB (8 instances) |
| **L2 Cache** | 4 MiB (8 instances) |
| **L3 Cache** | 16 MiB (1 instance) |
| **Microcode** | 0xa500012 |
| **Virtualization** | AMD-V |

## Memory

| Field | Value |
|---|---|
| **Total** | 30 GiB |
| **Swap** | 8 GiB (on nvme0n1p2) |

## Storage

| Device | Size | Type | Mount | Label |
|---|---|---|---|---|
| nvme0n1 | 447.1 GiB | NVMe SSD | — | — |
| nvme0n1p1 | 512 MiB | Partition | /boot | — |
| nvme0n1p2 | 8 GiB | Partition | [SWAP] | — |
| nvme0n1p3 | 100 GiB | Partition | / | — |
| nvme0n1p4 | 338.6 GiB | Partition | /home | — |
| sda | 953.9 GiB | SATA SSD | /var/lib/longhorn | longhorn |
| sdb | 465.8 GiB | SATA SSD | — | — |
| sdc | 58.6 GiB | USB/Removable | — | NixOS installer |

## Network

| Interface | MAC | IP | Purpose |
|---|---|---|---|
| `enp6s0` | `fc:34:97:65:e9:69` | 192.168.111.10/24 | Primary LAN |

## K3s Kubernetes

| Component | Version |
|---|---|
| **K3s** | v1.35.5+k3s1 |
| **Containerd** | 2.2.3-k3s1 |
| **Flannel** | (built-in) |
| **CoreDNS** | (built-in) |
| **Local Path Provisioner** | (built-in) |
| **Metrics Server** | (built-in) |

## Running Services (Kubernetes)

| Namespace | Apps |
|---|---|
| `cattle-system` | Rancher, Webhook, System Upgrade Controller |
| `cattle-fleet-system` | Fleet Controller, GitJob, HelmOps |
| `cattle-capi-system` | Cluster API Controller |
| `cattle-turtles-system` | Rancher Turtles |
| `cert-manager` | cert-manager, CA Injector, Webhook |
| `longhorn-system` | Longhorn manager, CSI plugins, UI |
| `metallb-system` | MetalLB controller, FRR-K8s, Speaker |
| `kube-system` | CoreDNS, Local Path Provisioner, Metrics Server |
