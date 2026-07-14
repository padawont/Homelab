---
title: "k3d Registry Integration"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k3d
  - registry
  - kubernetes
  - docker
sources:
  - url: "https://k3d.io/v5.6.0/usage/registries/"
    title: "k3d — Using Image Registries"
  - url: "https://k3d.io/v5.6.0/usage/importing_images/"
    title: "k3d — Importing Images"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_registry_create/"
    title: "k3d registry create command"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_image_import/"
    title: "k3d image import command"
last_audit_date: 2026-07-10
---

# k3d Registry Integration

k3d clusters run k3s, which uses **containerd** (not the Docker daemon) to pull and run images. This means images available in your local Docker store are not automatically available inside the cluster. You must either:

1. Push images to a registry accessible from the cluster nodes
2. Import images directly into the k3s nodes

## Why a Registry Is Needed

In a standard Docker-based dev setup, `docker build` makes images available to `docker run`. With k3d, the k3s nodes are separate containers that don't share the Docker daemon's image cache. A registry bridges this gap: you push images to it, and containerd in the k3s nodes pulls from it.

---

## k3d-Managed Registry

### Create During Cluster Creation

```bash
k3d cluster create mycluster --registry-create mycluster-registry
```

This creates the cluster together with a registry container named `mycluster-registry`. The registry is automatically configured in containerd's `registries.yaml`. A random host port is mapped — check `docker ps -f name=mycluster-registry` to find it.

### Create a Standalone Registry

```bash
k3d registry create myregistry.localhost --port 12345
```

Creates a registry container named `k3d-myregistry.localhost` (k3d prefixes all resources with `k3d-`). The registry listens on port 12345 on the host.

Flags:
- `--port [HOST:]HOSTPORT` — specify the host port (default: random)
- `--image string` — registry image (default: `docker.io/library/registry:2`)
- `--volume [SOURCE:]DEST` — persist registry data
- `--proxy-remote-url string` — create a pull-through cache (proxy registry)

### Use an Existing k3d-Managed Registry

```bash
k3d cluster create newcluster --registry-use k3d-myregistry.localhost:12345
```

### List Registries

```bash
k3d registry list
```

### Delete a Registry

```bash
k3d registry delete myregistry.localhost
```

---

## Push to the Registry

```bash
# Tag your local image with the registry address
docker tag myapp:latest localhost:12345/myapp:latest

# Push to the registry
docker push localhost:12345/myapp:latest
```

For `*.localhost` registries (e.g. `myregistry.localhost`), `nss-myhostname` (Linux) resolves them to 127.0.0.1 automatically. On other platforms, add a `/etc/hosts` entry:

```
127.0.0.1 myregistry.localhost
```

Alternatively, use `localhost:<port>` directly for push operations.

---

## Reference Images in Manifests

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
        - name: myapp
          image: myregistry.localhost:12345/myapp:latest
          imagePullPolicy: Always
```

The `imagePullPolicy: Always` is important when tags don't change between pushes (e.g. `:latest`).

---

## Direct Image Import (No Registry)

For quick testing without a registry:

```bash
k3d image import myimage:latest --cluster mycluster
```

Import modes (auto-detected):
- **Direct** — loads images directly into k3s node containers (no separate container spawned)
- **Tools Node** — starts a `k3d-tools` container, copies images there, then loads into nodes
- **Auto** — uses direct for local Docker, tools-node for remote runtimes

---

## Registries Configuration File (registries.yaml)

For advanced registry setups (external registries, authentication, TLS):

```bash
k3d cluster create mycluster --registry-config /path/to/registries.yaml
```

### Mirrors

```yaml
mirrors:
  "my.company.registry:5000":
    endpoint:
      - http://my.company.registry:5000
```

### Authentication

```yaml
mirrors:
  my.company.registry:
    endpoint:
      - http://my.company.registry
configs:
  my.company.registry:
    auth:
      username: aladin
      password: abracadabra
```

### TLS / Secure Registries

```yaml
mirrors:
  my.company.registry:
    endpoint:
      - https://my.company.registry
configs:
  my.company.registry:
    tls:
      ca_file: "/etc/ssl/certs/my-company-root.pem"
```

Mount the CA certificate when creating the cluster:

```bash
k3d cluster create \
  --volume "${HOME}/.k3d/my-company-root.pem:/etc/ssl/certs/my-company-root.pem"
```

### Embedded in Config File

Registries config can also be embedded directly in the k3d YAML config:

```yaml
apiVersion: k3d.io/v1alpha5
kind: Simple
metadata:
  name: test
servers: 1
agents: 2
registries:
  create:
    name: myregistry
  config: |
    mirrors:
      "my.company.registry":
        endpoint:
          - http://my.company.registry:5000
```

---

## Registry Proxy / Pull-Through Cache

Create a registry that mirrors DockerHub (or another registry) and caches images locally:

```yaml
registries:
  create:
    name: registry.localhost
    host: "0.0.0.0"
    hostPort: "5000"
    proxy:
      remoteURL: https://registry-1.docker.io
      username: ""
      password: ""
```

---

## Testing Your Registry

```bash
# Deploy a test nginx from the registry
kubectl create deployment nginx --image=myregistry.localhost:12345/nginx:latest

# Verify the pod is running
kubectl get pods

# Inspect the registry contents
curl http://localhost:12345/v2/_catalog
```
