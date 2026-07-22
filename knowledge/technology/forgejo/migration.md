---
title: "Forgejo Migration"
status: draft
tags:
  - git
  - forge
  - migration
  - github
  - gitlab
  - gitea
sources:
  - url: "https://forgejo.org/docs/latest/user/first-repository/"
    title: "Forgejo — Your First Repository"
  - url: "https://forgejo.org/docs/latest/user/repo-mirror/"
    title: "Forgejo Repository Mirrors"
  - url: "https://forgejo.org/docs/v15.0/admin/upgrade/from-gitea/"
    title: "Migrating from Gitea to Forgejo"
  - url: "https://forgejo.org/docs/latest/contributor/repository-migration/"
    title: "Forgejo Repository Migration (Contributor Guide)"
last_audit_date: 2026-07-22
related_configs:
  - "configs-and-adr/node-main/kubernetes/forgejo.yaml"
---

# Forgejo Migration

Forgejo supports importing repositories from GitHub, GitLab, Gitea, and other Git hosting platforms. This can be done through the web UI or the command line.

## Import from GitHub

Via web UI:

1. Click "+" → "New Migration" → "GitHub"
2. Authorize Forgejo to access your GitHub account
3. Select repositories to migrate
4. Options: repository name, visibility, wiki, issues, pull requests, milestones, labels, releases

The migration includes:
- Git history (all branches and tags)
- Issues and pull requests (with comments)
- Wiki pages
- Labels and milestones
- Releases and attachments

## Import from GitLab

Same process as GitHub — select "GitLab" as the migration source. Requires a GitLab personal access token.

## Import from Gitea

Migrating from Gitea to Forgejo is a server-side upgrade:

1. Stop the Gitea service
2. Install Forgejo (binary or container) pointing to the existing Gitea data directory
3. Run database migrations (automatic on first start)
4. The data directory and database are compatible between Gitea and Forgejo

For the Docker image, replace the Gitea image with the Forgejo image and restart — Forgejo will automatically detect and migrate the existing data.

## Import via Repository Mirroring

For ongoing synchronization:

1. Create a repository mirror (Settings → Mirror Settings)
2. Configure the remote Git URL and credentials
3. Set the mirror interval (e.g., every 6 hours)
4. Forgejo will periodically fetch new commits, issues, and PRs

Mirrors support both push and pull directions.

## Import Raw Repositories

Forgejo can adopt existing bare Git directories on disk:

```bash
# Place bare repositories in the data directory
# Then adopt via admin UI: Site Administration → Repositories → Adopt
```

## What Gets Migrated

| Feature | GitHub | GitLab | Gitea |
|---|---|---|---|
| Git history (all branches/tags) | Yes | Yes | Yes |
| Issues + comments | Yes | Yes | Yes |
| Pull/Merge requests | Yes | Yes | Yes |
| Wiki | Yes | Yes | Yes |
| Labels | Yes | Yes | Yes |
| Milestones | Yes | Yes | Yes |
| Releases | Yes | Yes | Yes |
| LFS objects | Yes | Yes | Yes |
| CI/CD history | No | No | No |

## Homelab Notes

For the homelab, no migration from GitHub is planned initially. Forgejo will host new internal/test repositories first. Future migration can be done incrementally per repository as needed.
