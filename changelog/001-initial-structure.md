---
changelog: 001
title: Initial Homelab Repository Structure
status: final
date: 2026-07-14
---

# CHANGELOG 001: Initial Homelab Repository Structure

## Context

Created a homelab documentation repository to serve as the single source of truth for infrastructure configuration, knowledge reference, and change tracking.

## Structure

```
Homelab/
├── configs/           # Software & infrastructure configs
│   ├── nixos/
│   └── kubernetes/
├── knowledge/         # Reference documentation
│   ├── kubernetes/
│   ├── operations/
│   ├── tooling/
│   ├── technology/
│   ├── design/
│   └── hardware/
│       ├── server-specs/
│       ├── network-topology/
│       ├── storage/
│       └── sbc/
├── changelog/         # Decision history
├── .opencode/         # opencode agents and skills
├── AGENTS.md          # Root rules and conventions
└── README.md
```

## Imported Content

- **Knowledge:** Kubernetes, operations, tooling, technology, and design docs imported from `RunicEngines/knowledge-base`
- **History:** ADRs, proposals, and research from knowledge-base preserved in `changelog/` as reference
- **Conventions:** AGENTS.md rules, frontmatter requirements, status lifecycle, GitHub etiquettes

## Key Decisions

- Flat `changelog/` with numbered entries instead of nested adr/proposals/research directories
- `knowledge/` as flat category folders (no subcategory nesting beyond one level)
- `configs/` for live infrastructure configuration separate from `knowledge/` reference docs
- Content pipeline model (ideas → research → proposals) explicitly excluded
