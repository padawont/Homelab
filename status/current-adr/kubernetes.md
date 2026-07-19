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
    [*] --> adr0001: created
    adr0001 --> Accepted: accepted 2026-07-19
    Accepted --> Superseded: Superseded by newer ADR
    Accepted --> Deprecated: No longer relevant

    state "ADR 0001 — Restructure into 4-Phase Pipeline" as adr0001 {
        state "Helm-Managed" as helm {
            longhorn-v1.12.0
            rancher-v2.14.3
            cert-manager-v1.16.3
            metallb-v0.16.1
            fleet-0.15.4
            rancher-turtles-0.26.3
            rancher-webhook-0.10.7
            system-upgrade-controller-v0.19.1
        }
        state "Raw Manifests" as raw {
            nodes.yaml
            k3s-kubeconfig.yaml
            cluster-state.yaml
            bookstack.yaml
            kiwix.yaml
            kiwix-copy-job.yaml
            extras.yaml
        }
        state "NixOS Configs" as nixos {
            configuration.nix
            hardware-configuration.nix
        }
        adr0001 --> helm
        adr0001 --> raw
        adr0001 --> nixos
    }

    note right of adr0001
        Restructured repo into 4-phase pipeline.
        All config placement governed by this ADR.
        Verified on 2026-07-19 (issue #3).
    end note
```

## Legend

| State | Meaning |
|---|---|
| `[*]` | Initial creation |
| `Accepted` | Approved and currently in effect |
| `Deprecated` | No longer relevant, not replaced |
| `Superseded` | Replaced by a newer ADR |
