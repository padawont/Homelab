---
name: deploy-service
description: >
  Standard deploy flow for services and containers on the homelab k3s cluster
  (node-main, 192.168.111.7). Trigger when the user asks to deploy, install,
  upgrade, or update a service, container, or helm chart on the cluster.
  Finds the service's Implementation overview.md and follows its documented
  deployment steps. ONLY usable from the build or runesmith agents — refuses
  to run from any other agent.
---

# deploy-service

Standard, repeatable flow for deploying services to the homelab k3s cluster
(`node-main`). The skill first looks up the service in the Implementation
folder, reads its `overview.md`, and follows the documented deployment steps.
Run the steps in order.

## Guardrails (non-negotiable)

- **Agent gate**: this skill runs ONLY when the active agent is `build` or
  `runesmith`. Check your own agent identity in context. If it is neither,
  STOP immediately — run no commands, do not proceed — and tell the user to
  switch to the build or runesmith agent.
- **Follow the Implementation doc**: deployment MUST follow the steps in the
  service's `05_Implementations/node-main/{service}/overview.md`. Do not
  improvise the procedure.
- **Target confirmation**: always confirm the target cluster and the service
  name with the user before running anything. The only documented target is
  node-main k3s.
- **Read-only before deploy**: discovery and checks use inspection commands
  only (`kubectl get/describe/logs`, `helm list`, `helm show values`). Nothing
  mutates cluster state until the user has confirmed the deploy plan.
- **No secrets in the repo**: never hardcode passwords, tokens, or keys. Pull
  from env vars or existing Secrets. Never write secrets to a file or commit
  them.
- **Destructive ops need confirmation**: any `delete`, `uninstall`, namespace
  removal, PVC deletion, or data-destroying action requires explicit user
  confirmation first.
- **Rollback documented**: every deploy must have a corresponding
  `rollback.md` entry (created/updated in the PKM step below).
- **When in doubt whether a command mutates state, do not run it — ask.**

## Connection (via login-server skill)

- Use the `login-server` skill for ALL SSH to node-main (192.168.111.7): it
  handles `SSHPASS`, `sshpass`, the key-based fallback, and connection
  details. Do not duplicate connection info here.
- kubectl on the node:
  `KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl` (runic) or
  `sudo k3s kubectl` (root).
- Helm on the node: `helm` with the same `KUBECONFIG`.

## Deploy flow

### Step 1 — Find the service's Implementation doc

- Confirm the service name with the user.
- Check `05_Implementations/node-main/` for a folder matching the service.
- Read its `overview.md` (deployment steps) and `rollback.md` (revert steps).
- If no Implementation folder exists, STOP and tell the user — do not
  improvise a deploy for an undocumented service.

### Step 2 — Pre-deploy checks (read-only)

- Confirm the cluster and service with the user.
- Run the pre-deploy checks listed in the service's `overview.md` (node Ready,
  namespace present, existing chart/manifests, secrets/values sourcing).
- Present the plan to the user: target, service, namespace, method (Helm vs
  manifests), and version. Get confirmation.

### Step 3 — Deploy (follow the Implementation doc)

- Execute exactly the deployment steps from the service's `overview.md`
  (Helm install/upgrade or kubectl apply, with the documented versions).
- Do not use `latest`; use the versions pinned in the doc.
- If the doc references a chart or manifests file, use those exact sources.

### Step 4 — Post-deploy verification

- Run the post-deploy verification steps from the service's `overview.md`
  (rollout status, pod readiness, endpoints reachable).
- If verification fails, do not update the PKM notes. Diagnose, report, and
  propose a fix (or roll back per `rollback.md` if the user requests).

### Step 5 — PKM note update

After a successful verified deploy, update the implementation records under
`05_Implementations/node-main/{service}/`:

- Update `overview.md` with any config/version changes from this deploy,
  per `05_Implementations/AGENTS.md` (frontmatter, kebab-case, ≤150 lines).
- Ensure `rollback.md` documents how to revert this deploy safely.
- If the folder does not exist yet, create it from
  `./Templates/implementations/service.md` and `rollback.md`.

## Rules

- Always confirm the target and service before deploying.
- NEVER improvise a deployment procedure — follow the Implementation doc.
- Never hardcode or commit secrets.
- No destructive action without explicit user confirmation.
- Document every deploy in the PKM (overview + rollback).
- Do not invent cluster targets — the only documented cluster is node-main.
