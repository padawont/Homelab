---
title: "Harvester Advanced Features"
status: draft
date: 2026-07-28
author: padawont
tags:
  - harvester
  - advanced
  - settings
  - addons
  - vgpu
  - cloud-init
  - longhorn-v2
sources:
  - url: "https://docs.harvesterhci.io/v1.8/advanced"
    title: "Harvester Advanced Features"
  - url: "https://docs.harvesterhci.io/v1.8/advanced/vgpu"
    title: "Harvester vGPU Support"
  - url: "https://docs.harvesterhci.io/v1.8/advanced/settings"
    title: "Harvester Settings Reference"
last_audit_date: 2026-07-28
related_configs:
  - "configs-and-adr/node-main/vm/"
---

# Harvester Advanced Features

## Settings Reference

Harvester exposes configuration via a `settings.harvesterhci.io` custom resource. Key settings include:

### Backup Target

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: Setting
metadata:
  name: backup-target
spec:
  value: |
    {
      "type": "nfs",
      "nfs": {
        "server": "192.168.111.10",
        "path": "/mnt/backups/harvester"
      }
    }
```

### HTTP Proxy

Configure an HTTP/HTTPS proxy for nodes that need outbound access through a proxy:

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: Setting
metadata:
  name: http-proxy
spec:
  value: |
    {
      "httpProxy": "http://proxy.example.com:3128",
      "httpsProxy": "http://proxy.example.com:3128",
      "noProxy": "localhost,127.0.0.1,10.0.0.0/8,192.168.0.0/16,.svc,.cluster.local"
    }
```

### Overcommit Configuration

Controls CPU and memory overcommit ratios:

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: Setting
metadata:
  name: overcommit-config
spec:
  value: |
    {
      "cpu": 1.5,
      "memory": 1.2
    }
```

### VM Force Reset Policy

Controls whether users can force-reset VMs:

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: Setting
metadata:
  name: vm-force-reset-policy
spec:
  value: "always"  # Options: "always", "admin-only", "never"
```

### SSL Certificate

Replace the self-signed TLS certificate:

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: Setting
metadata:
  name: ssl-certificate
spec:
  value: |
    {
      "ca": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
      "publicCertificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
      "privateKey": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
    }
```

### Additional Settings

| Setting | Description | Default |
|---|---|---|
| `containerd-registry` | Private registry mirrors for containerd | Empty |
| `default-storage-class` | StorageClass for new PVCs | `harvester-longhorn` |
| `log-level` | Logging verbosity (`info`, `debug`, `trace`) | `info` |
| `maintenance-mode` | Global maintenance mode | `false` |
| `media-link-prefix` | Base URL for media links | Empty |
| `ntp-servers` | NTP server list | Google NTP pool |
| `prometheus-endpoint` | Remote Prometheus write endpoint | Empty |
| `support-bundle-timeout` | Timeout for support bundle generation (minutes) | `10` |
| `upgrade-checker` | Enable/disable upgrade availability checks | `true` |

## Addons

Harvester addons extend platform capabilities. They are managed via the `addons.harvesterhci.io` custom resource.

### PCI Devices Addon

Exposes PCI devices (e.g., GPUs, NVMe drives, network cards) to VMs via PCI passthrough:

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: Addon
metadata:
  name: pcidevices
  namespace: harvester-system
spec:
  enabled: true
  values:
    enabledDevicePlugins:
      - name: nvidia
        vendor: "10de"  # NVIDIA vendor ID
        deviceSelector:
          - "10de:1e04"  # GPU device ID
```

Requires IOMMU enabled in BIOS/UEFI (VT-d / AMD-Vi).

### NVIDIA Driver Toolkit Addon

Installs NVIDIA GPU drivers on Harvester nodes:

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: Addon
metadata:
  name: nvidia-driver-toolkit
  namespace: harvester-system
spec:
  enabled: true
  values:
    driverVersion: "535.154.05"
```

After installation, GPUs can be passed to VMs via PCI passthrough or vGPU (with supported GPUs).

### Upgrade Manager

Handles Harvester version upgrades:

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: Addon
metadata:
  name: upgrade-manager
  namespace: harvester-system
spec:
  enabled: true
```

