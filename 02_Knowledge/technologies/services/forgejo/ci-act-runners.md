---
title: "Forgejo Actions and runners (CI/CD)"
status: draft
author: "padawont"
date: 2026-08-23
tags: [forgejo, ci, cd, actions, runners, docker]
sources:
  - url: "https://forgejo.org/docs/latest/admin/actions/"
    title: "Forgejo Actions administrator guide"
  - url: "https://forgejo.org/docs/latest/admin/actions/configuration/"
    title: "Forgejo Runner configuration"
  - url: "https://forgejo.org/docs/latest/admin/actions/installation/docker/"
    title: "Forgejo Runner installation with Docker"
  - url: "https://forgejo.org/docs/latest/admin/actions/registration/"
    title: "Forgejo Runner registration"
  - url: "https://forgejo.org/docs/latest/admin/actions/security/"
    title: "Securing Forgejo Actions deployments"
  - url: "https://forgejo.org/docs/latest/user/actions/github-actions/"
    title: "Forgejo Actions — GitHub Actions"
last_audit_date: 2026-08-23
related_docs:
  - "./02_Knowledge/technologies/services/forgejo/overview.md"
  - "./02_Knowledge/technologies/services/forgejo/install-config.md"
  - "./02_Knowledge/technologies/services/forgejo/security.md"
---

# Forgejo Actions and runners (CI/CD)

## Overview

Forgejo Actions gives Forgejo GitHub-Actions-style CI/CD. Workflow files
live in `.forgejo/workflows/*.yml` and are executed by **Forgejo Runner**, a
standalone binary that connects to the instance with a UUID + token.
Runners register at instance, organization, user, or repository scope, and can
run jobs in Docker containers. Runner setup is noted here as reference — the
runner is not provisioned yet in this homelab (a follow-up after the ADR).

## Details

### Workflow files

- Store workflows as `.forgejo/workflows/*.yml` in the repository.
- Workflow YAML is familiar to GitHub Actions users but not guaranteed
  compatible (see the GitHub Actions doc): `jobs`, `runs-on` labels, `steps`
  with `uses: actions/checkout@v6` (requires Node.js in the job image),
  environment variables, and secrets.
- See the user-guide "basic concepts" and reference pages for syntax details.

### Runner registration

A runner needs a UUID and a token, obtained in three ways:

1. **Interactive (recommended)** — create a runner in the UI, which yields a
   UUID + token to paste into the runner's config file:
   - Instance admin `/admin/actions/runners` → all repos on the instance
   - Org `/org/{org}/settings/actions/runners` → all repos in the org
   - User `/user/settings/actions/runners` → all of a user's repos
   - Repo `/{owner}/{repo}/settings/actions/runners` → a single repo
2. **HTTP API** — automate creation via the API.
3. **Offline (IaC)** — on the Forgejo host:
   `forgejo forgejo-cli actions register --name runner-name --scope myorganization --secret <40-hex>`
   then put the printed UUID and the secret into the runner config. The first 16
   hex chars are the runner identifier; the rest is the secret.

Runner config (`config.yaml`, generated if absent) — example:

```yaml
# Example — abstract
server:
  connections:
    forgejo:
      url: https://git.homelab.local/
      uuid: 33834eef-e758-48c4-a676-1745426747aa
      token: d4fe2db46a4c6bdc434a9ce3378d9a1489c1b30e
```

One runner config can hold multiple `connections` (different instances or
orgs). Jobs needing containers require Docker access on the runner.

### Runner modes

- **Persistent** (default): runs many jobs over its lifetime.
- **Ephemeral**: at most one job, then deleted by Forgejo. Ephemeral mode is
  enabled at registration and enforced server-side — the safer choice where
  runner instances are created on demand.

### Security

Runners execute untrusted repository code — treat them like CI workers:

- Isolate runners from the cluster and from host secrets; give them only what a
  job needs (see the Actions security guide).
- Use ephemeral runners where practical; keep persistent runners' scope narrow.
- Workflows only run if a runner with a matching label exists.
- Secrets reach jobs only with the right permission; review PR-triggered runs
  (a PR from an untrusted contributor can submit workflow changes).
- Pin third-party actions to commit SHAs where supply-chain risk matters.
- Runner tokens are secrets — store them in a k8s Secret
  (`./02_Knowledge/technologies/kubernetes/concepts/secrets.md`).

### Deploying a runner on k3s

- Install the runner binary, or run the container image
  `data.forgejo.org/forgejo/runner` (the binary inside it is `forgejo-runner`),
  register it, mount the `config.yaml`, and give it Docker access for
  container-based jobs.
- On the homelab the runner would live alongside Forgejo in the `forgejo`
  namespace; exact manifests are deferred to the Implementation stage.

## Sources / Further Reading

- Actions administrator guide: https://forgejo.org/docs/latest/admin/actions/
- Runner registration: https://forgejo.org/docs/latest/admin/actions/registration/
- Runner installation with Docker: https://forgejo.org/docs/latest/admin/actions/installation/docker/
- Securing Actions deployments: https://forgejo.org/docs/latest/admin/actions/security/
- Overview: `./02_Knowledge/technologies/services/forgejo/overview.md`
- Security: `./02_Knowledge/technologies/services/forgejo/security.md`
