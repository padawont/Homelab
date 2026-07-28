---
title: "Harvester Networking"
status: draft
date: 2026-07-28
author: padawont
tags:
  - harvester
  - networking
  - vlan
  - multus
  - kube-ovn
  - ip-pools
sources:
  - url: "https://docs.harvesterhci.io/v1.8/networking"
    title: "Harvester Networking"
  - url: "https://docs.harvesterhci.io/v1.8/networking/index"
    title: "Harvester Cluster Networks"
  - url: "https://docs.harvesterhci.io/v1.8/networking/ippool"
    title: "Harvester IP Pools"
  - url: "https://docs.harvesterhci.io/v1.8/networking/kubeovn-vpc"
    title: "Harvester VPC Networking"
last_audit_date: 2026-07-28
related_configs:
  - "configs-and-adr/node-main/vm/"
---

# Harvester Networking

## Overview

Harvester networking is built on Kubernetes CNI plugins with additional abstractions for VM networking. The network stack includes:

- **Management Network** — Default cluster network for Kubernetes pods, API access, and VM management traffic
- **Cluster Networks** — Additional network definitions for workload isolation
- **Multus CNI** — Meta-plugin that allows attaching multiple network interfaces to pods (and thus VMs)
- **NetworkAttachmentDefinitions (NADs)** — Kubernetes resources that define network configurations attached to pods
- **IP Pools** — IP address management (IPAM) for LoadBalancer services (v1.2+)
- **VPC Networking** — Virtual Private Cloud via Kube-OVN for advanced network isolation

## Management Network

The management network is created automatically during installation. It is a flat VLAN network (typically VLAN 1 or an admin-specified VLAN) that carries:

- Kubernetes pod-to-pod communication
- API server traffic
- Longhorn replica traffic (unless a dedicated storage network is configured)
- VM management traffic (VNC, serial console)
- UI and API access

The management interface uses whatever IP configuration is provided during installation (static or DHCP). In the homelab, the management interface is set to `192.168.111.51/24` with gateway `192.168.111.1`.

## Custom Cluster Networks

Harvester allows creating additional cluster networks for workload isolation. Each cluster network can use different link types:

| Link Type | Description | Use Case |
|---|---|---|
| `VLAN` | 802.1Q VLAN tagging | Traffic isolation on existing physical infrastructure |
| `VXLAN` | Overlay network over IP fabric | Traffic isolation without physical VLAN configuration |

Creating a custom cluster network requires:

1. **Define the cluster network** — Name and link type
2. **Configure the link** — Physical NIC or bridge on each node
3. **Define VLANs** — VLAN IDs that will be available on this network

```bash
# Example: Create a VLAN cluster network for data traffic
kubectl create -f - <<EOF
apiVersion: harvesterhci.io/v1beta1
kind: ClusterNetwork
metadata:
  name: vlan-data
spec:
  type: VLAN
  config:
    defaultPhysicalNIC: ens224  # Physical NIC for this network
    defaultVLANID: 100
EOF
```

## NetworkAttachmentDefinitions (NADs)

NADs define the network configuration for VM interfaces. Each NAD references a cluster network and specifies the VLAN ID, IPAM settings, and other options:

```yaml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: vlan-100
  namespace: default
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "harvester-br0",
      "vlan": 100,
      "ipam": {}
    }
```

VMs attach to NADs through their network interface configuration. A VM can have multiple interfaces, each on a different NAD.

## IP Pools for LoadBalancer

Introduced in Harvester v1.2, IP pools provide IP address management for LoadBalancer services. When a VM exposes a service of type LoadBalancer, Harvester allocates an IP from the configured pool.

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: IPPool
metadata:
  name: vm-ippool
  namespace: default
spec:
  selector:
    - vm: "my-web-vm"
  ranges:
    - subnet: 192.168.111.0/24
      start: 192.168.111.100
      end: 192.168.111.120
      gateway: 192.168.111.1
    - subnet: 192.168.111.0/24
      start: 192.168.111.200
      end: 192.168.111.210
  serviceSelector:
    - namespace: default
      service: my-vm-service
```

### IP Pool Selectors

The `serviceSelector` field controls which services get IPs from this pool. Without a selector, any LoadBalancer service in the namespace can use the pool. A `vm` selector in `spec.selector` reserves specific IPs for specific VMs.

## VPC Networking (Kube-OVN)

Harvester integrates Kube-OVN for VPC networking, providing:

- **Logical routers and switches** — Isolated L3 network per VPC
- **NAT and SNAT** — Outbound internet access from VPCs
- **Security groups** — L2-L4 firewall rules within VPCs
- **Subnets** — Multiple subnets within a single VPC

VPC networking is an advanced feature suitable for multi-tenant environments. The homelab's single flat VLAN does not require VPC networking.

## Single Flat VLAN Configuration

For the homelab, the network configuration is intentionally simple:

| Parameter | Value |
|---|---|
| VLAN | Single flat VLAN 192.168.111.0/24 |
| Management interface | Static IP 192.168.111.51/24 |
| Gateway | 192.168.111.1 |
| DNS | 192.168.111.1 |
| NTP | 0.pool.ntp.org, 1.pool.ntp.org |
| IP Pool range | 192.168.111.100-192.168.111.120 for LoadBalancer services |
| Physical NIC | ens192 |

No additional cluster networks, VXLAN overlays, or VPC are configured. All VM workloads share the same flat VLAN, which is suitable for a single-node lab environment.

## References

- [Harvester Networking Overview](https://docs.harvesterhci.io/v1.8/networking)
- [Harvester Cluster Networks](https://docs.harvesterhci.io/v1.8/networking/index)
- [Harvester IP Pools](https://docs.harvesterhci.io/v1.8/networking/ippool)
- [Harvester VPC Networking](https://docs.harvesterhci.io/v1.8/networking/kubeovn-vpc)
- [Multus CNI Documentation](https://github.com/k8snetworkplumbingwg/multus-cni)
