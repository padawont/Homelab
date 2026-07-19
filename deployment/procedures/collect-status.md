# Collect Cluster Status Snapshot

## Prerequisites

- SSH access to node-1 (see `.opencode/skills/ssh-node-1/SKILL.md`)
  - `sshpass` installed on local machine
  - Password configured for `nixos@192.168.111.10`
- kubectl configured on node-1 (default with K3s)
- Git working tree clean before starting

## Steps

### 1. Collect Software Versions

SSH into node-1 and run:

```bash
sshpass -p 'nixos' ssh -o StrictHostKeyChecking=no nixos@192.168.111.10 "
  echo '=== K3S VERSION ===' && k3s --version && \
  echo '=== KUBECTL VERSION ===' && kubectl version && \
  echo '=== HELM VERSION ===' && helm version && \
  echo '=== HELM LIST ===' && helm list -A && \
  echo '=== NIXOS VERSION ===' && nixos-version && \
  echo '=== KERNEL ===' && uname -r && \
  echo '=== NODES ===' && kubectl get nodes -o wide && \
  echo '=== ALL PODS ===' && kubectl get pods --all-namespaces -o wide
" > .opencode/tmp/versions-raw.txt
```

Parse the output into `status/versions/{date}-snapshot.md` (see `status/versions/2026-07-19-snapshot.md` for format reference).

### 2. Collect Hardware Utilization

SSH into node-1 and run:

```bash
sshpass -p 'nixos' ssh -o StrictHostKeyChecking=no nixos@192.168.111.10 "
  echo '=== FREE ===' && free -h && \
  echo '=== DF ===' && df -h && \
  echo '=== UPTIME ===' && uptime && \
  echo '=== TOP NODES ===' && kubectl top nodes && \
  echo '=== TOP PODS ===' && kubectl top pods -A && \
  echo '=== LSBK ===' && lsblk && \
  echo '=== NPROC ===' && nproc
" > .opencode/tmp/hardware-raw.txt
```

Parse the output into `status/hardware/node-1-{date}.md` (see `status/hardware/node-1-2026-07-19.md` for format reference).

### 3. Verify Deployed Configs Against Inventory

```bash
sshpass -p 'nixos' ssh -o StrictHostKeyChecking=no nixos@192.168.111.10 "kubectl get all -A" > .opencode/tmp/all-resources.txt
```

For each entry in `status/current-config/kubernetes.md`:
- Verify the file exists under `configs-and-adr/node-main/kubernetes/`
- Verify the resources defined in the file exist on cluster (from `kubectl get all -A`)
- Set `Last Applied` to today's date

For each entry in `status/current-config/nixos.md`:
- Verify the file exists under `configs-and-adr/node-main/OS/`
- Set `Last Applied` to today's date

Check for any new manifest files on disk not yet listed in the inventory table and add them.

### 4. Update ADR Diagrams

Check `configs-and-adr/adr/` for any new ADRs:

```bash
ls configs-and-adr/adr/
```

If new ADRs exist, update `status/current-adr/kubernetes.md` and/or `status/current-adr/nixos.md` Mermaid diagrams to include them.

### 5. Validate Frontmatter

Ensure all created/modified files pass `status/AGENTS.md` frontmatter requirements:
- `status/versions/{date}-snapshot.md`: `snapshot_date`, `ci_job`, `generated`
- `status/hardware/node-1-{date}.md`: `snapshot_date`, `ci_job`, `generated`
- `status/current-config/kubernetes.md`: `snapshot_date`, `domain`
- `status/current-config/nixos.md`: `snapshot_date`, `domain`
- `status/current-adr/kubernetes.md`: `snapshot_date`, `domain`, `updated_by`, `related_adrs`
- `status/current-adr/nixos.md`: `snapshot_date`, `domain`, `updated_by`, `related_adrs`

### 6. Run Validation Pipeline

Execute the 5-stage validation from the issue template (see issue #3 Validations section). If any stage fails, fix and re-run. Maximum 3 retry loops.

## Rollback

```bash
# If snapshots contain stale or incorrect data:
git revert <commit-hash>

# If only current-config needs restore:
git checkout HEAD~1 -- status/current-config/kubernetes.md
git checkout HEAD~1 -- status/current-config/nixos.md

# Delete erroneous snapshot files:
rm status/versions/{wrong-date}-snapshot.md
rm status/hardware/node-1-{wrong-date}.md

# Commit the rollback:
git add -A
git commit -m "fix(status): revert incorrect snapshot data"
```
