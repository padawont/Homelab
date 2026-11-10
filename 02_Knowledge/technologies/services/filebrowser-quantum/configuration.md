---
title: "FileBrowser Quantum — configuration model"
status: draft
author: "padawont"
date: 2026-11-08
tags: [filebrowser, filebrowser-quantum, configuration, yaml, self-hosted]
sources:
  - url: "https://filebrowserquantum.com/en/docs/configuration/configuration-overview/"
    title: "FileBrowser Quantum — Configuration Overview"
  - url: "https://filebrowserquantum.com/en/docs/configuration/server/"
    title: "FileBrowser Quantum — Server Settings"
  - url: "https://filebrowserquantum.com/en/docs/configuration/http/"
    title: "FileBrowser Quantum — HTTP Settings"
  - url: "https://filebrowserquantum.com/en/docs/getting-started/config/"
    title: "FileBrowser Quantum — Configuration Files (v2.0.0)"
  - url: "https://filebrowserquantum.com/en/docs/reference/cli/"
    title: "FileBrowser Quantum — CLI Commands"
  - url: "https://filebrowserquantum.com/en/docs/reference/environment-variables/"
    title: "FileBrowser Quantum — Environment Variables"
  - url: "https://filebrowserquantum.com/en/docs/reference/fullconfig/"
    title: "FileBrowser Quantum — Full Config Example"
last_audit_date: 2026-11-10
related_docs:
  - "./02_Knowledge/technologies/services/filebrowser-quantum/overview.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/installation.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/authentication.md"
---

# FileBrowser Quantum — configuration model

## Overview

Quantum (v2.x) is configured by one YAML file, `config.yaml`: a tree of top-level sections
(`http`, `server`, `auth`, `userDefaults`, `frontend`, `integrations`) read once at
startup. Verified against **v2.0.2-stable** (released 2026-10-23); docs read 2026-11-08.

> **Classic Filebrowser does not transfer.** Classic Filebrowser used CLI flags plus a
> BoltDB `database.db` store; Quantum v1.4.x–v1.5.x already shipped a `config.yaml`, which
> v2.0.0 restructured — HTTP keys moved from `server` to top-level `http` and deprecated
> flat formats were removed. Fork history: `./02_Knowledge/technologies/services/filebrowser-quantum/overview.md` § Lineage; older flag tutorials no longer apply.

## Details

### File discovery

The docs give one priority order for locating the file:

1. `-c` / `--config <path>` on the command line.
2. `FILEBROWSER_CONFIG` environment variable.
3. Default locations: `./config.yaml` in the working directory; in the official Docker
   image, the path and layout are in
   `./02_Knowledge/technologies/services/filebrowser-quantum/installation.md` § Ports, mounts, and paths.

- Image config path, the `/config` caveat, and the mount-a-directory rule live in the same
  section — `./02_Knowledge/technologies/services/filebrowser-quantum/installation.md` § Ports, mounts, and paths.
- With no file the server boots on built-in defaults, but `server.sources` is required to
  serve content, so a config-less instance browses nothing.
- Read at startup only; edits need a restart. To generate a starting `config.yaml`, see
  `./02_Knowledge/technologies/services/filebrowser-quantum/installation.md` § Standalone binary.
- Unknown keys are rejected (`userdefaults` vs `userDefaults`) and some fields are
  required (`server.sources`), so a bad file fails loudly instead of being ignored.
- The Configuration Overview page lists the same three sources in another order (flag,
  current directory, env var); the Getting Started page is the explicit priority
  statement followed above. Prefer `-c` in scripts to avoid the ambiguity.

### Section map

| Top-level key | Purpose |
|---|---|
| `http` | port, listen address, `baseURL`, Unix socket, TLS, external/internal URL, WebDAV, proxy-header trust, auth rate limiting |
| `server` | database, `cacheDir`, `sources`, logging, indexing, previews, file/dir permissions, archive cap |
| `auth` | admin username/password, auth methods (password, OIDC, LDAP, JWT, proxy, no-auth, passkey), TOTP secrets |
| `userDefaults` | defaults for new users: sidebar, listing, preview, fileViewer, search, ui, fileLoading, account |
| `frontend` | display name, sidebar links, CSS/themes, background colours |
| `integrations` | media (FFmpeg paths), office (OnlyOffice URL/secret) |

