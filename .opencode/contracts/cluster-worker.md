# cluster-worker — command whitelist contract

Owned here so `./.opencode/agents/cluster-worker.md` stays inside the 250-line agent
cap. The agent's `permissions` block is the enforcement; this file is the contract it
enforces and the rule the executor plans against.

## Ten verbs

| Command | Purpose |
|---|---|
| `kubectl get` | read-only inspection of resources |
| `kubectl describe` | read-only inspection of resource detail/events |
| `kubectl logs` | read-only container log retrieval |
| `kubectl rollout undo` | revert a workload to its previous revision |
| `kubectl rollout restart` | restart a workload in place |
| `kubectl rollout status` | wait for a rollout to settle |
| `helm rollback` | revert a release to a prior revision |
| `helm history` | read-only release revision history |
| `helm status` | read-only release status |
| `helm list` | list releases |

`helm show` is explicitly excluded from Mode B: it fetches chart metadata and has no
plan-execution value. Read-only discovery is `runesmith`'s; anything that mutates is
the human's, before the plan is committed.

## Three forms

Every verb is whitelisted in three forms and all three are valid:

- the bare local form — `kubectl get …` / `helm status …`;
- the explicit-config form — `KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl get …`;
- the pinned `sshpass` transport form below.

The granted skills also accept `sudo k3s kubectl` for the root path, but `sudo` is
denied in the agent, so that third form is not yours to run.

## Prefix matching, not a grammar

The permission matcher is a prefix glob. The verb must come **immediately** after
`kubectl` or `helm` — `kubectl -n cv-sender get` is denied while
`kubectl get -n cv-sender` is allowed. Flags are permitted only as far as they stay
inside the verb above (e.g. `kubectl get pods -n cv-sender -o yaml`); anything that
changes the verb is out of scope. Anything appended that is not a verb flag —
redirection, a command separator, a quoted second command, or a
kubeconfig/context/server override — is denied by the hardening rules that follow
the allows.

## Single-command rule

One command per shell call. No redirection into files (`>`, `>>`, `tee`, `sed -i`,
heredocs), no chaining (`;`, `&&`, `||`, `|`), no quoting of the transported
command, and no `--kubeconfig`/`--context`/`--server`/`--kube-context` override.

## Transport

The node is remote: `ssh` and `sshpass` are permitted ONLY as transport, and the
transported verb is always the `KUBECONFIG` form — `sudo k3s kubectl` cannot be
wrapped. Copy the transport line exactly — unquoted, with the whitelisted host and
user — and substitute only `<whitelisted command>`:

```bash
sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o PreferredAuthentications=password -o PubkeyAuthentication=no -o IdentitiesOnly=yes runic@192.168.111.7 KUBECONFIG=/etc/rancher/k3s/k3s.yaml <whitelisted command>
```

You may not run any other remote command. Connection flags, auth method and
credential handling are owned by `./.opencode/skills/login-server/SKILL.md`.
