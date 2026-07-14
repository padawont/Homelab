---
title: "Rancher Troubleshooting"
status: draft
author: padawont
date: 2026-07-11
tags:
  - rancher
  - troubleshooting
  - kubernetes
  - debugging
sources:
  - url: "https://ranchermanager.docs.rancher.com/troubleshooting/general-troubleshooting"
    title: "Rancher — Troubleshooting"
  - url: "https://ranchermanager.docs.rancher.com/faq/general-faq"
    title: "Rancher — FAQ"
  - url: "https://github.com/rancher/rancher/wiki"
    title: "Rancher Wiki"
last_audit_date: 2026-07-11
---

# Rancher Troubleshooting

## Prerequisites

- [Rancher instance](../rancher-install-k3d.md) — installed and accessible
- [Kubernetes Fundamentals](../) — K8s concepts (Pods, logs, events, DNS)
- [k3d Debugging](../k3d/debugging.md) — if running on k3d
- [Kubernetes Pods](../pods.md) — understanding of pod logs and describe

## Bootstrap Password Issues

**Symptom:** The login page says the bootstrap password is already set or the password doesn't work.

**Resolution:**

Retrieve the current bootstrap password from the Kubernetes secret:

```bash
kubectl get secret --namespace cattle-system bootstrap-secret \
  -o jsonpath='{.data.bootstrapPassword}' | base64 -d
```

If the secret does not exist:

```bash
kubectl -n cattle-system get secret | grep bootstrap
```

If missing entirely, you can force-reset it by deleting the existing secret (Rancher will recreate it):

```bash
kubectl -n cattle-system delete secret bootstrap-secret
kubectl -n cattle-system rollout restart deploy/rancher
```

Then re-retrieve the new password.

## Certificate Problems

**Symptom:** Browser shows "Your connection is not private" or `curl` returns SSL errors.

**Resolution for self-signed certs:**

Use `--insecure` with `curl`:

```bash
curl -sk https://rancher.127.0.0.1.nip.io/ping
```

Or add the Rancher CA to your system trust store:

```bash
# Extract the Rancher CA certificate
kubectl get secret --namespace cattle-system tls-rancher-ingress \
  -o jsonpath='{.data.ca\.crt}' | base64 -d > rancher-ca.crt

# Add to system trust store (Linux)
sudo cp rancher-ca.crt /usr/local/share/ca-certificates/rancher-ca.crt
sudo update-ca-certificates
```

**Symptom:** cert-manager is not issuing a certificate.

**Check cert-manager status:**

```bash
kubectl -n cert-manager get pods
kubectl -n cert-manager logs -l app=cert-manager --tail=50
kubectl describe certificate -n cattle-system tls-rancher-ingress
```

