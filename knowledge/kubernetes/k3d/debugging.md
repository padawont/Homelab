---
title: "k3d Debugging"
status: draft
author: padawont
date: 2026-07-10
tags:
  - k3d
  - debugging
  - kubernetes
  - troubleshooting
sources:
  - url: "https://k3d.io/v5.6.0/faq/faq/"
    title: "k3d — FAQ"
  - url: "https://k3d.io/v5.6.0/faq/compatibility/"
    title: "k3d — Compatibility"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_node/"
    title: "k3d node commands"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_node_create/"
    title: "k3d node create command"
  - url: "https://k3d.io/v5.6.0/usage/commands/k3d_version/"
    title: "k3d version command"
last_audit_date: 2026-07-10
---

# k3d Debugging

## Node Logs

View logs from a node container using Docker:

```bash
docker logs k3d-mycluster-server-0
```

Tail and follow logs:

```bash
docker logs --tail 50 --follow k3d-mycluster-server-0
```

## Execute Commands Inside Nodes

Open a shell on a node using Docker:

```bash
docker exec -it k3d-mycluster-server-0 sh
```

Run a single command:

```bash
docker exec k3d-mycluster-server-0 crictl images
docker exec k3d-mycluster-server-0 journalctl -u k3s --no-pager | tail -30
```

## Registry Inspection

List registries:

```bash
k3d registry list
```

Check registry API (must be running):

```bash
curl http://localhost:12345/v2/_catalog
```

JSON output of registry state:

```bash
k3d registry list -o json | jq
```

## Cluster State

List all clusters with detailed status:

```bash
k3d cluster list
```

JSON output for scripting:

```bash
k3d cluster list -o json | jq '.Clusters[] | {name: .Name, nodes: [.Nodes[].Name]}'
```

## Available k3s Versions

```bash
k3d version list k3s
```

Shows available k3s image versions that can be used with `--image`.

---

## Common Issues

| Problem | Cause | Fix |
|---|---|---|
| Port already in use | Another process or k3d cluster uses the same port | Change `--api-port` or `-p` values |
| ImagePullBackOff on pods | Registry not configured or unreachable | Use `--registry-use`, `--registry-create`, or `k3d image import` |
| Pods stuck in Pending | Disk pressure / insufficient resources | Adjust kubelet eviction thresholds via `--k3s-arg` |
| Kubeconfig not working | Wrong context or kubeconfig not merged | `k3d kubeconfig merge --kubeconfig-switch-context` |
| Docker not found | Docker daemon not running | Start Docker first, then retry |
| Cannot push to registry | Registry not running or wrong address | `k3d registry list` to verify, check `docker ps` |
| Multi-server restart fails | dqlite (pre-etcd) doesn't allow initial server to go down | Use embedded etcd (k3s >= v1.21) |

### Pod Evictions Due to Disk Pressure

```bash
k3d cluster create \
  --k3s-arg '--kubelet-arg=eviction-hard=imagefs.available<1%,nodefs.available<1%@agent:*' \
  --k3s-arg '--kubelet-arg=eviction-minimum-reclaim=imagefs.available=1%,nodefs.available=1%@agent:*'
```

### Docker Hub Pull Rate Limit

If k3s nodes hit Docker Hub's pull rate limit, configure authenticated containerd access:

```yaml
# registries.yaml
mirrors:
  docker.io:
    endpoint:
      - https://docker.io
configs:
  docker.io:
    auth:
      username: <your-dockerhub-username>
      password: <your-dockerhub-token>
```

Then create the cluster with `--registry-config registries.yaml`.

### BTRFS Filesystem Issues

On systems with BTRFS, mount `/dev/mapper` into the nodes:

```bash
k3d cluster create mycluster -v /dev/mapper:/dev/mapper
```

### ZFS Filesystem Issues

k3s does not support ZFS. Multi-server setups fail with raft init errors. Workaround: configure Docker to use a different filesystem (e.g. overlay2).

### Nodes Stuck in NotReady (nf_conntrack_max)

```bash
# Workaround: reduce conntrack max per core (fixed in k3s v1.21.1+)
k3d cluster create mycluster --k3s-arg "--kube-proxy-arg=conntrack-max-per-core=0@all"
```

### Access Services on the Docker Host from the Cluster

Use the `host.k3d.internal` DNS name (resolves to the Docker network gateway):

```bash
curl http://host.k3d.internal:5432  # Connect to a DB running on host
```

### Spurious PID Entries After Delete

After deleting a k3d cluster with shared mounts, `/proc` may show stale PID entries. Remount `/proc` in the affected containers or restart Docker.

---

## Cleanup

Remove all clusters and registries:

```bash
k3d cluster delete --all
k3d registry delete --all
```
