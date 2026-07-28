---
title: "Harvester HCI"
status: draft
author: padawont
date: 2026-07-28
tags:
  - harvester
  - hyperconverged
  - kubernetes
  - virtualization
  - hci
sources:
  - url: "https://docs.harvesterhci.io/v1.8"
    title: "Harvester Documentation v1.8"
last_audit_date: 2026-07-28
related_configs:
  - "configs-and-adr/node-main/vm/"
related_knowledge:
  - "knowledge/kubernetes/rancher/"
---

# Harvester HCI

Reference notes on [Harvester HCI](https://harvesterhci.io/) — an open-source hyperconverged infrastructure platform built on Kubernetes and KubeVirt. Harvester replaces traditional virtualization stacks (VMware vSphere, Proxmox) with a Kubernetes-native approach backed by Longhorn for distributed storage and Elemental SLE Micro for the underlying OS.

These notes cover architecture, installation, VM operations, storage, networking, Rancher integration, monitoring, and advanced features for Harvester v1.8.1.

## Prerequisites

- [Kubernetes Fundamentals](../) — basic K8s concepts
- [Rancher](../rancher/) — Rancher multi-cluster management, used for Harvester integration
- [ADR 0003 — Harvester VM Platform](../../../configs-and-adr/adr/0003-harvester-vm-platform.md) — decision record for choosing Harvester

## Architecture

| File | Description |
|---|---|
| [overview.md](overview.md) | Harvester architecture — KubeVirt, Longhorn, Elemental SLE Micro, use cases |

## Installation

| File | Description |
|---|---|
| [installation.md](installation.md) | Hardware requirements, install methods, harvester-config YAML, single-node setup |

## Host Operations

| File | Description |
|---|---|
| [host-management.md](host-management.md) | Node roles, maintenance mode, multi-disk, NTP, CloudInit CRD, certificate rotation |

## VM Operations

| File | Description |
|---|---|
| [vm-management.md](vm-management.md) | Create/edit/clone/delete VMs, live migration, backup/restore, snapshots, hotplug, resource tuning |

## Storage

| File | Description |
|---|---|
| [storage-volumes.md](storage-volumes.md) | PVCs via Longhorn CSI, StorageClasses, volume operations, storage network |

## Networking

| File | Description |
|---|---|
| [networking.md](networking.md) | Mgmt VLAN, custom cluster networks, Multus NADs, IP pools, VPC/Kube-OVN |
| [homelab-networking.md](homelab-networking.md) | Lab-specific networking — single flat VLAN, VIP 192.168.111.51, IP pool config |

## Rancher Integration

| File | Description |
|---|---|
| [rancher-integration.md](rancher-integration.md) | Import into Virtualization Management, node driver, CSI driver, cloud provider |

## Monitoring

| File | Description |
|---|---|
| [monitoring-logging.md](monitoring-logging.md) | rancher-monitoring addon, Prometheus/Grafana dashboards, Alertmanager |

## Advanced

| File | Description |
|---|---|
| [advanced-features.md](advanced-features.md) | Settings reference, addons, witness node, vGPU, CloudInit CRD, Longhorn V2 |
