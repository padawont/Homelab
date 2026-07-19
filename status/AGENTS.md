# Status Section

Status captures point-in-time snapshots of the homelab cluster state. This is Phase 4 of the pipeline — the feedback loop that reports what's actually running, on what versions, and how healthy it is.

## Structure

```
status/
├── workloads/     # Active deployments, services, ingress, replicas
├── hardware/      # CPU, memory, storage utilization snapshots
├── versions/      # Software version inventory
└── generated/     # CI-generated reports — gitignored by default
```

## Snapshot Naming

```
{date}-{scope}-snapshot.md
```

Examples:
- `2026-07-19-workloads-snapshot.md`
- `2026-07-19-versions-snapshot.md`

## Frontmatter Template

Each snapshot file should include:

```yaml
---
snapshot_date: ISO-DATE
ci_job: ""                  # CI job URL or run ID
generated: true | false     # true if CI-generated
---
```

## CI Generation Guidelines

- `status/generated/` is gitignored — CI-generated files go here
- Committed snapshots in `workloads/`, `hardware/`, `versions/` are manually curated or CI-promoted from generated/
- Generated reports should include CI provenance (job URL, run ID) in frontmatter
