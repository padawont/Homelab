# Knowledge

Reference documentation about software and tools used in the homelab. This is NOT for homelab-specific configs (those go in `configs/`).

## Categories

| Category | Description |
|---|---|
| `kubernetes/` | K8s architecture, resources, tools |
| `operations/` | CI/CD, NixOS infrastructure, deployment |
| `tooling/` | Developer tools, dev environments, version control |
| `technology/` | Languages, frameworks, platforms |
| `design/` | Architecture patterns, documentation standards |
| `hardware/` | Server specs, network topology, storage, SBCs |

## Rules

- Each topic is a kebab-case folder with `README.md` + atomic `.md` files
- All files must have `sources` and `last_audit_date` in frontmatter
- Knowledge may cross-reference configs via `related_configs` frontmatter
- Writing knowledge may lead to creating or updating config entries

See `AGENTS.md` for full rules.
