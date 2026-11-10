---
title: "FileBrowser Quantum — sharing and permissions"
status: draft
author: "padawont"
date: 2026-11-08
tags: [filebrowser, filebrowser-quantum, permissions, sharing, access-control, webdav]
sources:
  - url: "https://filebrowserquantum.com/en/docs/features/user-permissions/"
    title: "User Permissions"
  - url: "https://filebrowserquantum.com/en/docs/configuration/users/"
    title: "User Management"
  - url: "https://filebrowserquantum.com/en/docs/access-control/access-control-overview/"
    title: "Access Control Overview"
  - url: "https://filebrowserquantum.com/en/docs/access-control/rules/"
    title: "Access Rules"
  - url: "https://filebrowserquantum.com/en/docs/shares/options/"
    title: "Share Common Options"
  - url: "https://filebrowserquantum.com/en/docs/shares/normal-shares/"
    title: "Normal Shares"
  - url: "https://filebrowserquantum.com/en/docs/shares/upload-shares/"
    title: "Upload Shares"
  - url: "https://filebrowserquantum.com/en/docs/features/webdav/"
    title: "WebDAV"
  - url: "https://filebrowserquantum.com/en/docs/reference/api/"
    title: "API Reference"
  - url: "https://filebrowserquantum.com/en/docs/changelog/stable/"
    title: "Stable changelog (v2.0.2-stable)"
last_audit_date: 2026-11-10
related_docs:
  - "./02_Knowledge/technologies/services/filebrowser-quantum/overview.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/authentication.md"
  - "./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md"
---

# FileBrowser Quantum — sharing and permissions

## Overview

Verified against **FileBrowser Quantum v2.0.2-stable** (released 2026-10-23); docs read
2026-11-08. Since v2.0.0 authorization is layered: global account capabilities, per-source
file permissions on each user scope, and optional path-level access rules. Share links and
API tokens are separate grants layered on top. This differs from classic Filebrowser,
where file-operation permissions were global checkboxes. Quantum's rules differ entirely,
do not carry over from the legacy project, and must be recreated.

## Details

### Users and groups

- Users are created in **User Management** (UI), `user set` (CLI), or `PATCH /api/users/{username}`; frontend-facing APIs address users by username, not numeric id.
- A **scope** is a source plus a path inside it (`/`, `/subfolder`, `/users/john`). A user only sees sources in their scopes, and only the subtree of each scope path.
- `defaultUserScope` sets the path *inside* a source where each user's `<username>` directory is created: source `path: /home/users` plus `defaultUserScope: /` yields `/home/users/<username>`, and the directory is created. Which sources new users are granted is governed by `defaultEnabled` (`./02_Knowledge/technologies/services/filebrowser-quantum/storage-and-sources.md`).
- **Groups** are supplied by LDAP or OIDC, or created via the API (see `/swagger/`); manual group management is not yet in the UI.
- Access rules can target a group, which is how IdP group membership becomes folder access.
- Admins get full file operations on every source and are exempt from enforced permission caps.

### Permission flags

| Layer | Flag | Grants |
|---|---|---|
| Global | `admin` | Full system, user management, configuration |
| Global | `api` | Create API tokens, use the REST API and Swagger |
| Global | `share` | Create and manage share links |
| Global | `realtime` | SSE/live update connections |
| Per source | `view` | Browse, list, properties, preview; WebDAV `PROPFIND` |
| Per source | `download` | Read bytes, download files/archives, copy source; WebDAV `GET` |
| Per source | `modify` | Edit, overwrite, rename, move |
| Per source | `create` | Create files/folders, upload, copy into the source |
| Per source | `delete` | Delete files and folders |

- Built-in per-source defaults: `view` and `download` true; `modify`, `create`, `delete` false.
- Defaults apply only to new scopes and auto-provisioned users; changing a default does not rewrite existing users.
- The **Enforce** toggle in Access management overwrites the flag for all non-admin users and blocks per-user overrides.
- `view` and `download` are deliberately separate: a user can preview in the browser without being able to save bytes.
- Path allow rules do not imply `create`/`modify`/`delete`; those must be granted on the scope row.