The upgrade manager checks for new Harvester versions, downloads upgrade artifacts, and manages the A/B partition upgrade process. Upgrades are atomic — on failure, the system boots from the previous partition.

### Kube-OVN Operator

Manages Kube-OVN for VPC networking:

```yaml
apiVersion: harvesterhci.io/v1beta1
kind: Addon
metadata:
  name: kube-ovn
  namespace: harvester-system
spec:
  enabled: true
  values:
    vpc:
      enable: true
```

Required for VPC networking features (see [networking.md](networking.md)).

## Witness Node

A witness node is a Harvester node that runs etcd only — it does not run KubeVirt or Longhorn. Its sole purpose is to provide etcd quorum in a 2-node cluster where a third etcd member is required for fault tolerance.

### Witness Node Requirements

- Minimum 2 CPU cores
- 4 GB RAM
- 40 GB disk
- Network connectivity to the management cluster

### When to Use a Witness Node

- 2-node production clusters needing etcd HA
- Edge deployments where a third full node is not feasible

**Lab relevance:** Not applicable. The homelab is single-node with no HA requirements.

## vGPU (Virtual GPU)

vGPU allows sharing a physical GPU across multiple VMs. NVIDIA vGPU (formerly GRID) requires:

- Supported NVIDIA GPU (enterprise-grade: A-series, A100, H100, RTX-series with vGPU license)
- NVIDIA vGPU Manager driver on the host
- NVIDIA vGPU guest driver in each VM
- `nvidia-driver-toolkit` addon installed

AMD MxGPU and Intel GVT-g are alternative vGPU technologies with different hardware requirements.

**Lab relevance:** Currently not applicable. The homelab node does not have a supported GPU for vGPU.

## CloudInit CRD

The CloudInit CRD stores reusable cloud-init configurations for VM provisioning (detailed in [host-management.md](host-management.md)). Advanced features include:

- **Templating** — Reference `{{ .InstanceName }}`, `{{ .Hostname }}` in cloud-init user-data
- **NetworkData Templates** — Pre-configured network configurations for common OS images
- **Validation** — YAML syntax validation at creation time

## Longhorn V2

Longhorn V2 is an experimental storage backend in Harvester v1.8 that uses **SPDK** (Storage Performance Development Kit) for improved performance:

| Feature | Longhorn V1 | Longhorn V2 |
|---|---|---|
| I/O path | Kernel (iSCSI) | Userspace (SPDK/NVMe-oF) |
| Latency | Higher | Lower |
| CPU overhead | Lower (kernel path) | Higher (polling mode) |
| Features | Full | Experimental |
| Backups | Supported | Not yet supported |

V2 volumes are created via a separate StorageClass:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn-v2
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "1"
  backendDriver: "v2"
```

**Lab relevance:** Not applicable. Longhorn V2 is experimental and lacks backup support, which is critical for single-node disaster recovery.

## Additional Advanced Features

### Support Bundle

Harvester can generate a support bundle containing cluster diagnostics:

- Cluster state (resources, events, logs)
- Longhorn status and volume health
- KubeVirt VM and VMI states
- System logs (journald)
- Network configuration and connectivity tests

Generate via UI under **Settings > Support Bundle** or via CLI:

```bash
kubectl get supportbundle -n harvester-system
```

### Upgrade Process

Harvester upgrades are atomic operations using A/B partition layout:

1. Upgrade Manager downloads the new version artifact
2. A new boot partition is created (B)
3. The new version is installed on partition B
4. The system reboots into partition B
5. If boot fails, the system automatically reverts to partition A
6. Kubernetes and Harvester components are upgraded in-place

## References

- [Harvester Advanced Features](https://docs.harvesterhci.io/v1.8/advanced)
- [Harvester Settings Reference](https://docs.harvesterhci.io/v1.8/advanced/settings)
- [Harvester vGPU Support](https://docs.harvesterhci.io/v1.8/advanced/vgpu)
- [Longhorn V2](https://longhorn.io/docs/v2.0/)
