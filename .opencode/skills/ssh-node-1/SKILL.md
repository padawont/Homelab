---
name: ssh-node-1
description: SSH into node-1 (192.168.111.10) — run commands and transfer files on the NixOS machine using password authentication.
---

# SSH into node-1

## Prerequisites

- `sshpass` must be installed. Check with:
  ```bash
  which sshpass
  ```

## Run a command

```bash
sshpass -p 'nixos' ssh -o StrictHostKeyChecking=no nixos@192.168.111.10 "<command>"
```

## Run multiple commands

Chain with `&&`:

```bash
sshpass -p 'nixos' ssh -o StrictHostKeyChecking=no nixos@192.168.111.10 "cmd1 && cmd2 && cmd3"
```

Use `;` if partial failure is acceptable.

## Copy a file from node-1 to local

```bash
sshpass -p 'nixos' scp -o StrictHostKeyChecking=no nixos@192.168.111.10:/remote/path /local/path
```

## Copy a file from local to node-1

```bash
sshpass -p 'nixos' scp -o StrictHostKeyChecking=no /local/path nixos@192.168.111.10:/remote/path
```

## Copy a directory recursively

Add `-r`:

```bash
sshpass -p 'nixos' scp -o StrictHostKeyChecking=no -r nixos@192.168.111.10:/remote/dir /local/dir
```

## Security note

`nixos` is the default NixOS live ISO password. This skill is for initial bootstrap only. Do not commit credentials to the repository.
