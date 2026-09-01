---
title: "Agones metrics and monitoring — OpenCensus, Prometheus, Grafana"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, metrics, monitoring, prometheus, grafana]
sources:
  - url: "https://agones.dev/site/docs/guides/metrics/"
    title: "Agones metrics guide"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/fleet-autoscaling.md"
---

# Agones metrics and monitoring — OpenCensus, Prometheus, Grafana

## Overview

Agones exposes operational metrics for its control plane (the controller) and
for every managed GameServer, Fleet, and autoscaler. Metrics are collected
with **OpenCensus** and exported to **Prometheus**; Agones also ships
**Grafana** dashboards for visualizing them. This note covers how the metrics
are exposed, what is measured, and how they map onto the homelab monitoring
stack. Scaling behavior and autoscaling policy details belong to the companion
note `./02_Knowledge/technologies/services/agones/fleet-autoscaling.md`.

## Details

### How Agones exposes metrics

- The **agones-controller** collects metrics internally with OpenCensus and
  registers views for its own operations and for the GameServer, Fleet, and
  autoscaler resources it manages.
- Prometheus is the reference metrics backend. Prometheus metrics are enabled
  at install time via the Helm values `agones.metrics.prometheusEnabled` and
  `agones.metrics.prometheusServiceDiscovery`.
- There is no separate metrics exporter pod: the **agones-controller** (and the
  allocator) expose `/metrics` themselves on port `http/8080`, discovered via
  Pod annotations; point a scrape job or ServiceMonitor/PodMonitor at them.
- The controller can also push to Stackdriver, but the documented dashboards
  and workflows target Prometheus.

### What's measured

- **Controller metrics** — control-plane health and allocation performance,
  e.g. the total count of successful allocations
  (`agones_gameservers_allocations_total`) and allocation latency as a
  histogram (`agones_gameserver_allocations_duration_seconds`).
- **GameServer metrics** — GameServer state counts, broken out by a `state`
  label (e.g. Ready, Allocated, Shutdown) and labeled with the GameServer, its
  Fleet, namespace, and node.
- **Fleet metrics** — replica counts per Fleet, labeled by type: desired,
  allocated, ready, reserved (`agones_fleets_replicas_count`).
- **Autoscaling metrics** — autoscaler state used for scaling decisions:
  current vs desired replica counts and buffer size/limits
  (`agones_fleet_autoscalers_current_replicas_count`,
  `agones_fleet_autoscalers_desired_replicas_count`,
  `agones_fleet_autoscalers_buffer_size`,
  `agones_fleet_autoscalers_buffer_limits`) plus
  whether scaling is currently allowed (`agones_fleet_autoscalers_able_to_scale`,
  `agones_fleet_autoscalers_limited`).
- **Custom game server metrics** — the game process can record its own
  counters, gauges, timers, and histograms through the SDK; see the Latency
  Testing Services guide for SDK metrics usage.

Example — abstract (exploratory only; nothing is deployed in the homelab):

```yaml
# scrape Agones metrics with a Prometheus operator / Rancher monitoring setup
# selector labels are illustrative — match the controller/allocator as deployed
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: agones-metrics
  namespace: agones-system
spec:
  selector:
    matchLabels:
      agones.dev/role: metrics
  endpoints:
    - port: metrics
      interval: 30s
```

### Grafana dashboards

- Agones ships ready-made Grafana dashboards for the controller, GameServers,
  Fleets, and autoscalers.
- Import them through the Grafana UI (upload the dashboard JSON from the
  Agones repo) and point them at a Prometheus data source that scrapes Agones.
- The dashboards render the metric categories above: state breakdowns, fleet
  replica counts, allocation latency, and autoscaler buffers.

### Homelab fit

Exploratory only — Agones is **not deployed** in the homelab. If it moves
forward on the single-node k3s cluster (`node-main`), the monitoring stack is
Rancher's built-in monitoring app, which deploys Prometheus + Grafana +
Alertmanager and supports ServiceMonitors/PodMonitors for custom scrapes
(`./02_Knowledge/technologies/kubernetes/rancher/operations.md`). The mapping
would be: enable `agones.metrics.prometheusEnabled` at Helm install, add a
ServiceMonitor for the agones-controller in `agones-system`, import the Agones
Grafana dashboards, and point their data source at the Rancher-managed
Prometheus. There is no dedicated Prometheus/Grafana knowledge note in this
repo yet; the Rancher operations note is the current reference.

## Sources / Further Reading

- Agones metrics guide: https://agones.dev/site/docs/guides/metrics/
- Agones documentation (v1.60.0): https://agones.dev/site/docs/
- Agones source repository: https://github.com/agones-dev/agones
- Sibling notes: `./02_Knowledge/technologies/services/agones/overview.md`,
  `./02_Knowledge/technologies/services/agones/fleet-autoscaling.md`
- Rancher monitoring:
  `./02_Knowledge/technologies/kubernetes/rancher/operations.md`
