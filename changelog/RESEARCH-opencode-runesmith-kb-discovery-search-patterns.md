---
title: "KB Search Patterns Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - kb-discovery
  - search
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/skills/full-text-search.md"
  - knowledge: "knowledge/tooling/opencode/skills/pipeline-trace.md"
references:
  - url: "https://opencode.ai/docs/tools"
    title: "OpenCode Tools Documentation"
last_audit_date: 2026-06-07
---

# KB Search Patterns Design

## Context

The `@runicengines/opencode-runesmith` plugin requires a systematic approach to searching the Knowledge Base once it has been discovered and registered. While KB discovery (locating and indexing the KB) is handled by a separate mechanism, this document analyzes **what** to search and **how** to search it. The search layer is the primary way agents interact with the KB after discovery — it powers everything from context-gathering during task execution to pipeline tracing for architecture analysis.

The Knowledge Base follows a structured pipeline: `Idea → Knowledge → Research → Proposal → ADR`. Each section has distinct frontmatter conventions, cross-linking patterns, and status lifecycles. Search patterns must account for these conventions to return relevant, actionable results.

## Findings

### Search Type Catalog

Five fundamental search patterns emerged from analyzing how agents query the KB. Each serves a distinct use case and maps to a different implementation approach.

#### 1. Full-Text Search

Full-text search is the most general-purpose and most-used search type. It scans all markdown files in the KB directory tree for keyword or phrase matches.

**Use case:** An agent working on a development task needs to find all knowledge notes, research, and proposals related to "OpenCode skills" or "tool permissions."

**Approach:** Execute `grep -r` (or an equivalent recursive text search) across the entire KB directory. Results are filtered by relevance (frequency, section priority) and returned as file paths with matching line excerpts.

**Tool:** A custom `rs-kb-search` tool (or OpenCode skill) that wraps `grep -rnI --include="*.md" "<query>" <kb-path>` and returns structured results. The search should exclude `.git` directories and binary files.

**Scope:** All markdown files in `ideas/`, `knowledge/`, `research/`, `proposals/`, `adr/`, and `templates/`. Projects and tasks sections are registries and may be excluded or searched separately.

**Limitations:** No semantic understanding — purely lexical matching. A query for "decision" will not match "ADR" unless the text appears literally.

#### 2. Cross-Reference Lookup

The KB uses frontmatter fields to establish explicit links between documents: `related_ideas`, `sources`, `related_research`, `related_adrs`, `replaces`, and `replaced-by`. Cross-reference lookup traces these connections to build a graph of related documents.

**Use case:** An architect investigating "OpenCode skill registration" needs to find all research, proposals, and ADRs that reference it.

**Approach:** Parse the YAML frontmatter of all documents, extract `related_*` and `sources` fields, and build a bidirectional index. Given a target document, return both incoming links (documents that point to it) and outgoing links (documents it points to).

**Tool:** A `rs-kb-cross-ref` skill that, given a topic path, returns all documents that link to or from it. Implementation reads frontmatter using a YAML parser (e.g., Python `yaml` module or `yq`) and resolves relative paths against the KB root.

**Traversal depth:** Single-hop by default, configurable for multi-hop traversal ("find everything connected to this idea within 2 hops").

#### 3. Pipeline Tracing

Pipeline tracing follows a topic through the KB content pipeline: from idea inception through knowledge gathering, research analysis, proposal planning, and ultimately to an architecture decision record.

**Use case:** Understanding why a particular architectural decision was made by tracing it back through the pipeline to the original idea and knowledge that informed it.

**Approach:** A bidirectional walk of the pipeline graph. Start at any document in the pipeline and follow `sources` fields backward (upstream) or `related_*` and `related_research`/`related_adrs` fields forward (downstream). The pipeline direction is:

```
Idea ←→ Knowledge ←→ Research ←→ Proposal ←→ ADR
```

**Tool:** A `rs-kb-pipeline-trace` skill that takes a starting document path and a direction (`upstream` or `downstream`) and returns the full chain. The skill understands the pipeline semantics — it knows that `sources` in a research doc link to knowledge notes, while `related_adrs` in a proposal link to ADRs.

**Example trace:** Given an ADR, trace upstream: ADR → Proposal (via `related_adrs` in proposal) → Research (via `related_research` in proposal) → Knowledge (via `sources` in research) → Idea (via `related_ideas` in knowledge or manual link).

#### 4. Status-Aware Queries

