---
name: login-server
description: >
  Connects to and runs commands on the homelab server 192.168.111.7 over SSH using
  password authentication only. Uses sshpass -e with the SSHPASS env var — never
  hardcode the password, never use key-based auth. Trigger when the user asks to
  ssh in, scp files to/from, or run any remote command on the server.
---

# login-server

## Steps

1. Ensure `SSHPASS` is set. If unset, ask the user to export it
   (`export SSHPASS=runic`) or provide the value. Never put the password in a
   file.
2. Ensure `sshpass` is installed. If missing, install it (Arch:
   `sudo pacman -S sshpass`).
3. Run the remote command with password auth forced and key auth disabled:

   ```bash
   sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
     -o PreferredAuthentications=password -o PubkeyAuthentication=no \
     -o IdentitiesOnly=yes runic@192.168.111.7 '<command>'
   ```

4. To transfer files, use the same password-only flags:

   ```bash
   sshpass -e scp -o PreferredAuthentications=password -o PubkeyAuthentication=no \
     -o IdentitiesOnly=yes ./local-file runic@192.168.111.7:/remote/path
   sshpass -e scp -o PreferredAuthentications=password -o PubkeyAuthentication=no \
     -o IdentitiesOnly=yes runic@192.168.111.7:/remote/path ./local-file
   ```

5. If the SSH daemon is down, start it remotely via sudo:
   `echo "$SSHPASS" | sudo -S systemctl start sshd`.

## Connection table

| Field | Value |
|---|---|
| Host | `192.168.111.7` |
| User | `runic` |
| Auth | password via `SSHPASS` env var only (no key auth) |

## Rules

- Always use `sshpass -e` (reads `SSHPASS`) — never the `-p` flag with a plain
  password in the command line.
- Password authentication is the only permitted method. Never use key-based auth
  (`-i`, ssh-agent keys, `~/.ssh/id_ed25519`). Always force
  `PreferredAuthentications=password` and `PubkeyAuthentication=no`.
- If password auth is rejected, stop and report to the user — do not attempt any
  key-based fallback.
- `echo "$SSHPASS"` uses double quotes so the variable expands.
- Do not store or log the password anywhere in the repo.
