---
title: "Harvester Host Management"
status: draft
date: 2026-07-28
author: padawont
tags:
  - harvester
  - host
  - node-management
  - single-node
sources:
  - url: "https://docs.harvesterhci.io/v1.8/host"
    title: "Harvester Host Management"
  - url: "https://docs.harvesterhci.io/v1.8/host/"
    title: "Managing Hosts"
last_audit_date: 2026-07-28
related_configs:
  - "configs-and-adr/node-main/vm/"
---

# Harvester Host Management

## Node Roles

Harvester nodes have three possible roles:

| Role | Description |
|---|---|
| **Management** | Runs the Kubernetes control plane (etcd, API server, scheduler, controllers) and standard workloads. Every node in a multi-node cluster has this role by default. |
| **Worker** | Runs workloads only — no control plane components. Useful for scaling compute independently from control plane capacity. |
| **Witness** | Runs etcd only — provides etcd quorum without running KubeVirt or Longhorn. Used to maintain HA in a 2-node cluster where a third etcd member is needed. |

In a single-node deployment, the one node fills the management role by default and runs all components.

## Maintenance Mode

Maintenance mode drains all VMs and pods from a node, making it safe for hardware maintenance:

1. In the Harvester UI, navigate to **Hosts**
2. Click the menu on the target node and select **Enable Maintenance Mode**
3. Running VMs are live-migrated to other nodes (if available) or shutdown
4. The node is cordoned and drained

**Single-node limitation:** Maintenance mode cannot complete because no other node exists to receive migrated VMs. Any attempt to enable maintenance mode will fail with VMs unable to evacuate. VMs must be shutdown manually before maintenance.

## Multi-Disk Management

Harvester supports attaching multiple disks to a node for Longhorn storage:

### Adding a Disk

1. Attach a physical disk to the node
2. SSH into the node and partition/format the disk (Harvester uses the full disk, no partitioning required)
3. In the Harvester UI, navigate to **Hosts > Edit Config > Disks**
4. Add the new disk path (e.g., `/dev/sdb`)

### Storage Tags

Tags allow you to control which disks Longhorn uses for specific volumes:

```yaml
# Example: tag a fast SSD for high-performance workloads
tags:
  - fast
  - ssd
```

Volumes can be scheduled on specific tags via a StorageClass:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "1"
  diskSelector: "fast,ssd"
```

In a single-node deployment, disk tags are less critical since all disks are on the same node, but they remain useful for distinguishing between SSD and HDD within the same node.

### Removing a Disk

Before removing a disk, ensure all replicas on that disk are migrated to other disks. In a single-node setup, replicas must be deleted (there is no other disk to migrate to). Back up the volume data first.

## NTP Configuration

Time synchronization is critical for Harvester — etcd and Longhorn both depend on accurate clocks:

- Configure NTP during installation via `harvester-config.yaml` (`os.ntp_servers`)
- Modify NTP servers post-install via the UI under **Settings > NTP**
- SSH into the node and check status: `timedatectl status`

The homelab uses `0.pool.ntp.org` and `1.pool.ntp.org` as NTP servers.

## CloudInit CRD

Harvester provides a `CloudInit` custom resource that stores cloud-init user-data and network-data for VMs. Unlike regular Kubernetes Secrets or ConfigMaps, the Harvester CloudInit CRD is UI-manageable and supports YAML syntax validation:

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: CloudInit
metadata:
  name: ubuntu-cloudinit
  namespace: default
spec:
  userData: |
    #cloud-config
    package_update: true
    packages:
      - qemu-guest-agent
      - curl
    users:
      - name: ubuntu
        ssh-authorized-keys:
          - ssh-rsa AAAA...
        sudo: ALL=(ALL) NOPASSWD:ALL
  networkData: |
    version: 2
    ethernets:
      eth0:
        dhcp4: true
```

CloudInit templates can be reused across multiple VMs. The CRD is stored as a Kubernetes resource and backed up with the cluster state.

## Certificate Rotation

Harvester generates a self-signed TLS certificate during installation. To replace it:

1. Prepare a PEM-encoded certificate and key (or obtain from Let's Encrypt / internal CA)
2. Apply via the UI under **Settings > SSL Certificate**
3. Or use kubectl to update the `tls-rancher-ingress` secret in the `harvester-system` namespace:

```bash
kubectl -n harvester-system create secret tls tls-rancher-ingress \
  --cert=cert.pem \
  --key=key.pem \
  --dry-run=client -o yaml | kubectl apply -f -
```

The change takes effect after restarting the ingress controller pods.

## Single-Node Limitations

| Feature | Limitation |
|---|---|
| High Availability | No HA — control plane runs on one node |
| Live Migration | Not available (requires 2+ nodes) |
| Maintenance Mode | Cannot evacuate VMs (no destination nodes) |
| Storage Replication | Replicas must be set to 1 (default 3 fails on single node) |
| etcd Backup | Manual snapshots required (no automated etcd backup with 1 node) |

## References

- [Harvester Host Management](https://docs.harvesterhci.io/v1.8/host/)
- [Managing Hosts](https://docs.harvesterhci.io/v1.8/host/)
- [Storage Tags](https://docs.harvesterhci.io/v1.8/host/storage-tags)
