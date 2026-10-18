---
title: "Longhorn storage — Rollback"
status: active
author: "padawont"
date: 2026-10-02
tags: [kubernetes, storage, longhorn, rollback]
technologies: [longhorn, helm, iscsi, kubernetes]
related_docs:
  - "./overview.md"
  - "./05_Implementations/node-main/k3s/overview.md"
references:
  online:
    - url: "https://longhorn.io/docs/latest/deploy/uninstall/"
      title: "Longhorn uninstall"
  repo:
    - "./overview.md"
node: node-main
---

# Longhorn storage — Rollback

Remove Longhorn from `node-main`. **This destroys all volumes and their data.**
Confirm nothing depends on Longhorn before proceeding.

## Prerequisites

- Helm and `kubectl` pointed at the cluster.
- A copy of any data you need off Longhorn volumes.
- Confirmation of the impact of losing the default StorageClass (`longhorn`) —
  new PVCs need another provisioner (e.g. `local-path` re-enabled).

## Rollback steps

1. Uninstall the release:

```bash
helm uninstall longhorn -n longhorn-system
```

2. Delete the namespace:

```bash
kubectl delete namespace longhorn-system
```

3. Remove the Longhorn CRDs:

```bash
kubectl get crd -o name | grep longhorn.io | xargs -r kubectl delete
```

4. Stop iSCSI and unmount the data path **before** wiping it:

```bash
sudo systemctl stop iscsid
sudo umount /var/lib/longhorn
```

5. Wipe the data directories (destroys all volume data):

```bash
sudo rm -rf /var/lib/longhorn /var/lib/longhorn-ssd
```

6. Optionally remove the disk-1 `/etc/fstab` entry:

```
UUID=6d6a0b8c-0c6f-44ce-a627-8a59346820f4 /var/lib/longhorn ext4 defaults,noatime 0 2
```

## Verification

```bash
kubectl get ns longhorn-system              # not found
kubectl get crd | grep longhorn.io          # empty
kubectl get storageclass                    # longhorn / longhorn-static gone
findmnt /var/lib/longhorn                   # not mounted
```

If dynamic provisioning is still needed, restore the default StorageClass
annotation on `local-path` (or choose another provisioner).
