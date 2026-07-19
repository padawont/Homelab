# Deployment Section

Deployment contains CI/CD pipeline definitions, step-by-step deployment procedures, and Helm/Kustomize values. This phase bridges configuration (what to deploy) and operations (how to deploy it).

## Structure

```
deployment/
├── pipelines/       # CI/CD workflow configs (GitHub Actions, ArgoCD app sets)
├── procedures/      # Step-by-step deployment guides
└── manifests/      # Helm values, Kustomize overlays, ArgoCD application manifests
```

## Pipeline Config Format

Pipeline files must be named `{service}-{action}.{ext}` — e.g. `deploy-bookstack.yml`, `backup-cluster.yml`.

Each pipeline file should include in its header:
- `service` — the workload being deployed
- `trigger` — what starts the pipeline (push, schedule, manual)
- `target` — which node or environment it deploys to

## Procedure Template

Deployment procedures should follow this structure:

```markdown
# Deploy {Service}

## Prerequisites
- Access requirements
- Expected versions
- Dependencies

## Steps
1. Preparation
2. Configuration
3. Deployment
4. Verification

## Rollback
How to undo the deployment
```

## Manifests vs Raw Configs

- **Raw K8s manifests** (deployments, services, configmaps) belong in `configs-and-adr/node-<role>/kubernetes/`
- **Helm values, Kustomize overlays, ArgoCD Application YAMLs** belong in `deployment/manifests/`
- A procedure may reference both locations
