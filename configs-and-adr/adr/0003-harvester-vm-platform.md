---
adr: 3
title: "Adopt Harvester HCI as VM Infrastructure Platform"
author: runicengines
status: proposed
topic: vm-platform
date: 2026-07-28
date-proposed: 2026-07-28
history: "2026-07-28: Created"
related_knowledge:
  - knowledge/kubernetes/harvester/
related_configs:
  - configs-and-adr/node-main/vm/
---

# ADR 0003 — Adopt Harvester HCI as VM Infrastructure Platform

## Context

The homelab needs a hypervisor / VM management platform to host services such as Pterodactyl (game server management). Currently, node-main runs NixOS with K3s and Longhorn, which handles containerized workloads but provides no native VM lifecycle management. Adding VM hosting requires a dedicated HCI (Hyperconverged Infrastructure) platform.

Hardware constraints: 8 cores, 32 GB RAM, single SSD, UEFI boot (required by Harvester v1.8). Networking is a single flat VLAN (192.168.111.0/24). The existing Rancher instance (running on the K3s cluster) should manage the VM platform to maintain a unified management plane.

## Decision

Use **Harvester HCI v1.8** as the VM infrastructure platform.

Rationale:
- **Native Rancher integration** — Harvester can be imported into Rancher's Virtualization Management, providing a single UI/API for both containers (K3s) and VMs
- **Kubernetes-native** — VMs are managed as Kubernetes CRDs, aligning with the existing K8s-first approach
- **Built-in Longhorn storage** — provides replicated block storage for VMs without additional components
- **Built-in monitoring** — Grafana and Prometheus are bundled for cluster observability
- **Apache 2.0 license** — no licensing costs or restrictions

Acceptable trade-offs:
- Replaces NixOS on node-main (loses declarative OS config)
- Higher resource overhead vs. bare-metal hypervisors
- Single-node deployment means no HA, no live migration, storage replica count must be 1

### Configuration values

| Parameter | Value |
|---|---|
| Harvester VIP | 192.168.111.51 |
| Hostname | harvester |
| Node IP | 192.168.111.51/24 |
| Gateway | 192.168.111.1 |
| DNS | 192.168.111.1 |
| Cluster CIDR | 10.52.0.0/16 |
| Service CIDR | 10.53.0.0/16 |
| Cluster DNS | 10.53.0.10 |
| Storage replica | 1 (single-node) |
| Management interface | ens192 (single NIC) |
| Install device | /dev/sda |

## Consequences

**Positive:**
- Unified VM + K8s management through Rancher
- Built-in monitoring and storage
- Single platform for both container and VM workloads
- Harvester VMs support cloud-init, enabling declarative provisioning

**Negative:**
- Loses NixOS declarative OS configuration — node-main OS is now managed via Harvester's UI/API
- Higher resource overhead than Proxmox or bare NixOS
- No high availability or live migration on a single node
- Single point of failure for all VM workloads

## Alternatives Considered

### Proxmox VE
- **Pros**: Lower overhead, mature, larger community, ZFS storage
- **Cons**: No native K8s/Rancher integration — requires separate management plane; Terraform provider is third-party

### oVirt / RHV
- **Pros**: Enterprise-grade, Active Directory integration
- **Cons**: End-of-life risk (Red Hat Virtualization EOL announced); high complexity for single-node; no native K8s integration

### XCP-ng / XenServer
- **Pros**: Stable, Xen-based
- **Cons**: Smaller ecosystem, no native K8s/Rancher integration, less familiar tooling

## Related Decisions

- **ADR 0004** (Pterodactyl VM Hosting) depends on this decision — Pterodactyl will run as a VM on Harvester
