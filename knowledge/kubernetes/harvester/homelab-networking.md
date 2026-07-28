---
status: draft
date: 2026-07-28
title: "Harvester Homelab Networking"
sources:
  - url: "https://docs.harvesterhci.io/v1.8/networking"
    title: "Harvester Networking Documentation"
last_audit_date: 2026-07-28
related_configs:
  - "configs-and-adr/node-main/vm/"
---

# Harvester Homelab Networking

## Overview

The homelab uses a deliberately simple networking topology — a single flat VLAN for all traffic types. This section documents the specific networking configuration for the Harvester single-node deployment.

## Network Topology

```
                    ┌─────────────────────┐
                    │     Router/Gateway   │
                    │     192.168.111.1    │
                    └──────┬──────────────┘
                           │
                    ┌──────┴──────┐
                    │  Flat VLAN  │
                    │ 192.168.111.0/24
                    └──────┬──────┘
                           │
               ┌────────────┼────────────────────┐
               │            │                    │
      ┌────────┴──┐  ┌─────┴─────┐  ┌───────────┴──┐
      │Harvester  │  │Harvester  │  │Future       │
      │VIP/Node   │  │Node       │  │Workloads    │
      │(ens192)   │  │(expansion)│  │(IP pool)    │
      │192.168.111│  │192.168.111│  │192.168.111  │
      │.51        │  │.52-.99    │  │.100-.120    │
      └───────────┘  └───────────┘  └─────────────┘
```

## Single Flat VLAN

All traffic — management, VM workloads, and storage — shares the same VLAN and subnet:

| Parameter | Value |
|---|---|
| Subnet | 192.168.111.0/24 |
| Gateway | 192.168.111.1 |
| DNS | 192.168.111.1 |
| DHCP Range (existing network) | 192.168.111.2-192.168.111.50 |
| Harvester Static IP | 192.168.111.51 |
| IP Pool (LoadBalancer) | 192.168.111.100-192.168.111.120 |

The single flat VLAN approach is acceptable for a lab environment. In production, VLAN segregation is strongly recommended:

- **Management VLAN** — Harvester API, UI, and cluster-internal traffic
- **VM Traffic VLAN** — Workload VM traffic
- **Storage VLAN** — Longhorn replication traffic

## Harvester VIP Configuration

The Harvester VIP (Virtual IP) is `192.168.111.51`. This IP serves as the single endpoint for:

- Harvester web UI: `https://192.168.111.51`
- Kubernetes API: `https://192.168.111.51:6443`
- SSH access (if configured)
- Rancher integration endpoint

The VIP is set during installation via `harvester-config.yaml`:

```yaml
install:
  vip: 192.168.111.51
  management_interface:
    method: static
    ip: 192.168.111.51/24
    gateway: 192.168.111.1
```

In a single-node deployment, the VIP is effectively the node's IP address. In multi-node deployments, the VIP floats between nodes using kube-vip.

## Management Interface Configuration

The management network uses physical NIC `ens192` with static IP configuration:

**Install-time config:**
```yaml
install:
  management_interface:
    method: static
    ip: 192.168.111.51/24
    gateway: 192.168.111.1
    dns_nameservers:
      - 192.168.111.1
    interfaces:
      - name: ens192
```

**Post-install modification:**
Network config can be modified via the Harvester UI under **Hosts > Edit Config > Network**, or by editing the node's network configuration files over SSH.

## IP Pool for LoadBalancer

An IP pool allocates addresses from the `192.168.111.100-192.168.111.120` range to LoadBalancer services. This range is outside the existing network's DHCP range to avoid IP conflicts.

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: IPPool
metadata:
  name: homelab-pool
  namespace: default
spec:
  ranges:
    - subnet: 192.168.111.0/24
      start: 192.168.111.100
      end: 192.168.111.120
      gateway: 192.168.111.1
  serviceSelector:
    - namespace: default
```

This pool allows VMs exposing LoadBalancer services to receive routable IPs on the homelab network. For example, a web server VM could use `192.168.111.101` as its LoadBalancer IP.

## IP Allocation Summary

| Address | Purpose | Assignment |
|---|---|---|
| 192.168.111.1 | Gateway / Router | Static |
| 192.168.111.2 - .50 | DHCP pool (existing devices) | DHCP |
| 192.168.111.51 | Harvester VIP | Static (harvester-config) |
| 192.168.111.52 - .99 | Future Harvester nodes (multi-node expansion) | Static (reserved) |
| 192.168.111.100 - .120 | Harvester LoadBalancer IP pool | IPPool |
| 192.168.111.121 - .254 | Reserved | Unallocated |

## DNS Configuration

- **Primary DNS**: 192.168.111.1 (router)
- **Internal DNS resolution**: Harvester does not run its own DNS server. VM hostnames are resolved via the router's DNS or external registries.
- **External DNS**: Configured upstream (e.g., 8.8.8.8 as fallback on the router)
- **VM DNS**: Passed to VMs via DHCP or cloud-init networkData

## NTP Configuration

- **NTP Servers**: `0.pool.ntp.org`, `1.pool.ntp.org`
- **Configured in**: `harvester-config.yaml` at install time
- **Verification**: `timedatectl status` or `chronyc sources` over SSH

## Future Expansion

If the homelab grows to multiple nodes:

1. **Dedicated management VLAN** — Isolate cluster traffic to VLAN 10 (or similar)
2. **VM traffic VLAN** — VLAN 100 for workload VMs
3. **Storage VLAN** — VLAN 200 with dedicated NIC for Longhorn replication
4. **VLAN tagging** — Configure on the physical switch and in Harvester cluster networks
5. **VIP migration** — The VIP automatically floats to the active management node (kube-vip handles failover)

For the current single-node deployment, the flat VLAN is sufficient and simpler to manage.

## References

- [Harvester Networking Overview](https://docs.harvesterhci.io/v1.8/networking)
- [Harvester Installation Config](https://docs.harvesterhci.io/v1.8/install/harvester-config)
- [Harvester IP Pools](https://docs.harvesterhci.io/v1.8/networking/ippool)