Common causes:
- cert-manager not yet installed before Rancher
- ClusterIssuer misconfigured (for Let's Encrypt)
- DNS challenge failed (domain not publicly resolvable)
- HTTP01 challenge failed (port 80 not reachable)

**Expired certificates:**

Delete the certificate and secret, and cert-manager will re-issue:

```bash
kubectl -n cattle-system delete certificate tls-rancher-ingress
kubectl -n cattle-system delete secret tls-rancher-ingress
```

Wait for cert-manager to re-issue (check `kubectl get certificate -n cattle-system`).

## Agent Connectivity Issues

**Symptom:** Downstream cluster shows "Unavailable", "Disconnected", or "Waiting" in the Rancher UI.

**Check the agent logs:**

```bash
kubectl -n cattle-system logs -l app=cattle-cluster-agent --tail=50
```

Common errors and their causes:

| Error | Likely Cause |
|---|---|
| `x509: certificate signed by unknown authority` | Agent doesn't trust the Rancher server cert. Check that the correct CA is configured on the agent |
| `connection refused` | Rancher server URL is not reachable from the agent. Check DNS and firewall |
| `401 Unauthorized` | Cluster registration token is invalid or expired. Re-import the cluster |
| `dial tcp: lookup rancher.example.com: no such host` | DNS resolution failure on the downstream cluster. Check CoreDNS config |

**Force agent restart:**

```bash
kubectl -n cattle-system delete pod -l app=cattle-cluster-agent
```

**Re-import the cluster:**

If the agent cannot recover, generate a new registration token from the Rancher UI and re-apply the import manifest:

1. Navigate to cluster → **⋮** → **View in API** → `clusterRegistrationTokens`
2. Copy the `insecureCommand` or `command`
3. Run the command on the downstream cluster

## Stuck Clusters

**Symptom:** Cluster stuck in "Provisioning", "Updating", or "Deleting" state for more than 10 minutes.

**Check CAPI resources:**

```bash
kubectl get cluster,clusterclass -n fleet-default
kubectl describe cluster <cluster-name> -n fleet-default
```

**Check agent status:**

```bash
kubectl -n cattle-system get pods
kubectl -n cattle-system describe pod -l app=cattle-cluster-agent
kubectl -n cattle-system describe pod -l app=cattle-node-agent
```

**Force remove annotation (last resort):**

If a cluster is stuck in "Deleting", remove the finalizer:

```bash
kubectl patch cluster <cluster-name> -n fleet-default -p '{"metadata":{"finalizers":[]}}' --type=merge
```

This should only be done if the downstream cluster has already been deleted independently and Rancher is waiting for confirmation.

## Webhook Errors

**Symptom:** `rancher-webhook` is crash-looping or admission webhook errors prevent resource creation.

**Check webhook status:**

```bash
kubectl -n cattle-system get pods | grep webhook
kubectl -n cattle-system logs -l app=rancher-webhook --tail=50
```

**Temporary bypass:**

If a misconfigured webhook is blocking critical operations:

```bash
kubectl delete validatingwebhookconfiguration rancher.cattle.io
kubectl delete mutatingwebhookconfiguration rancher.cattle.io
```

Rancher will recreate these on the next restart. This is a last resort — diagnose the root cause first.

**Cert mismatch:**

If the webhook cannot read its serving cert:

```bash
kubectl -n cattle-system describe secret rancher-webhook-tls
kubectl -n cattle-system get certificate rancher-webhook-serving
```

Delete and let cert-manager re-issue if the certificate is missing or expired.

## Fleet / GitOps Issues

**Symptom:** GitRepo bundle is not deploying to downstream clusters.

**Check Fleet agent logs:**

```bash
kubectl -n cattle-fleet-system logs -l app=fleet-agent --tail=50
```

**Check bundle status:**

```bash
kubectl get bundles -n fleet-default
kubectl describe bundle <bundle-name> -n fleet-default
```

**Common causes:**

- Git credentials are missing or expired (check `GitRepo` spec)
- Bundle path in the repository doesn't match the `paths` field in `GitRepo`
- Workspace mismatch — the `GitRepo` must be in the same workspace as the target cluster group
- Downstream cluster Fleet agent not connected (see Agent Connectivity Issues above)

## Monitoring and Logging Issues

**Symptom:** Prometheus is not scraping targets.

```bash
kubectl -n cattle-monitoring-system get prometheus
kubectl -n cattle-monitoring-system get servicemonitors
kubectl -n cattle-monitoring-system get podmonitors
```

Check that `ServiceMonitor` selectors match the target service labels.

**Symptom:** Grafana dashboards show no data.

```bash
kubectl -n cattle-monitoring-system get pods | grep grafana
kubectl -n cattle-monitoring-system logs -l app=grafana --tail=20
```

Check Grafana datasource configuration — the Prometheus datasource URL must match the Prometheus service name.

**Symptom:** No logs appearing in Elasticsearch from rancher-logging.

```bash
kubectl get clusteroutputs -A
kubectl get clusterflows -A
kubectl -n cattle-logging-system logs -l app=fluentd --tail=50
```

Verify the Elasticsearch host is reachable from the Fluentd pods.

## General Debugging Commands

```bash
# Recent events in cattle-system
kubectl get events -n cattle-system --sort-by='.lastTimestamp' | tail -20

# Rancher pod logs
kubectl -n cattle-system logs -l app=rancher --tail=100

# All Rancher pods status
kubectl -n cattle-system get pods -o wide

# Describe Rancher pod (for crash reasons)
kubectl -n cattle-system describe pod -l app=rancher

# Check Helm release status
helm list -n cattle-system
helm status rancher -n cattle-system
```

## References

- [Rancher Troubleshooting](https://ranchermanager.docs.rancher.com/troubleshooting/general-troubleshooting)
- [Rancher FAQ](https://ranchermanager.docs.rancher.com/faq/general-faq)
- [Rancher Wiki — Troubleshooting](https://github.com/rancher/rancher/wiki/Troubleshooting)
- [Rancher Community Forums](https://forums.rancher.com/)