### Path scoping and access rules

- Rules are per user or group, per source, and per directory; types are **allow**, **deny**, and **deny-all**.
- Evaluation: exact-path rules first, then walk parents toward the root; if nothing matches, follow the source default.
- Default is allow unless the source sets `denyByDefault: true`, which leaves the source visible but blocks all files until explicit allows exist.
- More specific paths override broader ones, and an allow overrides a deny when both apply.
- In v2.0.x rule paths are matched case-sensitively; v2.1.0+ changes this to case-insensitive.
- Rules gate which paths are reachable; per-source permissions gate which actions succeed. Both must pass.
- Rules are stored against the source's configured `path`, so changing that path orphans them.
- Rules on a share are evaluated against the user who created the share.

### Share links

- Requires the global `share` permission; created from the Share action on a file or folder, yielding `/public/share/{hash}`.
- **Normal shares** allow browsing, viewing, and downloading; optional `allow create`, `allow modify`, `allow delete` (only when the source is not read-only).
- Normal-share controls include disable download, disable file viewer, downloads limit, max bandwidth, hidden files, thumbnails, and OnlyOffice viewing.
- **Upload shares** accept uploads only: no browsing, viewing, downloading, or directory visibility. They are suited to collecting submissions privately.
- Common options: duration in minutes/hours/days (blank = permanent) and an optional password that also applies to authenticated users.
- Expired shares become inaccessible and are deleted at startup unless **Keep after expiration** is set, which preserves them for audit or extension.
- **Disable anonymous access** restricts a share to authenticated users, who must still have access to the share's source.
- **Only share to certain users** takes a comma-separated username list and makes the link user-only.
- Upload shares may allow replacements; they otherwise expose only an upload form and progress.

### API tokens

- Creating tokens requires `api` or `admin`; tokens are managed under Settings → API Management / API Tokens with a chosen expiration.
- Tokens inherit the owner's per-source permissions. Customized tokens can carry permission or file caps; minimal (uncustomized) tokens inherit the owner's permissions in full.
- The v2.0.2 release fixed a gap where customized tokens with no global flags could exceed stored permission caps.
- Standard `/api/*` routes authenticate by `filebrowser_quantum_jwt` cookie, `&auth=<token>`, or `Authorization: Bearer <token>`.
- Public `/public/api/*` routes are share-scoped and hash-authenticated, not user tokens.
- Interactive API docs live at `/swagger/` (requires API permission); the UI's own Swagger token lasts two hours.
- API routes cover users, resources, shares, settings, access rules, events, and search.

### WebDAV

- Enabled by default at `/dav/<source-name>/`; clients use Basic Auth where the password is a **full, uncustomized** API token. The username is ignored.
- Permission mapping: `PROPFIND`/`OPTIONS` need `view`; `GET`/`HEAD` need `download`; `MKCOL` needs `create`; `PUT` needs `modify` (and `create` when the path is new); `DELETE` needs `delete`; `COPY` needs `download` + `create`; `MOVE` needs `modify`.
- Unhandled methods such as `LOCK` and `PROPPATCH` are denied.
- Access rules still apply after the source is resolved, so a granted permission does not bypass a path deny.
- A read-only mount therefore needs `view` + `download`; a full sync client needs the five per-source flags as needed — typically all five.

## Sources / Further Reading

- User permissions: https://filebrowserquantum.com/en/docs/features/user-permissions/
- Access control overview and rules: https://filebrowserquantum.com/en/docs/access-control/access-control-overview/
- Share options, normal shares, upload shares: https://filebrowserquantum.com/en/docs/shares/options/
- WebDAV permission matrix: https://filebrowserquantum.com/en/docs/features/webdav/
- API routes and authentication: https://filebrowserquantum.com/en/docs/reference/api/
