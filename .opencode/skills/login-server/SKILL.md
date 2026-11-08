---
name: login-server
description: >
  Connects to and runs commands on the homelab server 192.168.111.7 over SSH using
  password authentication only. Uses sshpass -e with the SSHPASS env var — never
  hardcode the password, never use key-based auth. Trigger when the user asks to
  ssh in, scp files to/from, or run any remote command on the server.
---

# login-server

## Who runs this

- `runesmith` — may run only the pinned `sshpass` transport with a whitelisted
  `kubectl`/`helm` read-only verb; `scp` is limited to the pinned form. Every other
  step below — `sudo` included — is handed to the human.
- `cluster-worker` — may use only the `ssh`/`sshpass` transport form its
  whitelist allows.
- `spec-writer` — cannot run this skill (shell denied); `runesmith` supplies the
  results in the brief instead.

## Steps

1. Ensure `SSHPASS` is set. If unset, `runesmith` asks the user to export it in
   their own shell from their password store (`export SSHPASS=<password>`, or a
   bare `export SSHPASS` if already set in the environment) and never to type the
   value into chat or a file. `cluster-worker` cannot ask — it refuses and
   escalates to `runesmith`.
2. Ensure `sshpass` is installed. If missing, `runesmith` asks the human to
   install it (`sudo pacman -S sshpass`) — no agent runs `sudo`. `cluster-worker`
   never installs packages.
3. Run the remote command with password auth forced and key auth disabled. An
   agent must use the unquoted, single-line form the permission block matches —
   copy it from `./.opencode/contracts/cluster-worker.md` § Transport. A human
   shell may quote the command:

   ```bash
   sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no -o IdentitiesOnly=yes runic@192.168.111.7 KUBECONFIG=/etc/rancher/k3s/k3s.yaml <whitelisted command>
   ```

   A human may instead quote the remote command.

4. To transfer files, use the same password-only flags in one line. An agent may
   only pull (remote source first); pushing a file to the node is the human's:

   ```bash
   sshpass -e scp -o PreferredAuthentications=password -o PubkeyAuthentication=no -o IdentitiesOnly=yes ./local-file runic@192.168.111.7:/remote/path
   sshpass -e scp -o PreferredAuthentications=password -o PubkeyAuthentication=no -o IdentitiesOnly=yes runic@192.168.111.7:/remote/path ./local-file
   ```

5. If the SSH daemon is down, `runesmith` asks the human to start it remotely —
   `echo "$SSHPASS" | sudo -S systemctl start sshd`. No agent runs `sudo` or
   `systemctl` on the node.

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
