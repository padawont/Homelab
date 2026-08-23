# Plan: Knowledge #307 — Forgejo reference notes

Status: executing · Issue: https://github.com/RunicEngines/knowledge-base/issues/307
Epic: Self-hosted Git hosting — Forgejo (GitHub alternative) (#306)

## Context

Forgejo is Codeberg's soft-fork of Gitea — a lightweight, self-hosted Git forge
(repos, issues, PRs, packages, Actions). Current docs are v16.0 (LTS v15.0.7).
The epic's Research sub-issue (#308) compares Forgejo vs Gitea/GitLab/Gogs; this
Knowledge issue produces the foundation notes. Forgejo is NOT deployed yet — the
ADR/Implementation stages are follow-ups — so all config blocks must be labeled
`Example — abstract`, never "real running config".

## Deliverable — file tree

```
02_Knowledge/technologies/services/forgejo/     (folder is new — services/ currently empty)
├── overview.md          # what Forgejo is, why self-host, architecture
├── install-config.md    # k3s deploy (Helm/manifests), Traefik ingress, Longhorn PVC, config
├── operations.md        # backup/restore, upgrades
├── migration.md         # GitHub / Gitea / GitLab migration
├── security.md          # SSH keys, tokens, 2FA, instance hardening
└── ci-act-runners.md    # Forgejo Actions / forgejo-runner setup
```

6 notes, one concept each, 50–150 lines (frontmatter excluded), all
`status: draft`, author `padawont`.

## Per-note hydration

### K1 overview.md
- What Forgejo is: Codeberg's Gitea soft-fork (2022), MIT-licensed, self-hosted Git forge.
- Why self-host: privacy, no SaaS dependency, homelab-scale footprint (single Go binary + small DB).
- Feature surface: repos, issues, PRs, wiki, package registry, Forgejo Actions (GitHub-Actions-compatible), webhooks, repo mirroring, OAuth2 provider.
- Architecture: web UI + git over HTTP/SSH; DB backends (SQLite / PostgreSQL / MySQL); file storage (local dir / Longhorn PVC); Forgejo Runner for CI; reverse proxy (Traefik) in front; v16 current, v15 LTS.
- Homelab placement: namespace `forgejo`, host `git.homelab.local`, service port 3000.
- Cross-links → sibling notes; related docs: `kubernetes/concepts/ingress.md`, `services.md`, `storage.md`.
- Tags: `git, forgejo, gitea, self-hosted, code-hosting`

### K2 install-config.md
- Deploy options: Docker, Helm chart, binary, distro packages; for k3s → Helm chart or raw manifests.
- Manifests (all `Example — abstract`): `Deployment` (image `codeberg.org/forgejo/forgejo`), `Service` (port 3000 → `forgejo-http`), `PersistentVolumeClaim` (Longhorn storageClass), `Ingress` (Traefik, `git.homelab.local`, matches the example in `ingress.md`).
- Config: `app.ini` key sections (`[server] DOMAIN/ROOT_URL`, `[database]`, `[service]`, `[actions]`, `[security] SECRET_KEY`) via config map / env / init.
- DB: SQLite fine for single-node homelab; PostgreSQL for heavier use.
- HTTPS: Traefik TLS (cert-manager/LetsEncrypt if present); `ROOT_URL` must be `https://git.homelab.local`.
- Cross-links → `overview.md`, `operations.md`, `security.md`, `ingress.md`, `storage.md`.
- Tags: `forgejo, kubernetes, helm, ingress, storage, configuration`

### K3 operations.md
- Backup: `forgejo dump` (config + repos + DB, optional secret-key include) → scheduled via k8s `CronJob` to Longhorn volume; restore procedure (dump → extract → run).
- Upgrades: Forgejo release schedule (v16.0 current, v15.0 LTS), upgrade guide, verify release notes + `forgejo dump` before upgrading, supported version jumps.
- Day-to-day: logging config, k8s `logs -f deploy/forgejo -n forgejo`, health/liveness.
- Cross-links → `install-config.md`, `migration.md`.
- Tags: `forgejo, operations, backup, restore, upgrade`

### K4 migration.md
- Migrate via web UI (Settings → Migration) from GitHub / Gitea / GitLab / Gogs — repo, org, or user level; token auth.
- Two modes: one-shot import vs continuous mirroring (`repo-mirror`).
- Caveats: large repos/LFS, wiki/packages/releases may not transfer; DNS/redirect plan for old URLs.
- Cross-links → `overview.md`, `operations.md`, `security.md`.
- Tags: `forgejo, migration, github, gitea, gitlab`

### K5 security.md
- Auth: SSH keys, fine-grained access tokens (`token-scope` doc), 2FA (TOTP), OAuth2/OpenID.
- Instance hardening: `[service] DISABLE_REGISTRATION`, require sign-in, email verification, moderation/blocking.
- Secrets handling: `app.ini` `SECRET_KEY`, Actions secrets, never commit secrets.
- Transport: TLS via Traefik; expose only HTTPS; reference Forgejo threat-analysis doc.
- Cross-links → `install-config.md`, `overview.md`, `kubernetes/concepts/secrets.md`, `rbac.md`.
- Tags: `forgejo, security, authentication, ssh, tokens, 2fa`

### K6 ci-act-runners.md
- Forgejo Actions = GitHub-Actions-compatible CI, driven by `forgejo-runner` (ACT-based) registered per instance/org/repo with a registration token.
- Setup: install runner (binary/Docker), registration command + token, `config.yaml` (labels, cache, workspace), running in Docker on k3s.
- Workflow files: `.forgejo/workflows/*.yml` (YAML-compatible with GHA), `actions/checkout`, `setup-*` actions.
- Security: runner isolation, secrets, pull-request security (permissions), pin actions.
- Cross-links → `install-config.md`, `security.md`.
- Tags: `forgejo, ci, cd, actions, runners, docker`

## Sources to verify live (during writing / pkm-researcher)

| Note | URLs |
|---|---|
| K1 | https://forgejo.org/docs/latest/, https://codeberg.org/forgejo/forgejo |
| K2 | https://forgejo.org/docs/latest/admin/installation/, .../installation/docker/, .../admin/config-cheat-sheet/, .../admin/setup/storage/ |
| K3 | .../admin/upgrade/, .../admin/command-line/ (dump), .../admin/release-schedule/ |
| K4 | https://forgejo.org/docs/latest/contributor/repository-migration/, .../user/repo-mirror/ |
| K5 | .../user/authentication/token-scope/, .../contributor/threat-analysis/, .../admin/setup/authentication/ |
| K6 | .../admin/actions/, .../admin/actions/registration/, .../admin/actions/installation/docker/, .../admin/actions/security/, .../user/actions/ |

## Execution phases

1. Branch `knowledge/307-forgejo` from `main`.
2. Write notes in dependency order: overview → install-config → operations → migration → security → ci-act-runners. Copy template each time; set frontmatter; label examples `Example — abstract`; cross-link as you go.
3. Validate with loop-validation: `pkm-researcher` → `pkm-editor` → `pkm-overview` → `pkm-compliance`, looping until clean (7 consecutive clean loops or user stop).
4. Commit per note (atomic), Conventional Commits: `knowledge(307): add Forgejo overview note`, etc.
5. PR to `padawont/Homelab` (body: Summary, Changes, Testing Notes, ADR 0002 checklist) closing #307; squash merge.
6. Post-merge: mark notes `accepted` (reviewed) and close #307.

## Acceptance criteria (from #307)

- [x] 6 atomic notes, one concept per file, each 50–150 lines
- [x] Every planned note enumerated in In Scope + Topic Hierarchy (in issue)
- [x] Valid knowledge frontmatter; `last_audit_date` set
- [x] Every `sources[]` URL live (via Researcher)
- [x] Abstract examples labeled clearly — no fake "real" configs since not deployed
- [x] Passes knowledge review (pkm-researcher → pkm-editor)

## Key risk

Forgejo isn't running yet, so `install-config.md` and `ci-act-runners.md` are
reference/abstract only — must not imply live configs.
