# Knowledge Section

Knowledge contains reference documentation about technologies, tools, and hardware used in the homelab. Notes must be comprehensive enough for AI agents to use as references for actual work.

This section is NOT for homelab-specific configuration — those go in `configs-and-adr/`. Knowledge entries may cross-reference configs and may lead to creating or updating config entries.

## Categorization

Knowledge is grouped by category, then topic folder:

```
knowledge/<category>/<topic>/
```

### Top-Level Categories

| Category | Description |
|---|---|
| `kubernetes/` | K8s architecture, resources, tools (Cilium, Helm, k3d, k9s, Rancher, Kiwix) |
| `operations/` | CI/CD, NixOS, dev environments (devbox, direnv, worktrunk), hardware CLI tools |
| `technology/` | Languages, frameworks, platforms (homelab-deployed only) |
| `hardware/` | Server specs, network topology, storage, SBCs |
| `design/` | Architecture patterns, documentation standards |

### Examples

```
knowledge/kubernetes/helm/
knowledge/operations/ci-cd/
knowledge/hardware/server-specs/
```

## Topic Folders

Each topic folder contains:

| File | Required | Purpose |
|---|---|---|
| `README.md` | Yes | Basic description and index |
| Atomic `.md` files | Yes (1+) | Focused notes, each covering one concept |
| `overview.md` | No | Optional summary — only if a single overview is explicitly requested |

**Atomic notes rule:** Break content into focused files rather than one comprehensive `overview.md`. Each atomic note covers exactly one concept. Use the README.md as an index linking to all notes in the folder.

### When to Split

Split when the topic has:
- Multiple distinct subtopics that can stand alone (each gets its own file)
- Concepts at different levels of detail (one file per concept)
- Independent reference value (reader should find one without reading all)

Do NOT split when the topic is genuinely a single concept — one focused file is fine.

## Frontmatter Requirements

All atomic `.md` files must include in frontmatter:
- `sources` — URLs of where this note is based on
- `last_audit_date` — date of the last accuracy review
- `related_configs` — paths to relevant configs in `configs-and-adr/` (optional)

## Cross-Referencing Configs

When a knowledge entry describes a tool or concept that has a corresponding configuration in the homelab:
1. Add the config path in the `related_configs` frontmatter field
2. Consider creating or updating the relevant config entry if one doesn't exist yet

For example, a knowledge note about Longhorn should link to `configs-and-adr/node-main/OS/` where the iSCSI and storage config lives.

## Weekly Generic Content Pruning

Generic tooling documentation (FastAPI, FastMCP, Pydantic-AI, pytest, type-checkers, opencode ecosystem) that belongs in the upstream `RunicEngines/knowledge-base` is flagged in `inventory/curator-report.md` and pruned on a recurring weekly schedule. This initial restructure flags but does not delete these files.

## Status Lifecycle

`draft` → `exploring` → `accepted` → `completed` / `superseded`
