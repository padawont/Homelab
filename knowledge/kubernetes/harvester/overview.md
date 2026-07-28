---
status: draft
date: 2026-07-28
title: "Harvester HCI Overview"
sources:
  - url: "https://docs.harvesterhci.io/v1.8"
    title: "Harvester Documentation v1.8"
  - url: "https://github.com/harvester/harvester"
    title: "Harvester GitHub Repository"
last_audit_date: 2026-07-28
related_configs:
  - "configs-and-adr/adr/0003-harvester-vm-platform.md"
  - "configs-and-adr/node-main/vm/"
---

# Harvester HCI Overview

## What Is Harvester?

Harvester is an open-source hyperconverged infrastructure (HCI) platform built on Kubernetes. It runs as a bare-metal operating system (replacing a traditional Linux distribution like NixOS) and provides VM management, distributed storage, and container runtime capabilities from a single management interface. Unlike traditional virtualization platforms, Harvester renders VMs and storage as first-class Kubernetes resources managed through the Kubernetes API and a dedicated web UI.

The project is maintained by SUSE (the same organization behind Rancher) and is designed to integrate natively with Rancher's Virtualization Management feature.

## Architecture

Harvester is composed of four major layers:

### 1. Operating System — Elemental SLE Micro 6.2

Harvester nodes boot from the Harvester ISO, which is built on SUSE Linux Enterprise Micro (SLE Micro) 6.2 via the Elemental toolkit. SLE Micro is an immutable, container-optimized OS with a read-only root filesystem. Package management is handled through container images and system upgrades are performed atomically via an A/B partition scheme. This is the OS that replaces the traditional Linux distribution on the host — there is no package manager for ad-hoc installations.

### 2. Kubernetes

Harvester runs an embedded Kubernetes cluster on every node. The control plane is deployed as static pods managed by kubelet. In a multi-node configuration, three nodes act as control plane + worker (management role). Single-node deployments (like the homelab) run all control plane components on the one node.

### 3. KubeVirt (VM Runtime)

KubeVirt is the virtualization add-on that allows Kubernetes to run and manage VMs alongside containers. It introduces a new resource type — `VirtualMachine` (VM) and `VirtualMachineInstance` (VMI) — which are Kubernetes-native custom resources. KubeVirt uses QEMU/KVM as the hypervisor and libvirt for VM lifecycle management. Every VM runs as a pod backed by a qemu process, inheriting Kubernetes scheduling, networking (via Multus CNI), and storage (via Longhorn CSI).

### 4. Longhorn (Distributed Storage)

Longhorn is a lightweight, cloud-native distributed block storage system for Kubernetes. Harvester bundles Longhorn as its default storage backend, providing:

- Volume provisioning via PVCs and StorageClasses
- Synchronous replication across nodes (default 3 replicas, set to 1 for single-node)
- Built-in backup to NFS or S3 targets
- Volume snapshots and cloning
- Incremental backups and restore

## Key Features

- **Unified UI** — Web-based dashboard for VMs, volumes, images, networks, and hosts
- **REST API** — Full Kubernetes API compatibility plus Harvester-specific CRDs
- **VM Import** — Import existing VMs from VMware vSphere (OVA/OVF) or disk images
- **Live Migration** — Move running VMs between nodes without downtime (requires 2+ nodes)
- **Backup & Restore** — Scheduled and on-demand VM backups to NFS or S3 targets
- **Cloud-native Integration** — Harvester nodes can provision Kubernetes clusters via the Rancher node driver, and VMs can be used as K8s nodes
- **Custom Networking** — Multiple cluster networks (VLAN, VXLAN), IP pools for LoadBalancer services, VPC via Kube-OVN

## Use Cases in the Homelab

In the homelab, Harvester serves as the VM platform for running persistent workloads that require full OS virtualization:

- Replace the existing VM hosting approach with a Kubernetes-native management interface
- Host application VMs with persistent storage backed by Longhorn
- Integrate with Rancher for unified cluster and VM management from a single pane of glass
- Provide LoadBalancer services to VMs via Harvester IP pools

The deployment is single-node (node-1), so features requiring multiple nodes (HA, live migration, witness node) are unavailable. Storage replication is set to 1 replica since there is only one storage backend.

## Version

The homelab targets Harvester **v1.8.1** (latest stable as of July 2026).

## References

- [Harvester Documentation v1.8](https://docs.harvesterhci.io/v1.8)
- [Harvester GitHub Repository](https://github.com/harvester/harvester)
- [KubeVirt Documentation](https://kubevirt.io/user-guide/)
- [Longhorn Documentation](https://longhorn.io/docs/)
- [Elemental Documentation](https://elemental.docs.rancher.com/)
