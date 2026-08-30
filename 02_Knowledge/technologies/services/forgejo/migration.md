---
title: "Migrating repositories to Forgejo"
status: accepted
author: "padawont"
date: 2026-08-23
tags: [forgejo, migration, github, gitea, gitlab]
sources:
  - url: "https://forgejo.org/docs/latest/user/repo-mirror/"
    title: "Forgejo repository mirrors"
  - url: "https://forgejo.org/docs/latest/contributor/repository-migration/"
    title: "Forgejo repository migration internals"
last_audit_date: 2026-08-25
related_docs:
  - "./02_Knowledge/technologies/services/forgejo/overview.md"
  - "./02_Knowledge/technologies/services/forgejo/operations.md"
  - "./02_Knowledge/technologies/services/forgejo/security.md"
---

# Migrating repositories to Forgejo

## Overview

Repositories can be brought into Forgejo either as a **one-shot migration** (a
copy of the code plus issues, PRs, and releases) or as a **mirror** (kept in
sync with the source). One-shot migrations and pull mirrors start from the web
UI's migration flow; push mirrors are configured per-repository. Migrations
and mirrors work with GitHub, Gitea, GitLab, Gogs, and plain URLs. Migration
is how a homelab
instance adopts an existing GitHub/Gitea history instead of starting from an
empty repo.

## Details

### One-shot migration

- Go to **Create → New Migration** and pick the source:
  GitHub, Gitea, GitLab, Gogs, or a generic git URL.
- Authenticate with a token (see `./02_Knowledge/technologies/services/forgejo/security.md`
  for fine-grained token scopes) — for GitHub, docs recommend a fine-grained
  personal access token with Content read.
- Choose what to bring over: repository itself, issues, pull requests, releases,
  milestones, labels, wiki. PR/issue comments are filtered according to the
  selected migration options.
- Migration runs server-side; for large or LFS-heavy repositories the `[git]`
  timeout settings (config cheat sheet) may need raising.

### Mirrors (continuous sync)

- A **pull mirror** re-fetches the source repository on a schedule
  (default `[mirror]` interval), keeping code, branches, and tags in sync.
- A **push mirror** pushes a Forgejo repo to a remote (e.g. GitHub) — by
  default it uses `git push --mirror` (all branches and tags); an optional
  branch filter restricts which branches are pushed. This is useful when
  Forgejo is canonical but an external copy is still published.
- Pull mirroring is chosen at repository creation (New Migration + the 'This
  repository will be a mirror' checkbox); push mirrors are set in **Settings →
  Repository → Mirror Settings**.
- A repository cannot be converted into a pull mirror after creation, and a
  push mirror force-pushes — it overwrites any changes on the remote.

### Practical migration checklist

- **Tokens first**: generate a scoped token on the source and a Forgejo access
  token for API/CLI work afterwards.
- **LFS / large files**: verify Git LFS content transfers; LFS objects are not
  mirrored over SSH push mirrors. If the source blocks it, clone + push the
  LFS objects manually.
- **Wiki and packages**: not every source migrates these cleanly — move them
  separately (export/import) if needed.
- **Releases and tags**: confirm tags arrive; a re-tag can be done from a local
  clone if the migration missed some.
- **Old URLs**: GitHub mirrors may be kept alive; or add DNS/web redirects so
  existing links still resolve.
- **Users and orgs**: repo-level migrations bring author names/commits as-is;
  account/org structure is recreated on Forgejo manually.

### Upgrade-path note

Forgejo also documents upgrades **from Gitea** (up to v1.22 included) as a
two-step path: any Gitea ≤ v1.22.x → Forgejo v10.0.x, then v10.0.x → any newer
Forgejo (e.g. v16). This is an instance upgrade, not a repo migration — see the
upgrade guide's from-Gitea section and `./02_Knowledge/technologies/services/forgejo/operations.md`.

## Sources / Further Reading

- Repository mirrors (pull/push): https://forgejo.org/docs/latest/user/repo-mirror/
- Migration internals (service layout, comment filtering): https://forgejo.org/docs/latest/contributor/repository-migration/
- Overview: `./02_Knowledge/technologies/services/forgejo/overview.md`
- Access tokens: `./02_Knowledge/technologies/services/forgejo/security.md`
