---
snapshot_date: ""
ci_job: ""
generated: false
---

# Version Inventory Snapshots

Point-in-time records of software versions running on the cluster.

## Template

```yaml
snapshot_date: ISO-DATE
software:
  - name: K3s
    version: x.y.z
  - name: Longhorn
    version: x.y.z
  - name: Rancher
    version: x.y.z
```

Create one snapshot file per date: `{date}-versions-snapshot.md`
