---
title: "FileBrowser Quantum — authentication"
status: draft
author: "padawont"
date: 2026-11-08
tags: [filebrowser, filebrowser-quantum, authentication, oidc, ldap, security]
sources:
  - url: "https://filebrowserquantum.com/en/docs/configuration/authentication/"
    title: "FileBrowser Quantum — Authentication"
  - url: "https://filebrowserquantum.com/en/docs/configuration/authentication/password/"
    title: "FileBrowser Quantum — Password Authentication"
  - url: "https://filebrowserquantum.com/en/docs/configuration/authentication/oidc/"
    title: "FileBrowser Quantum — OIDC Authentication"
  - url: "https://filebrowserquantum.com/en/docs/configuration/authentication/ldap/"
    title: "FileBrowser Quantum — LDAP Authentication"
  - url: "https://filebrowserquantum.com/en/docs/configuration/authentication/jwt/"
    title: "FileBrowser Quantum — JWT Authentication"
  - url: "https://filebrowserquantum.com/en/docs/configuration/authentication/proxy/"
    title: "FileBrowser Quantum — Proxy Authentication"
  - url: "https://filebrowserquantum.com/en/docs/configuration/authentication/noauth/"
    title: "FileBrowser Quantum — No Authentication"
  - url: "https://filebrowserquantum.com/en/docs/configuration/http/"
    title: "FileBrowser Quantum — HTTP Settings"
  - url: "https://filebrowserquantum.com/en/docs/getting-started/reverse-proxy/"
    title: "FileBrowser Quantum — Running behind a reverse proxy"
  - url: "https://filebrowserquantum.com/en/docs/configuration/users/"
    title: "FileBrowser Quantum — User Management"
  - url: "https://filebrowserquantum.com/en/docs/changelog/stable/"
    title: "FileBrowser Quantum — Stable changelog"
last_audit_date: 2026-11-10
related_docs:
  - "./02_Knowledge/technologies/services/filebrowser-quantum/overview.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/configuration.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/sharing-and-permissions.md"
  - "./05_Implementations/node-main/k3s/overview.md"
---

# FileBrowser Quantum — authentication

## Overview

Verified against FileBrowser Quantum **v2.0.2-stable** (released 2026-10-23); docs read 2026-11-08.

Quantum authenticates each request against one or more login methods under `auth.methods.*`,
then carries the result in a server-issued session cookie. Methods: password (with TOTP 2FA
or a passwordless passkey), OIDC, LDAP, externally signed JWT, reverse-proxy headers, and `noauth`.

Scope: method selection and minimum fields. Permissions and share links live in
`./02_Knowledge/technologies/services/filebrowser-quantum/sharing-and-permissions.md`; config
mechanics in `./02_Knowledge/technologies/services/filebrowser-quantum/configuration.md`.

## Details

### Selecting methods

- Each method has its own flag — `enabled` for most, a plain boolean for `noauth`; several can be active
  at once, and the login page offers whichever are enabled. OIDC alone auto-redirects to the provider.
- `auth.methods.noauth: true` disables every method and serves all requests as user ID 1;
  it overrides password, OIDC and proxy auth.
- Authentication is not authorization: a new user (signup, admin/CLI, first OIDC/LDAP/JWT/
  proxy login) gets only sources flagged `defaultEnabled`; a single-source config
  auto-enables it — grant semantics:
  `./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md`

Example — abstract:

```yaml
auth:
  methods:
    password: { enabled: true, minLength: 12, signup: false }
    oidc:     { enabled: false }   # requires an external identity provider
```

### Password, 2FA and passkeys

- `auth.methods.password` takes `minLength` (default 5) and `signup` (default false). In v2.0.2
  the bootstrap admin credentials sit at top-level `auth.adminUsername` / `auth.adminPassword`;
  v2.1 moves them under `auth.methods.password` and migrates the legacy keys.
- Passwords are stored in the server database; the hash algorithm is undocumented.
  Bootstrap admin creation (generated password, literal `admin`, forced first-login change)
  is in `./02_Knowledge/technologies/services/filebrowser-quantum/installation.md` § First
  run and admin creation.
- Forced change: the account carries `requirePasswordChange` until
  `POST /api/auth/password/change-required` succeeds, current password in `X-Password`.
- 2FA is TOTP, password users only (not OIDC/proxy); it needs `auth.totpSecret` (e.g.
  `openssl rand -base64 32`) to encrypt TOTP secrets. Changing that key locks out every
  enrolled user until an admin disables 2FA or a CLI reset clears it. `enforcedOtp: true`
  blocks password logins until 2FA is set up; codes refresh every 30 s, valid 2 min.
