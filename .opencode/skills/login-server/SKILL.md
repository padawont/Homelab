---
name: login-server
description: >
  Connects to and runs commands on the homelab server 192.168.111.7 over SSH.
  Trigger when the user asks to ssh in, scp files to/from, or run any remote
  command on the server. Uses sshpass -e with the SSHPASS env var — never
  hardcode the password.
---

# login-server

## Steps

1. Ensure `SSHPASS` is set. If unset, ask the user to export it
   (`export SSHPASS=runic`) or provide the value. Never put the password in a
   file.
2. Ensure `sshpass` is installed. If missing, install it (Arch:
   `sudo pacman -S sshpass`).
3. Run the remote command:

   ```bash
   sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 runic@192.168.111.7 '<command>'
   ```

4. To transfer files:

   ```bash
   sshpass -e scp ./local-file runic@192.168.111.7:/remote/path
   sshpass -e scp runic@192.168.111.7:/remote/path ./local-file
   ```

5. If the SSH daemon is down, start it remotely via sudo:
   `echo "$SSHPASS" | sudo -S systemctl start sshd`.

## Connection table

| Field | Value |
|---|---|
| Host | `192.168.111.7` |
| User | `runic` |
| Auth | password via `SSHPASS` env var |

## Rules

- Always use `sshpass -e` (reads `SSHPASS`) — never the `-p` flag with a plain
  password in the command line.
- `echo "$SSHPASS"` uses double quotes so the variable expands.
- Do not store or log the password anywhere in the repo.
- If password auth is rejected (node-main sets `PasswordAuthentication = false`),
  fall back to key-based ssh/scp (`ssh -i ~/.ssh/id_ed25519 runic@192.168.111.7 ...`).
