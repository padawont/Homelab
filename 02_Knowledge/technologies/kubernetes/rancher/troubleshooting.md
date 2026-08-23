---
title: "Rancher troubleshooting"
status: draft
author: "padawont"
date: 2026-08-22
tags: [kubernetes, rancher, troubleshooting, certificates, fleet]
sources:
  - url: "https://ranchermanager.docs.rancher.com/"
    title: "Rancher Manager documentation"
  - url: "https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/install-upgrade-on-a-kubernetes-cluster/troubleshooting"
    title: "Troubleshooting the Rancher server cluster"
  - url: "https://ranchermanager.docs.rancher.com/reference-guides/rancher-webhook"
    title: "Rancher webhook"
  - url: "https://fleet.rancher.io/troubleshooting"
    title: "Fleet troubleshooting"
last_audit_date: 2026-08-22
related_docs:
  - "./02_Knowledge/technologies/kubernetes/rancher/architecture.md"
---

# Rancher troubleshooting

## Overview

Common Rancher failures in a homelab cluster around four areas: certificates,
agent connectivity, stuck cluster states, and webhooks. Start from the Rancher
server's own pods/logs, then check the downstream agents. Most issues are
symptomatic of a hostname/TLS mismatch or agent tunnel loss — see
./02_Knowledge/technologies/kubernetes/rancher/architecture.md for the connection model.

## Details

### Certificates

**Symptom**: browser shows cert errors; agents report `x509: certificate
signed by unknown authority`; UI refuses to load.

- Verify the hostname: the cert must match the hostname used by agents
  (`rancher.local` vs `rancher.local.` vs an IP).
- `ingress.tls.source=rancher` certs are auto-renewed by cert-manager; check
  `kubectl -n cattle-system get certificates` for Ready/True and cert-manager
  logs if renewal stalls.
- If using a private CA, downstream clusters must trust the CA (add it to the
  node's trust store or use `privateCA: true` in the registration).
- Rotation: see docs for updating the Rancher certificate; after manual
  rotation restart `cattle-cluster-agent` pods so they pick up the new CA.

### Agent connectivity

**Symptom**: cluster shows `Active` but `Waiting` / `Disconnected`; workloads
visible but kubectl from the UI fails; agents crash-loop.

- Agents connect **outbound** to the management server — confirm DNS for the
  hostname resolves from the downstream node and the HTTPS port is reachable.
- Check agent logs: `kubectl -n cattle-system logs deploy/cattle-cluster-agent`
  and `kubectl -n cattle-system logs deploy/cattle-node-agent`.
- Restart agents after any cert/hostname change: `kubectl -n cattle-system rollout restart deploy/cattle-cluster-agent`.
- If a cluster is stuck `Waiting`, re-run the registration command (Cluster →
  Edit → Save regenerates agent manifests) or check for a stale
  `cattle-cluster-agent` ServiceAccount token.

### Stuck clusters / nodes

**Symptom**: cluster stuck in `Provisioning`, nodes `Waiting`, or deletion hangs.

- Check the provisioning operator: `kubectl get clusters.provisioning.cattle.io -A` and its status conditions.
- For imported clusters, Rancher mostly mirrors upstream state — verify the
  cluster really is healthy with kubectl before blaming Rancher.
- Delete hangs usually mean finalizers are blocked on a downstream resource;
  find them with `kubectl get cluster -o yaml` and inspect `metadata.finalizers`.

### Webhooks

**Symptom**: resources fail to create/update with webhook admission errors;
`rancher-webhook` pod CrashLooping.

- The `rancher-webhook` Deployment validates Rancher CRs on the management
  cluster; check its logs first.
- Version skew: after upgrading Rancher without upgrading the webhook, or after
  downgrading, webhook and rancher versions mismatch — upgrade/rollback both
  together (webhook version = rancher version).
- If the webhook is broken it can block *all* management CR writes: look for
  `validatingwebhookconfiguration` entries and the webhook's TLS secret.

### Fleet

**Symptom**: GitRepo shows `ErrApplied` / stuck; bundles not deploying.

- `fleet-agent` must be running in the downstream cluster — check
  `kubectl get pods -n cattle-fleet-system`.
- Validate the GitRepo URL/branch and that credentials are correct (private
  repos need a secret).
- Use `fleet analyze` / `fleet monitor` / `fleet dump` (see the fleet CLI) or inspect
  `Bundle` status conditions for the failing resource.

### General diagnostic flow

1. `kubectl -n cattle-system get pods` — rancher, webhook, fleet healthy?
2. Server logs: `kubectl -n cattle-system logs deploy/rancher -f`.
3. Downstream: agent logs + `kubectl get clusters.management.cattle.io -A`.
4. Check cert-manager certificates and the ingress `tls` secret.
5. Re-run registration or restart agents only after fixing the root cause.

## Sources / Further Reading

- Troubleshooting the Rancher server cluster: https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/install-upgrade-on-a-kubernetes-cluster/troubleshooting
- Rancher webhook: https://ranchermanager.docs.rancher.com/reference-guides/rancher-webhook
- Fleet troubleshooting: https://fleet.rancher.io/troubleshooting
- Rancher Manager documentation: https://ranchermanager.docs.rancher.com/
