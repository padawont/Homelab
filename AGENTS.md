# Homelab Knowledge Base

This repository documents my homelab infrastructure, configuration, and knowledge. It serves as the primary reference for restoring the homelab in case of failure and for tracking changes over time.

Content flows through a 4-phase pipeline: **knowledge** → **configs-and-adr** → **deployment** → **status**.

Upstream org-wide knowledge base: [RunicEngines/knowledge-base](https://github.com/RunicEngines/knowledge-base)

## External File Loading

When working on a specific section, use your Read tool to load the corresponding AGENTS.md file on demand:

- @knowledge/AGENTS.md — categorization rules, topic folder structure, audit expectations
- @configs-and-adr/AGENTS.md — node-role structure, per-node config layout, ADR conventions
- @deployment/AGENTS.md — pipeline config format, procedure template, manifests boundary
- @status/AGENTS.md — current ADR/config registry, Mermaid diagram rules, deployment-phase updates

Do NOT preemptively load all references — load them on a need-to-know basis when relevant to the current task.

## Skills and AGENTS.md Boundary

Skills (`.opencode/skills/*/SKILL.md`) and section `AGENTS.md` files follow a strict separation:

- **Section `AGENTS.md` = WHAT** — defines rules, requirements, conventions, and structure for that section
- **Skills = HOW** — provide mechanical steps, validation logic, and scaffolding procedures

Skills must never duplicate content from AGENTS.md files. If a fact or rule exists in an AGENTS.md, the skill must reference it by path rather than restating it. This keeps the AGENTS.md files as the single source of truth for section-specific rules.

## Directory Structure

```
Homelab/
├── AGENTS.md              # This file — root instructions
├── README.md              # Project overview + pipeline explanation
├── opencode.json          # opencode config
├── devbox.json            # Devbox environment
├── .gitignore
│
├── knowledge/             # Phase 1: Reference documentation (homelab-relevant only)
│   ├── AGENTS.md          # Knowledge section rules
│   ├── README.md
│   ├── kubernetes/        # K8s architecture, resources, tools
│   ├── operations/        # CI/CD, NixOS, dev environments, hardware tooling
│   ├── technology/        # Languages, frameworks, platforms
│   ├── hardware/          # Server specs, network topology, storage, SBCs
│   └── design/            # Architecture patterns, documentation standards
│
├── configs-and-adr/       # Phase 2: Configurations + Architecture Decisions
│   ├── AGENTS.md          # Configs + ADR section rules
│   ├── README.md
│   ├── adr/               # Homelab-specific Architecture Decision Records (MADR format)
│   ├── node-main/         # node-1: K3s server, Longhorn storage, Rancher management
│   │   ├── kubernetes/    # Actual K8s manifests (deployments, services, configmaps, etc.)
│   │   └── OS/            # NixOS configs, network settings, installed packages
│   └── node-extra/        # Future worker nodes
│       ├── kubernetes/
│       └── OS/
│
├── deployment/            # Phase 3: Deployment pipelines, procedures, Helm values
│   ├── AGENTS.md          # Deployment section rules
│   ├── README.md
│   ├── pipelines/         # CI/CD configs (GitHub Actions workflows, ArgoCD app sets)
│   ├── procedures/        # Step-by-step deployment guides
│   └── manifests/         # Helm values, Kustomize overlays, ArgoCD application manifests
│
└── status/                # Phase 4: Live ADR and config registry
    ├── AGENTS.md          # Status section rules
    ├── README.md
    ├── current-adr/       # Live ADR state diagrams (Mermaid)
    │   ├── kubernetes.md  #   K8s-related ADR statuses and workloads
    │   └── nixos.md       #   NixOS-related ADR statuses
    ├── current-config/    # Deployed config inventory tables
    │   ├── kubernetes.md  #   K8s manifest registry
    │   └── nixos.md       #   NixOS config registry
    ├── hardware/          # CPU, memory, storage utilization snapshots
    └── versions/          # Software version inventory (K3s, Longhorn, Rancher, etc.)
```

## Issue Template Directive

All new issues MUST follow the section structure defined in [issue #1](https://github.com/padawont/Homelab/issues/1):

- Description
- Objectives
- Scope / Out of Scope
- Good Examples / Bad Examples
- Pipeline
- Definition of Done
- Validations

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
| `completed` | Knowledge | Fully resolved |
| `cancelled` | All | Abandoned |
| `superseded` | All | Replaced by newer content |

## Cross-Linking Convention

Use frontmatter fields to link between sections:
- `related_knowledge: []` — links to knowledge/ topics
- `related_configs: []` — links to configs-and-adr/ paths

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
