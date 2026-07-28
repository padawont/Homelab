---
related_knowledge:
  - knowledge/kubernetes/harvester/
related_configs:
  - configs-and-adr/adr/0003-harvester-vm-platform.md
---

# VM Infrastructure — node-main

This directory contains VM infrastructure configuration for node-main, which runs Harvester HCI v1.8 as the hypervisor platform (see ADR 0003).

## Node Specs

| Attribute | Value |
|---|---|
| CPU | 8 cores |
| RAM | 32 GB |
| Storage | SSD |
| Harvester VIP | 192.168.111.51 |
| Setup | Single-node (no HA, no live migration) |
| Network | 192.168.111.0/24 flat VLAN |

## Services

Services that run as VMs on Harvester:
- Pterodactyl (game server management) — see ADR 0004

## Directory Layout

| Directory | Purpose |
|---|---|
| `kubernetes/` | Harvester-generated K8s manifests, VM templates, CRDs |
| `OS/` | Harvester OS configuration (harvester-config.yaml, cloud-init data) |
