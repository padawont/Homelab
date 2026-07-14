# node-1

ASUS ROG STRIX B550-I Gaming — AMD Ryzen 7 5700G, 32 GB RAM

**Role:** K3s server node with Longhorn distributed storage and Rancher management.

## Services

- **K3s** — Kubernetes server (v1.35.5+k3s1)
- **Docker** — container runtime (used by Longhorn)
- **Open iSCSI** — iSCSI initiator for Longhorn
- **Longhorn** — distributed block storage (mounted at `/var/lib/longhorn` on `/dev/sda`)
- **Rancher** — multi-cluster management (LoadBalancer at 192.168.111.100)
- **Cert-Manager** — certificate management
- **MetalLB** — bare-metal load balancer (FRR mode)
- **Fleet** — GitOps continuous delivery

## Network

| Interface | IP | Purpose |
|---|---|---|
| `enp6s0` | 192.168.111.10/24 | Main LAN |
| `docker0` | 172.17.0.1/16 | Docker bridge |
| `br-12f9262f83dd` | 172.18.0.1/16 | Docker bridge |
| `cni0` | 10.42.0.1/24 | Flannel/K8s pod network |
| `flannel.1` | 10.42.0.0/32 | Flannel overlay |

**MAC** (primary NIC): `fc:34:97:65:e9:69`

## Storage

| Device | Size | Mount |
|---|---|---|
| `nvme0n1` | 447.1G | `/` (100G), `/home` (338.6G), `/boot` (512M), swap (8G) |
| `sda` | 953.9G | `/var/lib/longhorn` (Longhorn backing store) |
| `sdb` | 465.8G | Unmounted / unknown partition layout |
| `sdc` | 58.6G | Removable / NixOS installer |

## Firewall

| Port | Protocol | Purpose |
|---|---|---|
| 22 | TCP | SSH |
| 80 | TCP | HTTP (Rancher) |
| 443 | TCP | HTTPS (Rancher) |
| 6443 | TCP | K3s API |
| 8472 | UDP | Flannel VXLAN / Longhorn |
