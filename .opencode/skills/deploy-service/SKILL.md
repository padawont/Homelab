---
name: deploy-service
description: >
  Standard deploy flow for services and containers on the homelab k3s cluster
  (node-main, 192.168.111.7). Trigger when the user asks to deploy, install,
  upgrade, or update a service, container, or helm chart on the cluster.
  Finds the service's Implementation overview.md and follows its documented
  deployment steps. Creating/mutating steps are human-run following the doc;
  runesmith does not hold those verbs. cluster-worker may run only the
  whitelisted verify, rollback and restart subset.
---

# deploy-service

Standard, repeatable flow for deploying services to the homelab k3s cluster
(`node-main`). The skill first looks up the service in the Implementation
folder, reads its `overview.md`, and follows the documented deployment steps.
Run the steps in order.

> Cluster execution is Flow B (operational chain) — see `./.opencode/WORKFLOW.md`.

## Guardrails (non-negotiable)

- **Two separate execution modes**:
  - **Mode A — create/mutate**: the human, following this doc, runs discovery,
    manifest generation, `helm install`/`upgrade` and `kubectl apply`. `runesmith`
    does not hold these verbs. They are outside `cluster-worker`'s whitelist, so it
    never runs them.
  - **Mode B — verify/rollback/restart**: `cluster-worker`, only from a
    committed plan in the service's Implementation folder and only its
    whitelisted verbs (`kubectl get`/`describe`/`logs`, `rollout undo`/
    `restart`/`status`, `helm status`/`history`/`list`/`rollback`, `ssh`
    transport).
  - No other agent besides `cluster-worker` runs this skill: `spec-writer` has shell
    denied.
- **Follow the Implementation doc**: deployment MUST follow the steps in the
  service's `05_Implementations/node-main/{service}/overview.md`. Do not
  improvise the procedure.
- **Target confirmation**: `runesmith` always confirms the target cluster and
  the service name with the user before the plan is committed. The only
  documented target is node-main k3s.
- **Read-only before deploy**: discovery and checks use inspection commands
  only (`kubectl get/describe/logs`, `helm list`, `helm show values`). Nothing
  mutates cluster state until the human has confirmed the deploy plan and
  committed it; `runesmith` may put the question, but it does not run the change.
- **No secrets in the repo**: never hardcode passwords, tokens, or keys. Pull
  from env vars or existing Secrets. Never write secrets to a file or commit
  them.
- **Destructive ops need confirmation**: any `delete`, `uninstall`, namespace
  removal, PVC deletion, or data-destroying action requires explicit user
  confirmation obtained by `runesmith` before the plan is committed.
- **Rollback documented**: every deploy must have a corresponding
  `rollback.md` entry (created/updated in the PKM step below).
- **When in doubt whether a command mutates state, do not run it** —
  `runesmith` asks the user, before the plan is committed.

## Connection (via login-server skill)

- Use the `login-server` skill for ALL SSH to node-main (192.168.111.7): it
  handles `SSHPASS`, `sshpass`, and connection details. Do not duplicate
  connection info here.
- kubectl on the node:
  `KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl` (runic) or
  `sudo k3s kubectl` (root).
- Helm on the node: `helm` with the same `KUBECONFIG`.

## Deploy flow

### Step 1 — Find the service's Implementation doc

- `runesmith` confirms the service name with the user.
- Check `05_Implementations/node-main/` for a folder matching the service.
- Read its `overview.md` (deployment steps) and `rollback.md` (revert steps).
- If no Implementation folder exists, STOP and tell the user — do not
  improvise a deploy for an undocumented service.

### Step 2 — Pre-deploy checks (read-only)

- `runesmith` confirms the cluster and service with the user.
- Run the pre-deploy checks listed in the service's `overview.md` (node Ready,
  namespace present, existing chart/manifests, secrets/values sourcing).
- Present the plan to the user: target, service, namespace, method (Helm vs
  manifests), and version. `runesmith` gets confirmation before committing the
  plan.

### Step 3 — Deploy (follow the Implementation doc)

- The human executes exactly the deployment steps from the service's `overview.md`
  (Helm install/upgrade or kubectl apply, with the documented versions);
  `runesmith` does not run them.
- Do not use `latest`; use the versions pinned in the doc.
- If the doc references a chart or manifests file, use those exact sources.

### Step 4 — Post-deploy verification

- Run the post-deploy verification steps from the service's `overview.md`
  (rollout status, pod readiness, endpoints reachable).
- If verification fails, do not update the PKM notes. Diagnose, report, and
  propose a fix (or roll back per `rollback.md` if the user requests).

### Step 4b — Rollback (via `cluster-worker`)

When the user requests a rollback, do not run `helm rollback` or `kubectl
rollout undo` yourself. Hand it to `cluster-worker` (Flow B — see
`./.opencode/WORKFLOW.md`) with a JSON plan:

```json
{
  "plan_id": "{service}-rollback",
  "plan_source": "./05_Implementations/node-main/{service}/rollback.md",
  "step_section": "## Rollback steps",
  "step_range": "1-6",
  "dry_run": false
}
```

Set `dry_run: false` for the rollback itself. A `dry_run: true` launch is an
inspect-only run: it reports and mutates nothing. It is not the pre-flight target
check every executing run does first; that check is described in
`./.opencode/agents/cluster-worker.md` § Pre-Flight & Step Budget. Re-launch the
same plan with `false` to execute.

- `cluster-worker` is limited to the whitelisted revert verbs
  (`kubectl rollout undo` / `helm rollback`) plus read-only inspection; it
  pre-flights the target first and refuses the whole plan if any step falls
  outside its whitelist. `runesmith` is the only agent that asks the human: a
  `cluster-worker` that needs a decision returns a refusal with
  `escalate_to: "runesmith"`. A whitelisted step that runs and fails is a
  `failed` payload, not a refusal: `state_after` reports what ran, the chain
  stops, and no worker resumes on its own
  (`./.opencode/agents/cluster-worker.md` § Failed).
- The **hub** launches `cluster-worker` and chains it — this skill never spawns
  it. The rollback path must exist in `rollback.md` before launch.

### Step 5 — PKM note update

After a successful verified deploy, update the implementation records under
`05_Implementations/node-main/{service}/`:

- Update `overview.md` with any config/version changes from this deploy,
  per `05_Implementations/AGENTS.md` (frontmatter, kebab-case, ≤150 lines).
- Ensure `rollback.md` documents how to revert this deploy safely.
- If the folder does not exist yet, create it from
  `./Templates/implementations/service.md` and
  `./Templates/implementations/rollback.md`.
- These are repo writes: the hub routes them to `worker` (draft/update) and
  `editor` (confirmed fixes), never a direct edit by this skill.

## Rules

- `runesmith` always confirms the target and service before deploying.
- NEVER improvise a deployment procedure — follow the Implementation doc.
- Never hardcode or commit secrets.
- No destructive action without explicit user confirmation by `runesmith`.
- **Rollback goes through `cluster-worker`** — never run `helm rollback` or
  `kubectl rollout undo` directly.
- Document every deploy in the PKM (overview + rollback).
- Do not invent cluster targets — the only documented cluster is node-main.