Sources are **nested** at `server.sources`, not top-level, and `server` no longer holds
port/`baseURL`/TLS — those moved to `http` in v2.0.0.

### Precedence

1. `-c` decides *which* file is loaded; it is the only config-selecting flag and there are
   no per-setting CLI flags, so flags never override individual values.
2. Values in `config.yaml` are the baseline.
3. Named `FILEBROWSER_*` variables override matching keys after the file is decoded — except the database path, which has its own order below
   (secrets such as `FILEBROWSER_ADMIN_PASSWORD`, OIDC client secret, JWT/TOTP keys);
   `FILEBROWSER_CONFIG` is the exception — it selects a path, not a value.
4. `${VAR}` / `$VAR` references inside YAML expand on the decoded tree; a scalar that is
   only one reference may be coerced to a boolean or number (`port: ${PORT}`).

Database path has its own documented order: `server.database.path` (config) →
`FILEBROWSER_DATABASE_PATH` (env) → built-in default (`./filebrowser.sqlite` standalone,
`/home/filebrowser/data/database.sqlite` in Docker). `FILEBROWSER_DATABASE` is v1-only.

### User defaults

`userDefaults` seeds the initial values for newly created users: `sidebar` (toggles, sticky, hide files), `listing` (view mode, hidden files, date format), `preview` (which file types preview), `fileViewer`, `search`,
`ui` (dark mode, theme, locale), `fileLoading` (upload/download chunking) and `account` (the global `admin`/`api`/`share`/`realtime` permissions, `lockPassword`, `disableSettings`, `loginMethod`). On first start
the values are copied into SQLite and only the fields you set stay locked in Settings → User management → User defaults; afterwards the database is authoritative, and config values do not overwrite existing users.

### Server and HTTP keys

`server`: `database.path` (plus one-time `migrateFrom` for a legacy BoltDB file),
`cacheDir` (default `tmp`; disk-backed, never tmpfs, writable by the container UID),
`sources[]`, `logging`, `filesystem.create{File,Directory}Permission`, preview/index
tuning (`disablePreviews`, `numImageProcessors`, `indexSqlConfig`), `maxArchiveSize` (GB,
default 20).

`http`: `port` (default 80), `listen` (default `0.0.0.0`), `baseURL` (default `/`,
normalized to leading+trailing slashes, required for a subpath), `socket` (Unix socket;
`port` is ignored when it is set, and TLS is rejected), `tlsCert` + `tlsKey` (both required for HTTPS,
not combinable with `socket`), `externalUrl`/`internalUrl`, `disableWebDAV`,
`trustProxyHeaders` (v2.0.0+, replaces v1's `trustedHeaders`), `disableRateLimit`.

### Example — abstract

```yaml
http:
  port: 80
  listen: "0.0.0.0"
  baseURL: "/"
server:
  database:
    path: "data/filebrowser.sqlite"
  cacheDir: "tmp"
  sources:
    - path: "/srv"
      config:
        defaultEnabled: true
auth:
  adminUsername: admin
  methods:
    password:
      enabled: true
userDefaults: {}
```

Values are illustrative; see the Full Config Example, or Settings → System & Admin →
Load Config in the web UI, for the exact keys of the running version.

## Sources / Further Reading

- Configuration Overview: https://filebrowserquantum.com/en/docs/configuration/configuration-overview/
- Server Settings: https://filebrowserquantum.com/en/docs/configuration/server/
- HTTP Settings: https://filebrowserquantum.com/en/docs/configuration/http/
- Configuration Files (v2.0.0): https://filebrowserquantum.com/en/docs/getting-started/config/
- CLI Commands: https://filebrowserquantum.com/en/docs/reference/cli/
- Environment Variables: https://filebrowserquantum.com/en/docs/reference/environment-variables/
- Full Config Example: https://filebrowserquantum.com/en/docs/reference/fullconfig/
