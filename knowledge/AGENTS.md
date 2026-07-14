# Knowledge Section

Knowledge contains the technical reference documentation for the homelab infrastructure. Notes must be comprehensive enough for AI agents to use as references for actual work.

## Categorization

Knowledge is grouped by category, then topic folder:

```
knowledge/<category>/<topic>/
```

### Top-Level Categories

| Category | Description |
|---|---|
| `kubernetes/` | K8s architecture, resources, tools (Cilium, Helm, k3d, k9s, Rancher) |
| `operations/` | Deployment, CI/CD, NixOS infrastructure |
| `tooling/` | Developer tools, dev environments, version control |
| `technology/` | Languages, frameworks, platforms |
| `design/` | Architecture patterns, documentation standards |
| `hardware/` | Server specs, network topology, storage, SBCs |

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

## Status Lifecycle

`draft` → `exploring` → `accepted` → `completed` / `superseded`
