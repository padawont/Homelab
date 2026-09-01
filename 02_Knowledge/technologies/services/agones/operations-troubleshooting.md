---
title: "Agones operations — troubleshooting and upgrades"
status: draft
author: "padawont"
date: 2026-08-30
tags: [agones, operations, troubleshooting, upgrade]
sources:
  - url: "https://agones.dev/site/docs/guides/troubleshooting/"
    title: "Agones troubleshooting guide"
  - url: "https://agones.dev/site/docs/installation/"
    title: "Agones installation guide (upgrading)"
  - url: "https://agones.dev/site/docs/"
    title: "Agones documentation (v1.60.0)"
  - url: "https://github.com/agones-dev/agones"
    title: "Agones source repository"
last_audit_date: 2026-08-30
related_docs:
  - "./02_Knowledge/technologies/services/agones/install-config.md"
  - "./02_Knowledge/technologies/services/agones/rancher-k3s-integration.md"
---

# Agones operations — troubleshooting and upgrades

## Overview

Operational playbook for Agones (CNCF sandbox project, v1.60.0): diagnosing
broken GameServers, reading controller and SDK-server logs, clearing stuck
states, avoiding port exhaustion, and upgrading the control plane. Exploratory
only — Agones is **not deployed** in the homelab, so the commands below are
generic `kubectl`/API workflows rather than live output.

## Details

### Diagnosing GameServer problems

- Reproduce the issue outside Kubernetes when possible: run the game server
  against a **local SDK server** so SDK integration problems surface before
  scheduling on the cluster.
- Run the failing workload as a single `GameServer` rather than a `Fleet` — a
  Fleet auto-replaces unhealthy GameServers, which can hide a persistent crash
  behind an endless replacement loop.
- Introspect with `kubectl describe gs <name>`, `kubectl describe pod <pod>`,
  `kubectl logs <pod>`, and `kubectl events` to see pod state and the events
  behind it.

### Viewing logs

- Control plane: `kubectl logs --namespace=agones-system agones-controller-<hash>`
  — the controller runs in the `agones-system` namespace.
- GameServer: SDK server sidecar logs — `kubectl logs <pod> -c agones-gameserver-sidecar`.
- Logs are JSON structured. Raise `sdkServer.logLevel` / controller `logLevel`
  to debug for more detail.
- The controller logs its `featureGates` in a log line — check this to confirm
  which feature gates are active (useful before and after upgrades).

### Common stuck states

- **GameServers won't delete after uninstall**: remove the finalizers via
  `kubectl patch` so the objects can be deleted.
- **Namespace stuck in `Terminating` after uninstall**: remove the finalizer
  via the Kubernetes API.
- **Forbidden errors**: on Kubernetes 1.12+ no special clusterrolebindings are
  needed, so a 403 usually points at something else (RBAC, webhooks, namespace).

### Port exhaustion

- The controller allocates GameServer ports from a configured range —
  `MinPort`/`MaxPort` (default 7000–8000 in the documented troubleshooting
  example).
- Ports are allocated dynamically; many concurrent GameServers can exhaust the
  range — plan capacity against `MinPort`/`MaxPort`.
- Homelab note: the target cluster is single-node k3s, so every GameServer host
  port comes from that one node's address space — the range is a hard ceiling
  on concurrently running servers.

### Image pulls

- `kubectl describe pod <pod>` shows pull errors, including image pull backoff
  states, in the pod's status and events.
- The SDK server sidecar is itself an image — if the sidecar image cannot be
  pulled, the whole Pod stays stuck even when the game image is fine.

### Upgrades

- Agones ships an upgrading guide under Installation/Upgrading in the docs —
  follow it for the current target version.
- Before upgrading, back up the current configuration and verify the current
  state, then walk through the guide step by step.
- Confirm the controller's `featureGates` before and after — upgrade versions
  can change gate defaults.

## Sources / Further Reading

- Agones troubleshooting guide: https://agones.dev/site/docs/guides/troubleshooting/
- Agones installation guide (upgrading): https://agones.dev/site/docs/installation/
- Agones documentation (v1.60.0): https://agones.dev/site/docs/
- Source repository: https://github.com/agones-dev/agones
- Companion notes: `./02_Knowledge/technologies/services/agones/install-config.md`
  (install/config) and `./02_Knowledge/technologies/services/agones/rancher-k3s-integration.md`
  (k3s wiring) — both planned siblings in this note set.
