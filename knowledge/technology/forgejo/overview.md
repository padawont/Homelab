---
title: "Forgejo Overview"
status: draft
tags:
  - git
  - forge
  - self-hosted
  - ci-cd
  - codeberg
sources:
  - url: "https://forgejo.org"
    title: "Forgejo Official Site"
  - url: "https://forgejo.org/docs/latest/"
    title: "Forgejo v16.0 Documentation"
  - url: "https://codeberg.org/forgejo/forgejo"
    title: "Forgejo Source Code"
  - url: "https://forgejo.org/compare/"
    title: "Forgejo vs Other Forges"
  - url: "https://codeberg.org/forgejo/governance"
    title: "Forgejo Governance"
last_audit_date: 2026-07-22
related_configs:
  - "configs-and-adr/node-main/kubernetes/forgejo.yaml"
  - "configs-and-adr/node-main/OS/forgejo.nix"
---

# Forgejo Overview

Forgejo is a self-hosted lightweight software forge for Git hosting, CI/CD, package registries, issue tracking, and code review. It is a community-governed fork of Gitea that was created in late 2022 after the Gitea project was taken over by a for-profit entity.

## Governance

Forgejo is governed by Codeberg e.V., a democratic non-profit organization registered in Germany. This governance model ensures:

- Forgejo will always be 100% Free and Open Source Software
- Decision-making is community-driven, not corporate-controlled
- The project exclusively uses Free Software for its own development

The governance structure is documented at [codeberg.org/forgejo/governance](https://codeberg.org/forgejo/governance).

## Key Features

- **Git hosting** — Repository management with branches, tags, forks, and mirrors
- **Forgejo Actions** — GitHub Actions-compatible CI/CD with reusable workflows
- **Package registries** — OCI container registry (Docker/OCI), npm, PyPI, Maven, Cargo, and 20+ others
- **Issue tracking** — Issues, pull requests, labels, milestones, projects (Kanban)
- **Code review** — Pull request workflows with inline comments, approval, merge strategies
- **Wiki** — Built-in wiki per repository
- **Federation** — ActivityPub-based federation between Forgejo instances (under development)
- **OAuth2 provider** — Can act as an OAuth2 identity provider
- **API** — REST API for programmatic access
- **Webhooks** — Outgoing webhooks for integration with external services
- **SSH** — Built-in SSH server or system SSH

## Architecture

Forgejo is a single Go binary with minimal dependencies:

- **Language**: Go
- **Database**: SQLite (default), PostgreSQL, or MySQL/MariaDB
- **Storage**: Local filesystem, S3-compatible object storage
- **Frontend**: Web UI with dark/light/auto themes and accessibility options
- **SSH**: Built-in SSH server or delegation to system sshd

### Resource Profile

Forgejo is designed to run on low-resource hardware:

- **Minimum RAM**: 512MB — 1GB for single-user
- **Storage**: ~500MB for the binary + database; repository storage depends on usage
- **CPU**: Single core sufficient for small teams

## Versioning

Forgejo publishes a stable release every three months and a Long Term Support (LTS) release every year. Patch releases address bugs and security vulnerabilities. The current stable series is v16 (as of July 2026).

## Deployment Options

- Docker/Podman container
- Binary download (Linux, macOS, Windows)
- NixOS module
- Kubernetes (raw manifests or Helm)
- Third-party packaging (see [Delightful Forgejo](https://codeberg.org/forgejo-contrib/delightful-forgejo))

## Homelab Deployment

Forgejo is deployed on node-1 in the homelab K3s cluster as a K8s workload:
- Image: `codeberg.org/forgejo/forgejo:16`
- Database: existing in-cluster Postgres
- Storage: 10Gi Longhorn PVC for `/data`
- Ingress: `git.homelab.internal` with TLS
