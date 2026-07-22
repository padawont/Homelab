# Forgejo

Forgejo is a self-hosted lightweight software forge — a community-governed fork of Gitea under Codeberg e.V. It provides Git hosting, Forgejo Actions (GitHub Actions-compatible CI/CD), built-in OCI container and package registries, issue tracking, code review, and wiki.

Documentation for the homelab Forgejo deployment at `configs-and-adr/node-main/kubernetes/forgejo.yaml`.

## Files

- [overview.md](./overview.md) — Project history, community governance, key features, architecture
- [installation.md](./installation.md) — Docker Compose, binary install, NixOS, K8s deployment
- [configuration.md](./configuration.md) — app.ini, Postgres/SQLite, reverse proxy, SSH, systemd
- [forgejo-actions.md](./forgejo-actions.md) — Workflow syntax, runner registration, labels, Docker-in-Docker, GitHub Actions compatibility
- [registries.md](./registries.md) — OCI container registry, package registries (npm, PyPI, Maven, Cargo)
- [migration.md](./migration.md) — Importing from GitHub, GitLab, Gitea
- [comparison.md](./comparison.md) — Feature matrix: Forgejo vs Gitea vs GitHub vs GitLab vs Gogs

## Related Configs

- [forgejo.yaml](../../../configs-and-adr/node-main/kubernetes/forgejo.yaml) — K8s manifest
- [forgejo.nix](../../../configs-and-adr/node-main/OS/forgejo.nix) — NixOS config
- [deploy-forgejo.md](../../../deployment/procedures/deploy-forgejo.md) — Deployment procedure