Documents in the KB have a `status` field that tracks their lifecycle position (e.g., `draft`, `exploring`, `proposed`, `accepted`, `completed`, `superseded`). Status-aware queries filter results to include only documents at specific lifecycle stages.

**Use case:** A tech lead assembling a proposal needs to reference only `accepted` or `completed` research — not drafts still under investigation.

**Approach:** Parse the `status` field from frontmatter and filter results. Can be combined with other search types (e.g., full-text search restricted to `accepted` documents only).

**Tool:** An argument or flag added to any search tool: `rs-kb-search --status accepted` or `rs-kb-cross-ref --status completed`. Implementation reads the `status` YAML field directly.

**Filters:** Supports exact match (`accepted`), exclusion (`!= superseded`), and stage grouping (`>= proposed` for any document past the proposal stage).

#### 5. Recent Content

Recent content queries identify documents that were created or updated recently, using the `date` and `last_audit_date` frontmatter fields.

**Use case:** An agent that runs periodically wants to check what has changed since its last run, or a developer wants to see what's new in the KB this week.

**Approach:** Parse `date` (creation) and `last_audit_date` (last reviewed) from frontmatter. Sort by the later of the two fields. Support a `--since <date>` filter parameter.

**Tool:** A `rs-kb-recent` skill that accepts `--days <N>` or `--since <YYYY-MM-DD>` and returns documents ordered by freshness. Can be scoped to specific sections.

## Analysis

### Search Type Interdependence

The five search types are not independent. They form a layered stack:

1. **Full-text search** is the foundation — it works on any KB without frontmatter support.
2. **Cross-reference lookup** depends on well-formed frontmatter but is more precise than full-text.
3. **Pipeline tracing** depends on both full-text and cross-reference to navigate the graph.
4. **Status-aware queries** are a filter modifier that can be applied to any other search type.
5. **Recent content** is a sorting/filter modifier also applicable to any other search type.

An effective search system should implement all five but can prioritize the stack from bottom to top.

### Implementation Priority

The recommended implementation order is:

**1. Full-text search (Priority: Highest).** It provides immediate value, requires no frontmatter infrastructure, and is useful even in partially populated KBs. Implementation is straightforward: a shell script or OpenCode skill wrapping `grep -rnI`.

**2. Cross-reference lookup (Priority: High).** Once documents have stable frontmatter, cross-reference enables graph-based discovery. This is where the KB becomes more than a collection of documents — it becomes a connected knowledge graph.

**3. Pipeline tracing (Priority: Medium).** This is a specialized use case built on top of cross-reference. It requires understanding pipeline semantics and is most useful for architecture and governance workflows.

**4. Status-aware queries (Priority: Medium).** Useful but not critical. Implement as a filter modifier on full-text and cross-reference tools.

**5. Recent content (Priority: Low).** Nice-to-have for periodic sync workflows. Lower priority because agents can track their own state externally.

### KB Structure Reference

Agents need to know the KB directory layout to target searches efficiently:

```
knowledge-base/
├── ideas/          # What we're going to do
├── knowledge/      # Technical reference info
├── research/       # Analysis (this section)
├── proposals/      # Implementation plans
├── adr/            # Architecture decisions
├── templates/      # Document templates
└── projects/       # Repo registry (minimal content)
```

When searching, agents should:
- Exclude `templates/` by default (they are scaffolds, not content)
- Include `projects/` only for registry lookups
- Target specific sections when the task domain is known (e.g., search only `adr/` for decisions)

## Recommendations

1. **Implement full-text search first** as a simple `rs-kb-search` skill. Use `grep -rnI --include="*.md"` with result ranking by section priority (knowledge > research > proposals > ideas > adr).
2. **Add cross-reference lookup second** as `rs-kb-cross-ref`. Build a YAML frontmatter index that is cached and invalidated on file changes.
3. **Layer pipeline tracing third** using the cross-reference index. Add a `--direction upstream|downstream` flag to the cross-reference skill.
4. **Add status filtering** as a `--status` parameter to existing skills rather than a standalone tool.
5. **Add recent content** as a `--since` or `--days` parameter. Tie it to file modification times as a fallback when `last_audit_date` is missing.
6. **Reference the existing knowledge notes** at `knowledge/tooling/opencode/skills/full-text-search.md` and `knowledge/tooling/opencode/skills/pipeline-trace.md` for detailed implementation patterns.
