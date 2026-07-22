# Deploy Forgejo

## Prerequisites

- kubectl configured for node-1 context
- MetalLB with available IP in the homelab pool (192.168.111.100-192.168.111.120)
- Longhorn storage class
- Access to `codeberg.org/forgejo/forgejo:16` container image

## Steps

### 1. Apply the K8s manifest

```bash
kubectl apply -f configs-and-adr/node-main/kubernetes/forgejo.yaml
```

This creates:
- Namespace `forgejo`
- PVC `forgejo-data` (10Gi Longhorn)
- Deployment `forgejo` (image `codeberg.org/forgejo/forgejo:16`)
- LoadBalancer service on 192.168.111.103 (HTTP port 80 -> 3000)
- NodePort service for SSH (port 2222 -> 30022)
- NetworkPolicy restricting ingress to metallb-system and rancher namespaces

### 2. Wait for pod readiness

```bash
kubectl wait --for=condition=ready pod -l app=forgejo -n forgejo --timeout=300s
```

### 3. Verify web UI

```bash
curl -s -o /dev/null -w '%{http_code}' http://192.168.111.103
# Expected: 200
```

### 4. Create admin user

Forgejo auto-initializes with SQLite on first startup. Create the admin user using the forgejo CLI:

```bash
kubectl exec -n forgejo deploy/forgejo -- su git -c '
  forgejo --work-path /data/gitea admin user create \
    --username <admin-username> \
    --password <secure-password> \
    --email <admin@example.com> \
    --admin
'
```

Note: The username `admin` is reserved. Use a different username.

### 5. Lock installation

Update the app.ini to set `INSTALL_LOCK = true`:

```bash
kubectl exec -n forgejo deploy/forgejo -- sed -i \
  's/INSTALL_LOCK = false/INSTALL_LOCK = true/' \
  /data/gitea/conf/app.ini
```

Then restart the pod:

```bash
kubectl rollout restart -n forgejo deploy/forgejo
kubectl wait --for=condition=ready pod -l app=forgejo -n forgejo --timeout=120s
```

### 6. Verify Forgejo Actions

Forgejo Actions is enabled by default via the `FORGEJO__actions__ENABLED=true` env var. Verify in the web UI at Site Administration -> Actions.

### 7. Create a test repository

```bash
# Create via API
curl -s -X POST http://192.168.111.103/api/v1/user/repos \
  -u '<username>:<password>' \
  -H 'Content-Type: application/json' \
  -d '{"name":"test-repo","auto_init":true,"readme":"Default"}'

# Clone and push
git clone http://<username>:<password>@192.168.111.103/<username>/test-repo.git
cd test-repo
echo "test" > README.md
git add README.md
git commit -m "Initial commit"
git push origin main
```

### 8. Test SSH access

```bash
ssh -p 30022 -o StrictHostKeyChecking=no git@192.168.111.103
# Expected: Permission denied (publickey) — means SSH server is running
```

## Configuration

Key environment variables set in the manifest:

| Variable | Value | Description |
|---|---|---|
| `FORGEJO__server__DOMAIN` | `192.168.111.103` | Server domain for clone URLs |
| `FORGEJO__server__ROOT_URL` | `http://192.168.111.103` | External access URL |
| `FORGEJO__server__START_SSH_SERVER` | `true` | Use built-in SSH on port 2222 |
| `FORGEJO__server__SSH_PORT` | `2222` | SSH port (2222 to avoid host sshd conflict) |
| `FORGEJO__actions__ENABLED` | `true` | Enable Forgejo Actions |
| `FORGEJO__actions__DEFAULT_ACTIONS_URL` | `https://data.forgejo.org` | Default action source |

## Rollback

```bash
kubectl delete namespace forgejo
kubectl delete -f configs-and-adr/node-main/kubernetes/forgejo.yaml
```

This destroys all resources including the PVC (data loss).

## Post-Deployment

1. Register a Forgejo Runner (separate future issue)
2. Set up DNS record for `git.homelab.internal` pointing to 192.168.111.103
3. Deploy Ingress controller and cert-manager for TLS termination
4. Migrate from SQLite to Postgres for production use
5. Create a test workflow in `.forgejo/workflows/` to verify CI
