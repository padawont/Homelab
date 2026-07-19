---
snapshot_date: 2026-07-19
domain: kubernetes
updated_by: manual-2026-07-19
related_adrs:
  - configs-and-adr/adr/0001-restructure-into-4-phase-pipeline.md
---

# Current Kubernetes ADRs

```mermaid
stateDiagram-v2
    [*] --> Accepted: ADR 0001
    Accepted --> Superseded: Superseded by newer ADR
    Accepted --> Deprecated: No longer relevant

    state "ADR 0001 — Restructure into 4-Phase Pipeline" as adr0001
    [*] --> adr0001: created
    adr0001 --> Accepted: accepted 2026-07-19

    note right of adr0001
        Covers the entire repo restructure
        including K8s config placement.
        Verified on 2026-07-19 by issue #3 snapshot.
    end note
```

## Legend

| State | Meaning |
|---|---|
| `[*]` | Initial creation |
| `Accepted` | Approved and currently in effect |
| `Deprecated` | No longer relevant, not replaced |
| `Superseded` | Replaced by a newer ADR |

## Workloads

Workloads defined by these ADRs and their associated configs are tracked in `current-config/kubernetes.md`.
