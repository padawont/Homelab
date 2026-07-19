---
snapshot_date: ""
ci_job: ""
generated: false
---

# Workload Snapshots

Point-in-time records of active deployments, services, ingress URLs, and replica counts.

## Template

```yaml
workload: {name}
namespace: {namespace}
replicas: {desired}/{ready}
ingress_url: https://{hostname}
health_endpoint: https://{hostname}/health
last_restart: ISO-DATE
```

Add one entry per workload in this file, or create one file per workload.
