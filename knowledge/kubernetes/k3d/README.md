# k3d

Reference notes on [k3d](https://k3d.io/) — a lightweight wrapper to run [k3s](https://github.com/rancher/k3s) (Rancher Lab's minimal Kubernetes distribution) in Docker containers. These notes cover local development cluster lifecycle, configuration, registry integration, volumes, networking, and debugging.

Prerequisites: Docker >= v20.10.5 and [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl). See the [Kubernetes](../) notes for prerequisite concepts (architecture, Pods, Services, Ingress, storage).

## Getting Started

| File | Description |
|---|---|
| [installation.md](installation.md) | Install k3d via Homebrew, curl script, Chocolatey, and other package managers |
| [cluster-lifecycle.md](cluster-lifecycle.md) | Create, start, stop, delete, and list clusters; manage kubeconfig |

## Configuration

| File | Description |
|---|---|
| [cluster-configuration.md](cluster-configuration.md) | Multi-node clusters, port mappings, load balancer, `--api-port`, `--k3s-arg`, and YAML config files |
| [registry-integration.md](registry-integration.md) | Local image registry for pushing images to k3d clusters; image import modes |
| [volume-mounts.md](volume-mounts.md) | Host-to-node volume mounts for persistent data and config injection |

## Networking & Debugging

| File | Description |
|---|---|
| [networking.md](networking.md) | Port forwarding, ServersLB, DNS resolution, ingress via Traefik, Docker networking |
| [debugging.md](debugging.md) | Node logs, exec into nodes, registry inspection, common issues and fixes |
