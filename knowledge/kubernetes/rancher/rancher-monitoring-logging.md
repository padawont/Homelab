---
title: "Rancher Monitoring and Logging"
status: draft
author: padawont
date: 2026-07-11
tags:
  - rancher
  - monitoring
  - logging
  - prometheus
  - grafana
  - fluentd
sources:
  - url: "https://ranchermanager.docs.rancher.com/reference-guides/rancher-cluster-tools"
    title: "Rancher — Cluster Tools"
  - url: "https://ranchermanager.docs.rancher.com/integrations-in-rancher/logging"
    title: "Rancher — Logging Integration"
  - url: "https://ranchermanager.docs.rancher.com/integrations-in-rancher/monitoring-and-alerting"
    title: "Rancher — Monitoring and Alerting"
last_audit_date: 2026-07-11
---

# Rancher Monitoring and Logging

## Prerequisites

- [Rancher instance](../rancher-install-k3d.md) — running and accessible
- [Kubernetes Fundamentals](../) — K8s concepts (Pods, Services, StorageClasses)
- [Kubernetes Storage](../storage.md) — understanding of PersistentVolumes for metric/log retention
- [Helm Basics](../deployments.md) — understanding of Helm chart installation

## rancher-monitoring (Prometheus + Grafana)

Rancher provides a monitoring stack based on the Prometheus Operator. It is installed per-cluster from the Rancher Apps Marketplace (Cluster → Apps → Charts → Monitoring).

### What It Installs

When you enable monitoring on a cluster, the following components are deployed:

| Component | Description |
|---|---|
| **Prometheus Operator** | Manages Prometheus and Alertmanager instances via CRDs |
| **Prometheus** | Time-series database for metrics collection and alerting |
| **Alertmanager** | Handles alert deduplication, silencing, and routing to notification channels |
| **Grafana** | Dashboard UI with pre-configured dashboards for cluster, node, and pod metrics |
| **node-exporter** | Hardware and OS metrics from each node (CPU, memory, disk, network) |
| **kube-state-metrics** | Cluster-level metrics derived from K8s object states (deployments, pods, nodes) |
| **prometheus-adapter** | Exposes Prometheus metrics for use by K8s HorizontalPodAutoscaler |

Each downstream cluster has its own Prometheus instance — there is no single global Prometheus.

### Enabling Monitoring

From the Rancher UI:

1. Navigate to the target cluster → **Apps** → **Charts**
2. Search for and select **Monitoring**
3. Configure storage retention and resource limits
4. Click **Install**

The installation creates a `cattle-monitoring-system` Namespace on the downstream cluster with all monitoring components.

### Pre-Configured Dashboards

The Grafana instance comes with dashboards for:

- **Cluster** — CPU/memory usage by namespace, pod, node; API server latency; etcd metrics
- **Nodes** — per-node resource usage, network I/O, disk I/O
- **Pods** — per-pod CPU/memory, restart count, network traffic
- **Kubernetes Components** — API Server, Scheduler, Controller Manager, CoreDNS, etcd

Dashboards are visible both within Grafana and directly embedded in the Rancher UI.

### Custom Alerting

Default alerting rules cover common scenarios:

- Node down for 5 minutes
- PersistentVolume filling up
- Pod crash-looping
- API server latency spike

To create custom alerts, define a `PrometheusRule` resource:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: rancher-custom-alerts
  namespace: cattle-monitoring-system
spec:
  groups:
    - name: rancher
      rules:
        - alert: HighMemoryUsage
          expr: node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes > 0.9 * node_memory_MemTotal_bytes
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Node memory usage above 90%"
```

Alertmanager routes can be configured from the UI to send notifications via Slack, email, PagerDuty, or webhook.

## rancher-logging (Fluentd)

Rancher provides a logging stack based on the Banzai Cloud Logging Operator, which manages Fluentd instances for log collection, transformation, and forwarding.

### What It Installs

When you enable logging on a cluster:

| Component | Description |
|---|---|
| **Logging Operator** | Manages Fluentd deployments via Flow and Output CRDs |
| **Fluentd** | Log collector and forwarder running as a DaemonSet on each node |
| **CRDs** | `ClusterFlow`, `ClusterOutput`, `Flow`, `Output` for configuring log routing |

### Enabling Logging

From the Rancher UI:

1. Navigate to the target cluster → **Apps** → **Charts**
2. Search for and select **Logging**
3. Configure the output destination (Elasticsearch, Splunk, S3, GCP, Kafka, syslog)
4. Click **Install**

### Configuring Log Collection

Log routing is configured via CRDs:

```yaml
# ClusterOutput — where logs go
apiVersion: logging.banzaicloud.io/v1beta1
kind: ClusterOutput
metadata:
  name: elasticsearch-output
spec:
  elasticsearch:
    host: elasticsearch.monitoring.svc.cluster.local
    port: 9200
    scheme: https
    ssl_verify: false
```

```yaml
# ClusterFlow — which logs to collect and how to transform them
apiVersion: logging.banzaicloud.io/v1beta1
kind: ClusterFlow
metadata:
  name: cattle-system-logs
spec:
  filters:
    - tag_normaliser: {}
    - parser:
        remove_key_name_field: true
        parsers:
          - type: multi_line_format
            format: /^(\d{4}-\d{2}-\d{2})/
  match:
    - select:
        labels:
          app: rancher
  globalOutputRefs:
    - elasticsearch-output
```

### Common Output Destinations

| Destination | Use case |
|---|---|
| **Elasticsearch** | Full-text search, aggregation in Kibana |
| **S3 / GCS** | Long-term cold storage, compliance archives |
| **Splunk** | Existing Splunk infrastructure |
| **Kafka** | Stream processing pipeline before permanent storage |

## References

- [Rancher Monitoring and Alerting](https://ranchermanager.docs.rancher.com/integrations-in-rancher/monitoring-and-alerting)
- [Rancher Logging](https://ranchermanager.docs.rancher.com/integrations-in-rancher/logging)
- [Prometheus Operator](https://prometheus-operator.dev/)
- [Banzai Cloud Logging Operator](https://banzaicloud.com/docs/one-eye/logging-operator/)
