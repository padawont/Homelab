# Homelab Knowledge Base

This repository documents the structure, configuration, and knowledge for my homelab.

## Directory Structure

```
knowledgebase/
├── AGENTS.md          # This file — root rules
├── README.md          # Human overview
├── opencode.json      # Agent config
├── templates/         # Reusable starters per section
├── hardware/          # One folder per machine
├── infra/             # OS, containers, virtualization
├── network/           # Network topology and config
├── services/          # One folder per service
├── config/            # Config files and templates
├── backups/           # Strategy and procedures
├── knowledge/         # Technical reference notes
└── decisions/         # Software choices + rationale
```

## Naming

All directories and files use kebab-case.

## Topic Folder Structure

Each topic folder must contain:
- `README.md` (mandatory) — basic description and index
- `overview.md` (mandatory) — the crux of the content

Additional `.md` files are optional.

## Status Lifecycle

`draft` → `active` → `archived` / `superseded`

- **draft** — being written, not ready
- **active** — current and accurate
- **archived** — no longer relevant, kept for history
- **superseded** — replaced by newer content (must include `replaced-by` field)

## Machine Tagging

Use the `machine:` frontmatter field to scope docs to specific hardware.
When searching, filter by machine to see what applies to a given box.

## Cross-Linking Fields

| Field | Used In | Type |
|---|---|---|
| `related_services` | hardware, infra, network, config, backups | list of paths |
| `related_hardware` | services, infra, backups, decisions | list of paths |
| `sources` | knowledge, decisions, services | list of URLs |
| `references` | knowledge | list of URLs |
| `replaces` | decisions | single path |
| `replaced-by` | decisions | single path |

## Archived / Superseded Markers

When `status: archived`, add a comment block at the end of the doc:

```
ARCHIVED — This document is no longer current. Retained for historical reference only.
```

When `status: superseded`, add a comment block at the end with the path:

```
SUPERSEDED — Replaced by: <path>
```

The `replaced-by` frontmatter field provides the path.

## Change Management — Machine Workflow

When making significant changes to any homelab machine, follow this workflow:

1. **Read first** — Before making changes, read the relevant docs in `hardware/<machine>/`, `services/`, `infra/`, `network/`, and `config/`. Use the `machine:` frontmatter tag to find all docs scoped to that machine.

2. **Make the change** — Proceed with the actual work on the machine.

3. **Update the KB** — After the change, update all affected docs to reflect the new state. This includes:
   - `hardware/<machine>/overview.md` — storage layout, OS version, hardware specs
   - `services/<service>/overview.md` — new/deleted/updated services
   - `infra/` — OS config changes, kernel params, Docker config
   - `network/` — IP changes, new routes, VLAN changes
   - `config/` — new config file templates

4. **Significant changes** that always trigger an update:
   - Hardware addition/removal/replacement
   - OS upgrade or distro swap
   - New service deployment or service removal
   - Network topology or IP scheme changes
   - Storage layout changes (new disks, LVM, partition changes)
   - Major software architecture changes (e.g. migrating from Docker to Podman)

5. **Frontmatter** — When updating, increment or update the `date` field in frontmatter. If the machine's purpose changes, update `tags` and `status` accordingly.

6. **Cross-links** — Update `related_services` / `related_hardware` fields when relationships change.
