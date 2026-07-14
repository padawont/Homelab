---
title: "Helm Repository Management"
status: draft
author: padawont
date: 2026-07-11
tags:
  - kubernetes
  - helm
  - repositories
  - oci
  - package-management
sources:
  - url: "https://helm.sh/docs/topics/chart_repository/"
    title: "Helm Repositories — Helm Documentation"
  - url: "https://helm.sh/docs/topics/registries/"
    title: "Helm OCI Support — Helm Documentation"
last_audit_date: 2026-07-11
---

# Helm Repository Management

Helm charts are distributed through chart repositories or OCI-compliant container registries.

## Chart Repositories

A chart repository is an HTTP/HTTPS server hosting an `index.yaml` file and packaged `.tgz` charts.

### helm repo add

Add a chart repository:

```bash
# Add a public repository
helm repo add bitnami https://charts.bitnami.com/bitnami

# Add a repository with authentication
helm repo add private-repo https://charts.example.com \
  --username myuser \
  --password mypass

# Add a repository with a CA certificate
helm repo add custom-repo https://charts.example.com \
  --ca-file ca.crt

# Add a repository with client certificate
helm repo add secure-repo https://charts.example.com \
  --cert-file client.crt \
  --key-file client.key

# Add a repository
helm repo add myrepo https://charts.example.com
```

> **Note:** OCI registries are not added via `helm repo add`. Instead, use `oci://` URLs directly with `helm install`, `helm pull`, `helm upgrade`, etc. after authenticating with `helm registry login`.

### helm repo update

Refresh the local cache of all added repositories:

```bash
# Update all repositories
helm repo update

# Update a specific repository
helm repo update bitnami
```

### helm repo list

List configured repositories:

```bash
# List all repositories
helm repo list

# List in JSON format
helm repo list --output json

# List in YAML format
helm repo list --output yaml
```

Output example:

```
NAME      URL
bitnami   https://charts.bitnami.com/bitnami
stable    https://charts.helm.sh/stable
```

### helm repo remove

Remove a repository:

```bash
helm repo remove bitnami
```

## Repository Index

The repository `index.yaml` contains metadata about all available charts:

```yaml
apiVersion: v1
entries:
  nginx:
    - apiVersion: v2
      appVersion: 1.25.0
      created: "2024-01-01T00:00:00Z"
      description: A Helm chart for Kubernetes
      digest: sha256:abc123...
      home: https://github.com/bitnami/charts
      name: nginx
      type: application
      urls:
        - https://charts.bitnami.com/bitnami/nginx-15.0.0.tgz
      version: 15.0.0
generated: "2024-01-01T00:00:00Z"
```

### Searching Charts

```bash
# Search Artifact Hub (cross-repo search)
helm search hub nginx

# Search configured repositories
helm search repo nginx

# Search with version matching
helm search repo nginx --versions

# Filter by regex
helm search repo nginx --regexp "^nginx-ingress"

# Output as JSON
helm search repo nginx --output json
```

## OCI Registries

Helm supports storing charts in OCI-compliant container registries (Docker Hub, GitHub Container Registry, Harbor, ACR, ECR, GCR).

### Requirements

- Helm 4+ (OCI is fully GA)
- `helm registry login` for authentication

### Authentication

```bash
# Login to an OCI registry
helm registry login registry.example.com \
  --username myuser \
  --password mypass

# Login with token
helm registry login ghcr.io \
  --username myuser \
  --password $GITHUB_TOKEN

# Login from stdin
echo $PASSWORD | helm registry login registry.example.com \
  --username myuser \
  --password-stdin

# Logout
helm registry logout registry.example.com
```

### Pulling Charts from OCI

```bash
# Pull chart from OCI registry
helm pull oci://ghcr.io/owner/chart --version 1.0.0

# Pull and untar
helm pull oci://ghcr.io/owner/chart --version 1.0.0 --untar

# Pull to specific directory
helm pull oci://ghcr.io/owner/chart --version 1.0.0 \
  --untar \
  --untardir ./charts
```

### Installing from OCI

```bash
# Install directly from OCI
helm install my-release oci://ghcr.io/owner/chart --version 1.0.0

# Install with values
helm install my-release oci://ghcr.io/owner/chart \
  --version 1.0.0 \
  --values prod-values.yaml
```

### Pushing Charts to OCI

```bash
# Push a packaged chart
helm push mychart-0.1.0.tgz oci://ghcr.io/owner/charts

# Push (version must differ from existing)
helm push mychart-0.1.0.tgz oci://ghcr.io/owner/charts
```

### OCI Repository Structure

Charts pushed to OCI registries are stored as artifacts with media type `application/vnd.cncf.helm.chart.content.v1.tar+gzip`:

```
oci://ghcr.io/owner/charts/mychart
├── 1.0.0          # Tag for version 1.0.0
├── 1.1.0          # Tag for version 1.1.0
└── 2.0.0          # Tag for version 2.0.0
```

## Repository vs OCI Comparison

| Feature | Standard Repo | OCI Registry |
|---|---|---|
| Protocol | HTTP/HTTPS | OCI distribution spec |
| Index | index.yaml | Registry API (tags) |
| Authentication | Basic auth, certs | Docker-compatible auth |
| Authorization | N/A | Registry RBAC |
| Multi-arch | N/A | N/A (charts are single blobs) |
| Garbage collection | Manual | Registry-native |
| Required Helm version | Any | 3.8+ |

## Chart Signing and Verification

Charts can be signed with GPG for integrity verification:

```bash
# During packaging
helm package --sign --key mykey --keyring ~/.gnupg/secring.gpg ./mychart

# Verify during install
helm install my-release ./mychart-0.1.0.tgz --verify

# Verify with keyring
helm install my-release ./mychart-0.1.0.tgz \
  --verify \
  --keyring ~/.gnupg/pubring.gpg
```

> **GnuPG v2 note:** GnuPG v2 stores secret keys in `pubring.kbx` format — `secring.gpg` is not generated by default. Export with: `gpg --export-secret-keys --export-secret-subkeys >~/.gnupg/secring.gpg`

## Proxied Repositories

For air-gapped or proxy environments:

```bash
# Use HTTP proxy
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Use local mirror
helm repo add internal-mirror https://charts.internal.example.com

# Download chart for air-gapped install
helm pull bitnami/nginx --version 15.0.0
# Transfer to air-gapped system
helm install my-release ./nginx-15.0.0.tgz
```

## References

- [Helm Repositories](https://helm.sh/docs/topics/chart_repository/)
- [Helm OCI Support](https://helm.sh/docs/topics/registries/)
- [Helm Chart Signing](https://helm.sh/docs/topics/provenance/)
