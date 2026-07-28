---
title: "Harvester Monitoring and Logging"
status: draft
date: 2026-07-28
author: padawont
tags:
  - harvester
  - monitoring
  - prometheus
  - grafana
  - alertmanager
  - logging
sources:
  - url: "https://docs.harvesterhci.io/v1.8/monitoring/harvester-monitoring"
    title: "Harvester Monitoring"
last_audit_date: 2026-07-28
related_configs:
  - "configs-and-adr/node-main/vm/"
---

# Harvester Monitoring and Logging

## rancher-monitoring Addon

Harvester ships with the `rancher-monitoring` addon, which is **disabled by default**. This addon deploys Prometheus, Grafana, Alertmanager, and associated exporters for cluster monitoring.

### Enabling the Addon

Enable it through the Harvester UI:

1. Navigate to **Settings > Addons**
2. Find `rancher-monitoring` in the list
3. Click **Enable** and confirm

Or via kubectl:

```bash
kubectl edit addons harvester-system rancher-monitoring
# Set spec.enabled: true
```

### Resource Requirements

The monitoring stack requires additional resources:

| Component | CPU Request | Memory Request |
|---|---|---|
| Prometheus (per replica) | 0.5 core | 2 GB |
| Grafana | 0.1 core | 200 MB |
| Alertmanager | 0.1 core | 50 MB |
| Node Exporter (per node) | 0.1 core | 50 MB |
| kube-state-metrics | 0.1 core | 100 MB |

In the homelab (8 cores, 32 GB RAM), enabling monitoring consumes ~1-2 GB RAM and 1-2 CPU cores. This is acceptable for a lab environment but should be considered when planning VM workloads.

### Disabling the Addon

The addon is disabled if resources are constrained or if external monitoring (e.g., existing Rancher monitoring) is already in place. In the homelab, Rancher's monitoring (deployed on the K3s cluster) can monitor the Harvester cluster remotely without enabling the local addon.

## Prometheus

The Prometheus instance deployed by `rancher-monitoring` scrapes:

- **Kubernetes components** — API server, kubelet, kube-scheduler, kube-controller-manager
- **Node metrics** — CPU, memory, disk, network via node_exporter
- **Harvester components** — Longhorn metrics (volume IOPS, latency, capacity)
- **KubeVirt metrics** — VM CPU, memory, network, disk I/O
- **etcd metrics** — Leader elections, proposal latency, database size

### Key Metrics

| Metric | Description |
|---|---|
| `kubevirt_vm_resource_requests` | VM requested CPU and memory |
| `kubevirt_vmi_memory_available_bytes` | Available guest memory |
| `kubevirt_vmi_network_traffic_bytes_total` | VM network throughput |
| `longhorn_volume_actual_size_bytes` | Actual disk usage per volume |
| `longhorn_volume_capacity_bytes` | Provisioned volume capacity |
| `longhorn_volume_ioops` | Volume I/O operations per second |

## Grafana Dashboards

The addon includes pre-configured Grafana dashboards:

### Cluster Overview Dashboard
- Node CPU, memory, disk utilization
- Pod and container resource usage
- Network throughput per node
- API server request latency

### VM Detail Dashboard
- Per-VM CPU usage and throttling
- Memory balloon and actual usage
- Network interface throughput
- Disk I/O latency and IOPS
- vCPU vs. pCPU ratio

### Longhorn Dashboard
- Volume health status (healthy/degraded/faulty)
- Replica distribution across nodes
- Backup operation status and duration
- Disk space usage per node

### Live Migration Dashboard
- Migration progress and throughput
- Migration success/failure rate
- Migration duration histogram

## Alertmanager Configuration

Alertmanager sends notifications when predefined conditions are met. Default alerts include:

| Alert Name | Condition | Severity |
|---|---|---|
| `NodeNotReady` | Node status is `NotReady` for > 5 minutes | critical |
| `PersistentVolumeFaulty` | Longhorn volume enters faulty state | critical |
| `NodeDiskPressure` | Node disk usage > 80% | warning |
| `HarvesterVMNotRunning` | VM is not in `Running` state for > 10 minutes | warning |
| `LonghornVolumeReplicaInsufficient` | Volume has fewer replicas than configured | warning |

### Alertmanager Receivers

Configure notification channels in Alertmanager:

**Webhook:**
```yaml
receivers:
  - name: webhook-receiver
    webhook_configs:
      - url: "https://hooks.example.com/alerts"
        send_resolved: true
```

**Microsoft Teams:**
```yaml
receivers:
  - name: teams-receiver
    webhook_configs:
      - url: "https://outlook.office.com/webhook/..."
        send_resolved: true
```

**SMS (via webhook gateway):**
```yaml
receivers:
  - name: sms-receiver
    webhook_configs:
      - url: "https://sms-gateway.example.com/send"
        send_resolved: true
```

## Resource Limits

Addon resources can be tuned via the addon's values:

```yaml
spec:
  values:
    prometheus:
      prometheusSpec:
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "1"
            memory: "2Gi"
    grafana:
      resources:
        requests:
          cpu: "100m"
          memory: "100Mi"
```

## Alternative: External Monitoring

If Harvester's built-in monitoring is disabled, the cluster can still be monitored:

- **Rancher Monitoring** — If Harvester is imported into Rancher, the Rancher monitoring stack can scrape Harvester's metrics endpoints remotely
- **Existing Prometheus** — Configure a remote Prometheus to scrape Harvester's kubelet and component metrics endpoints
- **Rancher Dashboard** — Basic cluster health (node status, resource usage) is visible without the monitoring addon

In the homelab, Rancher monitoring on the K3s cluster can monitor Harvester externally, avoiding the resource overhead of the local monitoring addon.

## Logging

Harvester does not include a built-in logging stack. VM logs are collected through:

1. **QEMU Guest Agent** — Running inside VMs, `qemu-guest-agent` provides guest OS metrics and console logs
2. **Serial Console** — Accessible from the Harvester UI for interactive troubleshooting
3. **External Logging** — Deploy Fluentd, Logstash, or Loki inside VMs or as a cluster addon

Rancher's logging integration (`rancher-logging` addon) can be deployed if centralized log aggregation is needed.

## References

- [Harvester Monitoring](https://docs.harvesterhci.io/v1.8/monitoring/harvester-monitoring)
- [Harvester VM Metrics](https://docs.harvesterhci.io/v1.8/monitoring/harvester-monitoring)
- [Prometheus Operator](https://prometheus-operator.dev/)
