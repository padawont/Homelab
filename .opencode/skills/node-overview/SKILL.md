---
name: node-overview
description: >
  Standard read-only overview of the homelab main node (node-main,
  192.168.111.7): host health, k3s cluster state, what services are running vs
  down, plus error deep-dives explaining why. Trigger when the user asks for a
  node overview, what's running on the node, whether the node is healthy, what
  services are up/down, or why a service/pod is failing on node-main. Use when
  working on node-main or needing info about the node. Read-only — gathers info
  only, never edits, writes, or restarts anything.
---

# node-overview

Standard step-by-step overview of node-main. Run the read-only checks below in
order over SSH, then report the results in chat.

## Connection (via login-server skill)

- Use the `login-server` skill for ALL SSH: it handles `SSHPASS`, `sshpass`,
  the key-based fallback, and the `192.168.111.7` connection details. Do not
  duplicate or hardcode connection info here.
- Every check below runs as a remote command through `login-server`.
- kubectl on the node: `sudo k3s kubectl` (root) or
  `KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl` (runic).

## Guardrails (read-only — non-negotiable)

- NEVER edit, write, delete, create, or move any file or config — locally or
  on the node.
- NEVER mutate cluster or service state: no `kubectl apply/edit/delete/scale/
  cordon/drain`, no `helm install/upgrade/rollback`, no
  `systemctl start/stop/restart`, no `nixos-rebuild`, no `kill`.
- Use ONLY inspection commands: `kubectl get/describe/logs/events/top`,
  `systemctl status/list-units/list-unit-files`, `journalctl`, `df`, `free`,
  `lsblk`, `uptime`, `nixos-version`, `k3s crictl ps/images`.
- No output redirection to files, no `scp` to/from the node, no writing anything.
- If the overview reveals a problem that needs fixing, STOP — report findings
  and recommend the action. Do not perform it.
- When in doubt whether a command mutates state, do not run it; ask the user.

## Step-by-step overview

Run each step in order; record results as you go. Batch related commands per
SSH call.

Two scopes:
- **Kubernetes-only** (default): Steps 2–6. Use when the user only wants
  cluster/service state.
- **Full (includes host/system)**: Step 1 + Steps 2–6. Use ONLY when the work
  involves the node OS itself — systemd, disk, kernel, NixOS config.

### Step 1 — Host & system health *(optional — only in full scope)*
- identity/version: `hostname; uname -a; nixos-version`
- uptime/load: `uptime`
- memory: `free -h`
- disk space + inodes: `df -h; df -i`
- disk layout: `lsblk`
- failed systemd units: `systemctl list-units --type=service --state=failed`
- running systemd services: `systemctl list-units --type=service --state=running --no-pager`
- recent system errors: `journalctl -p err -b --no-pager --no-hostname | tail -50`
- k3s service: `sudo systemctl status k3s --no-pager -l` and `sudo journalctl -u k3s -b --no-pager -n 50`

### Step 2 — k3s cluster state
- nodes: `sudo k3s kubectl get nodes -o wide`
- node detail (conditions/taints/capacity): `sudo k3s kubectl describe node node-main`
- versions: `sudo k3s kubectl version`
- cluster-info: `sudo k3s kubectl cluster-info`
- namespaces: `sudo k3s kubectl get namespaces`

### Step 3 — Workloads: running vs not
- `sudo k3s kubectl get deploy,sts,ds,jobs -A -o wide`
- all pods wide: `sudo k3s kubectl get pods -A -o wide`
- problem pods only: `sudo k3s kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded -o wide`
- note READY (`0/1`), RESTARTS, and STATUS from the pod list

### Step 4 — Ingress, storage, endpoints
- ingresses: `sudo k3s kubectl get ingress -A`
- services + endpoints: `sudo k3s kubectl get svc,endpoints -A`
- storage: `sudo k3s kubectl get pvc,pv -A`

### Step 5 — Resource usage (CPU + RAM)
- nodes (CPU + memory): `sudo k3s kubectl top nodes`
- pods by CPU: `sudo k3s kubectl top pods -A --sort-by=cpu | head -20`
- pods by memory: `sudo k3s kubectl top pods -A --sort-by=memory | head -20`
- memory pressure (host, full scope only): `free -h` (already in Step 1 when in full scope)

### Step 6 — Error deep-dive (why things are down)
For every pod not Running/Ready/Completed from Step 3:
1. `sudo k3s kubectl describe pod -n <ns> <pod>`
2. `sudo k3s kubectl logs -n <ns> <pod> --tail=100`
3. if restarted: `sudo k3s kubectl logs -n <ns> <pod> --previous --tail=100`
4. cluster events: `sudo k3s kubectl get events -A --sort-by=.lastTimestamp`
5. image/CRI issues: `sudo k3s crictl images; sudo k3s crictl ps -a`
6. control-plane errors: `sudo journalctl -u k3s -b --no-pager -n 100`

### Interpretation table
| Pod status | Meaning | Likely cause |
|---|---|---|
| ImagePullBackOff / ErrImagePull | image can't be pulled | bad tag, registry down, no pull secret |
| CrashLoopBackOff | container keeps exiting | app error — check `logs --previous` |
| Pending | unscheduled | insufficient resources, taint, unbound PVC |
| ContainerCreating | stuck at create | volume mount, CNI, image pull |
| OOMKilled / high restarts | killed by memory | exceeds limits — check `top pods` |
| Completed | exited 0 | job/one-shot done — expected |

## Report (chat only)

Present a structured summary, never dump raw output. State which scope was run
(kubernetes-only vs full):
1. Host (full scope only): version, uptime, disk/RAM pressure, failed systemd units.
2. Cluster: node status/conditions, k3s version.
3. Layout: namespaces → workloads with status ✓ running / ✗ down.
4. Problems: each unhealthy pod + status + root cause (from Step 6).
5. Storage/resources: capacity notes, top consumers.
