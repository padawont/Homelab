---
snapshot_date: 2026-07-19
domain: nixos
updated_by: manual-2026-07-19
related_adrs:
  - configs-and-adr/adr/0001-restructure-into-4-phase-pipeline.md
---

# Current NixOS ADRs

```mermaid
stateDiagram-v2
    [*] --> adr0001: governed by
    adr0001 --> Accepted

    state "ADR 0001 — Restructure into 4-Phase Pipeline" as adr0001 {
        state "NixOS Configs" as nixos_configs {
            configuration.nix
            hardware-configuration.nix
        }
        adr0001 --> nixos_configs
    }

    note right of adr0001
        No NixOS-specific ADRs exist yet.
        OS config is governed by ADR 0001.
    end note
```

## Legend

| State | Meaning |
|---|---|
| `[*]` | Initial creation |
| `Accepted` | Approved and currently in effect |
| `Deprecated` | No longer relevant |
| `Superseded` | Replaced by a newer ADR |
