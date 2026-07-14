# OpenChoreo IDP Pilot Plan

Proposal for a time-boxed, low-footprint pilot of [OpenChoreo](https://openchoreo.dev/) as an Internal Developer Platform for RunicEngines. Implements the **Pilot** recommendation from `research/openchoreo-idp-evaluation/`.

## Files

| File | Purpose |
|---|---|
| `overview.md` | The pilot plan (source of truth) — Motivation, Proposed Changes (scope), Implementation Plan (4 phases + go/no-go gate), Timeline |
| `diagrams/pilot-architecture.mmd` | Single-cluster pilot architecture (build plane out of scope) |
| `diagrams/pilot-phases.mmd` | Pilot phases and the go/no-go gate |
| `openchoreo-idp-pilot-v1.pdf` | Rendered PDF of version 1 (via `devbox run proposal-render openchoreo-idp-pilot`) |

## Rendering

```bash
devbox shell
devbox run proposal-render openchoreo-idp-pilot
```

## Cross-references

- **Research** — [`research/openchoreo-idp-evaluation/`](../../research/openchoreo-idp-evaluation/) (the evaluation and recommendation)
- **Idea** — [`ideas/organisation/tools/openchoreo-idp/`](../../ideas/organisation/tools/openchoreo-idp/)
- **ADR 0008** — [`adr/0008-pilot-openchoreo-idp/`](../../adr/0008-pilot-openchoreo-idp/) (the decision to run this pilot)
- **ADR 0002** — [`adr/0002-github-etiquettes/`](../../adr/0002-github-etiquettes/) (conventions the pilot follows)
- **Issue** — [#78](https://github.com/RunicEngines/knowledge-base/issues/78)
