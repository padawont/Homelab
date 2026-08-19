---
name: login-server
description: Log into and run commands on the homelab server at 192.168.111.16 via SSH. Use when the user asks to connect to, log into, or run remote commands on the server (ssh, scp, remote shell, remote command execution). Credentials come from the SSHPASS environment variable — never hardcode the password.
---

# login-server

SSH access to the homelab server.

## Connection details

| Field | Value |
|---|---|
| Host | `192.168.111.16` |
| User | `runic` |
| Auth | password, read from the `SSHPASS` env var |

## Running commands

Use `sshpass -e` so the password is read from the `SSHPASS` environment
variable instead of appearing in the process list or shell history:

```bash
sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 runic@192.168.111.16 '<command>'
```

## Copying files

`scp` uses the same auth:

```bash
sshpass -e scp ./local-file runic@192.168.111.16:/remote/path
sshpass -e scp runic@192.168.111.16:/remote/path ./local-file
```

## Credentials

- Read the password from the `SSHPASS` environment variable at runtime.
- If `SSHPASS` is unset, ask the user to export it (`export SSHPASS=runic`)
  or provide the value; never write the password into any file in the repo.
- If `sshpass` is missing, install it first (Arch: `sudo pacman -S sshpass`).
- If the SSH daemon is down on the server, start it with
  `echo '$PASSWORD' | sudo -S systemctl start sshd`.
