# Homelab Knowledge Base

This repository documents my homelab infrastructure, configuration, and knowledge. It serves as the primary reference for restoring the homelab in case of failure and for tracking changes over time.

## External File Loading

When working on a specific section, use your Read tool to load the corresponding AGENTS.md file on demand:

- @knowledge/AGENTS.md — categorization rules, topic folder structure, audit expectations

Do NOT preemptively load all references — load them on a need-to-know basis when relevant to the current task.

## Skills and AGENTS.md Boundary

Skills (`.opencode/skills/*/SKILL.md`) and section `AGENTS.md` files follow a strict separation:

- **Section `AGENTS.md` = WHAT** — defines rules, requirements, conventions, and structure for that section
- **Skills = HOW** — provide mechanical steps, validation logic, and scaffolding procedures

Skills must never duplicate content from AGENTS.md files. If a fact or rule exists in an AGENTS.md, the skill must reference it by path rather than restating it. This keeps the AGENTS.md files as the single source of truth for section-specific rules.

## Directory Structure

```
Homelab/
├── AGENTS.md          # This file — root instructions
├── README.md          # Project overview
├── opencode.json      # opencode config
├── devbox.json        # Devbox environment
├── .gitignore
│
├── configs/           # Software & infrastructure configuration
│   ├── nixos/         # NixOS machine configs
│   └── kubernetes/    # Kubernetes manifests (actual YAML)
│
├── knowledge/         # Reference documentation
│   ├── kubernetes/    # K8s knowledge (architecture, resources, tools)
│   ├── operations/    # CI/CD, infrastructure, deployment
│   ├── tooling/       # Developer tools, editors, build systems
│   ├── technology/    # Languages, frameworks, platforms
│   ├── design/        # Architecture patterns, documentation standards
│   ├── hardware/      # Server specs, network topology, storage, SBCs
│   └── AGENTS.md      # Knowledge section rules
│
└── changelog/         # Decision history (numbered entries)
```

## Directory Naming

All directory names and topic folder names must use kebab-case.

## Topic Folder Structure

Every topic folder must contain:
- `README.md` (mandatory) — basic description and index of contents
- `overview.md` (mandatory) — the crux of the content

Additional `.md` files are optional.

## Document Status Lifecycle

| Status | Used By | Meaning |
|---|---|---|
| `draft` | All | Initial creation, actively being written |
| `exploring` | Knowledge | Under investigation |
| `proposed` | Knowledge | Ready for review |
| `accepted` | Knowledge | Approved |
| `final` | Changelog only | Final decision recorded |
| `completed` | Knowledge | Fully resolved |
| `cancelled` | Changelog only | Abandoned |
| `superseded` | All | Replaced by newer content |

## Cross-Linking Convention

Use frontmatter fields to link between sections:
- `related_knowledge: []` — links to knowledge/ topics
- `related_configs: []` — links to configs/ paths
- `replaces: ""` / `replaced-by: ""` — in changelog entries (relative paths)

## GitHub Etiquettes

### Branch Naming

`{type}/{kebab-description}` — e.g. `feat/add-k3s-cluster`, `docs/update-hardware-inventory`

### Commit Messages

[Conventional Commits](https://www.conventionalcommits.org/) — `type(scope): description`

### PR Workflow

draft → CI passes → review → merge

### Merge Strategy

Squash merge (default); merge commits or rebase merge by exception

### Code Review

At least 1 approving review; resolve all threads before merge

### Responding to PR Reviews

When responding to PR review comments, always reply inline on the specific comment thread when possible rather than leaving a separate top-level comment. Inline replies keep context attached to the code or issue being discussed and make it easier for reviewers to follow resolutions.
