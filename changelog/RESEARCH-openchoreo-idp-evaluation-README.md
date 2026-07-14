# OpenChoreo IDP Evaluation — Research

Evaluation of [OpenChoreo](https://openchoreo.dev/) as a potential Internal Developer Platform for RunicEngines, per issue [#78](https://github.com/RunicEngines/knowledge-base/issues/78). Analysis is bounded by `knowledge/operations/internal-developer-platforms/openchoreo/` and contextualised by the idea `ideas/organisation/tools/openchoreo-idp/`. It lands on a **Pilot** recommendation.

## Files

| File | Description |
|---|---|
| [01-architecture.md](01-architecture.md) | Multi-plane architecture, K8s-native model, multi-cluster/env, GitOps, extensibility (incl. the Workflow/Build/CI plane naming caveat) |
| [02-developer-experience.md](02-developer-experience.md) | Self-service deployment, Backstage portal, lifecycle, CLI/API, onboarding |
| [03-cicd-and-delivery.md](03-cicd-and-delivery.md) | Argo Workflows build plane, GitHub Actions coexistence, promotion, GitOps |
| [04-platform-operations.md](04-platform-operations.md) | Install/maintenance, dependencies, scaling, RBAC, observability, day-2 (the decisive dimension) |
| [05-integration-ecosystem.md](05-integration-ecosystem.md) | Existing-cluster compatibility, Backstage/Argo/observability, identity, API management |
| [06-alternatives-comparison.md](06-alternatives-comparison.md) | Comparison matrix vs DIY, Backstage+ArgoCD, Crossplane-based, Port, Humanitec |
| [07-evaluation-and-recommendation.md](07-evaluation-and-recommendation.md) | Scored summary, adoption-effort estimate, risks, and the **Pilot** recommendation |

## Cross-references

- **Idea** — [`ideas/organisation/tools/openchoreo-idp/`](../../ideas/organisation/tools/openchoreo-idp/)
- **Knowledge** — [`knowledge/operations/internal-developer-platforms/openchoreo/`](../../knowledge/operations/internal-developer-platforms/openchoreo/)
- **Proposal** — [`proposals/openchoreo-idp-pilot/`](../../proposals/openchoreo-idp-pilot/) (the pilot plan)
- **ADR** — [`adr/0008-pilot-openchoreo-idp/`](../../adr/0008-pilot-openchoreo-idp/) (the decision)
- **Issue** — [#78](https://github.com/RunicEngines/knowledge-base/issues/78)
