---
title: "Securing a Forgejo instance"
status: accepted
author: "padawont"
date: 2026-08-23
tags: [forgejo, security, authentication, ssh, tokens, 2fa]
sources:
  - url: "https://forgejo.org/docs/latest/admin/advanced/moderation/"
    title: "Forgejo moderation tools"
  - url: "https://forgejo.org/docs/latest/admin/advanced/oauth2-provider/"
    title: "Forgejo OAuth2 provider"
  - url: "https://forgejo.org/docs/latest/admin/config-cheat-sheet/"
    title: "Forgejo configuration cheat sheet"
  - url: "https://forgejo.org/docs/latest/admin/installation/docker/"
    title: "Forgejo installation with Docker"
  - url: "https://forgejo.org/docs/latest/admin/setup/authentication/"
    title: "Forgejo authentication setup"
  - url: "https://forgejo.org/docs/latest/contributor/threat-analysis/"
    title: "Forgejo threat analysis"
  - url: "https://forgejo.org/docs/latest/user/authentication/token-scope/"
    title: "Forgejo access token scopes"
last_audit_date: 2026-08-23
related_docs:
  - "./02_Knowledge/technologies/services/forgejo/overview.md"
  - "./02_Knowledge/technologies/services/forgejo/install-config.md"
  - "./02_Knowledge/technologies/services/forgejo/ci-act-runners.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/secrets.md"
  - "./02_Knowledge/technologies/kubernetes/concepts/rbac.md"
---

# Securing a Forgejo instance

## Overview

A homelab Forgejo instance should be locked down at three levels: transport
(HTTPS only via Traefik), authentication (SSH keys, 2FA, scoped tokens), and
instance policy (no open registration, restricted sign-in, moderation). Forgejo
provides fine-grained access tokens and instance settings for exactly this, and
its threat-analysis documentation covers the remaining risk surface.

## Details

### Transport

- Expose the instance only through HTTPS. Traefik terminates TLS on the
  `forgejo-ingress` (`./02_Knowledge/technologies/services/forgejo/install-config.md`).
- Keep `ROOT_URL` on `https://` so redirects and OAuth callbacks never downgrade.
- Do not port-forward raw ports 3000/22 to the public network unless the
  exposure is intentional.

### Authentication

- **Local accounts**: passwords plus optional 2FA. Enforce 2FA for
  admins; consider it for all users.
- **SSH keys**: added by users under their account settings; git-over-SSH
  authenticates with them. The rootless container image embeds the SSH server.
- **Access tokens** (API/CLI): Forgejo tokens are scoped per API domain with
  `read:`/`write:` levels — `read:repository`, `write:issue`, `read:user`, etc.
  A scope is required even for public repositories. Choose the most restrictive
  token that works:
  - *All (public, private, limited)* — broadest.
  - *Public only* — restricted to public resources.
  - *Specific repositories* — limited to chosen repos and only
    `read/write:repository` + `read/write:issue` scopes; no admin powers.
  - **Least privilege**: a compromised scoped token only affects its own scope.
- **External auth**: OAuth2 / OpenID Connect providers can replace or supplement
  local logins (see the OAuth2 provider page).

### Instance policy (`app.ini`)

| Setting | Effect |
|---|---|
| `[service] DISABLE_REGISTRATION=true` | No public sign-ups — create accounts as admin |
| `[service] REQUIRE_SIGNIN_VIEW=true` | Hide public views behind login |
| `[service] EMAIL_DOMAIN_ALLOWLIST` | Restrict sign-ups to specific domains |
| `[security] INSTALL_LOCK=true` | Prevent re-running the installer |
| `[security] SECRET_KEY` | Random instance secret set on first install |

### Secrets

- Store `SECRET_KEY`, DB passwords, and runner tokens in a k8s Secret
  (`./02_Knowledge/technologies/kubernetes/concepts/secrets.md`), never in a
  committed manifest.
- Store Actions secrets scoped per repository/org rather than globally (see
  the CI note `./02_Knowledge/technologies/services/forgejo/ci-act-runners.md`).
- Rotate tokens after any suspected leak; token scope limits blast radius.

### Moderation and monitoring

- Block users and suspend/delete accounts or repositories via the moderation
  tools if the instance
  ever opens up beyond single-owner use.
- Review the threat-analysis documentation for known risks (e.g. remote login
  propagation) before exposing the instance
  beyond a trusted LAN.
- Access control inside the cluster follows Kubernetes RBAC
  (`./02_Knowledge/technologies/kubernetes/concepts/rbac.md`).

## Sources / Further Reading

- Access token scopes: https://forgejo.org/docs/latest/user/authentication/token-scope/
- Authentication setup (OAuth2/OpenID, local): https://forgejo.org/docs/latest/admin/setup/authentication/
- Moderation tools: https://forgejo.org/docs/latest/admin/advanced/moderation/
- Threat analysis: https://forgejo.org/docs/latest/contributor/threat-analysis/
- Install/config: `./02_Knowledge/technologies/services/forgejo/install-config.md`