- Passkeys are passwordless WebAuthn credentials; 2FA enrolment is what lives under Profile → Security.
  The RP ID comes from `http.externalUrl` when set, else the request host. Since v2.0.2,
  adding/removing a passkey on an account that already has one requires the account password.

### External providers — minimum fields

- **OIDC**: `issuerUrl`, `clientId`, `clientSecret`. The callback is
  `<request-base>/api/auth/oidc/callback`, derived from the request, not `externalUrl`.
  Optional: `scopes`, `userIdentifier` (default `preferred_username`), `adminGroup`,
  `userGroups`, `groupsClaim` (default `groups`).
- **LDAP**: `server` (`ldap://` or `ldaps://`), `baseDN`, and a service bind `userDN` +
  `userPassword`; `userFilter` (`%s` = login) and optional `userIdentifier`. Quantum searches
  with the service account, then binds as the user; `ldaps://` is the encrypted form.
- **JWT**: shared `secret` plus accepted `algorithm` (default HS256); the token arrives in
  `header` (default `X-JWT-Assertion`) or `?jwt=`. `sub` and `exp` are required claims.
- **Proxy**: `header` naming the trusted username header (e.g. `X-Forwarded-User`). Quantum
  accepts that header without further proof, so the method is only sound when the app is
  unreachable except through the proxy. Group/role headers are v2.1.0+.

### Sessions, cookies and throttling

- A successful login issues a session token carried in the **HttpOnly** cookie
  `filebrowser_quantum_jwt` (HttpOnly added in v1.5.4); cookie `Secure`/`SameSite` are
  undocumented. Lifetime is `auth.tokenExpirationHours`; API tokens are separate. Renewal is
  client keep-alive — `X-Renew-Token` was removed in v2.0.0.
- Cookie scoping follows the request `Host`, or `X-Forwarded-Host` when
  `http.trustProxyHeaders: true`; a proxy that rewrites `Host` without header trust breaks
  login. HTTPS detection likewise comes from `X-Forwarded-Proto`.
- Auth throttling is built in, in-memory, per process (not YAML-tunable): 10 req/min, burst
  8, per IP and per username on login/OTP. Eight consecutive 401s for the same IP+username
  trigger a 15-minute lockout (HTTP 429, `Retry-After: 900`). Other tiers: signup/logout
  30/min, OIDC 60/min, authenticated routes 180/min.
- `http.disableRateLimit: true` removes the 429 throttling and failed-login lockout;
  throttling is also absent under `noauth`. Counters clear on restart, are not shared across
  replicas, and since v2.0.2 the client IP is the rightmost trusted `X-Forwarded-For` hop.

### Plain HTTP on a LAN

- With no TLS on the hop, the login POST and every later request — session cookie, JWT
  header, proxy username header — cross the network in cleartext; an observer on the LAN
  segment can capture the cookie and reuse the session until it expires.
- WebAuthn/passkeys need a secure context, so on a plain `http://` LAN origin (other than
  `localhost`) they do not work, leaving password + TOTP.
- Behind a TLS-terminating proxy Quantum only sees `https` with `trustProxyHeaders: true`;
  without it, OIDC `redirect_uri`s and WebAuthn RP IDs are built as `http://` and the
  provider or browser rejects them.
- With `trustProxyHeaders: true` while the app is directly reachable, clients can spoof
  `X-Forwarded-For`/`X-Forwarded-Proto`, weakening per-IP throttling, lockout and cookie
  scoping. Bind to `127.0.0.1` or a private network when trusting headers.
- Homelab context: no identity provider exists here, so OIDC and LDAP are available in the
  product but unused; password (+2FA/passkeys) is what this environment can use. Stated as
  current setup, not a recommendation.

## Sources / Further Reading

- Authentication overview: https://filebrowserquantum.com/en/docs/configuration/authentication/
- Password, 2FA, require-password-change: https://filebrowserquantum.com/en/docs/configuration/authentication/password/
- Method pages — OIDC, LDAP, JWT, proxy, noauth: https://filebrowserquantum.com/en/docs/configuration/authentication/
- HTTP settings, rate limiting, `trustProxyHeaders`: https://filebrowserquantum.com/en/docs/configuration/http/
- Reverse proxy guide (cookies, headers, OIDC callbacks): https://filebrowserquantum.com/en/docs/getting-started/reverse-proxy/
- User management (`loginMethod`, 2FA reset): https://filebrowserquantum.com/en/docs/configuration/users/
- Changelog — passkeys (v1.4.0, v2.0.2), HttpOnly cookie (v1.5.4): https://filebrowserquantum.com/en/docs/changelog/stable/
