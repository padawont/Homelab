---
snapshot_date: ""
ci_job: ""
generated: false
---

# Hardware Status Snapshots

Point-in-time records of CPU, memory, and storage utilization per node.

## Template

```yaml
node: {name}
cpu_usage_percent: {value}
memory_usage_percent: {value}
storage_usage_percent: {value}
snapshot_date: ISO-DATE
```

Add one entry per node in this file, or create one file per node.
