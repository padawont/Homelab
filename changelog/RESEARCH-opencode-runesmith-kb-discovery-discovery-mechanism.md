---
title: "KB Discovery Mechanism Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - kb-discovery
  - runesmith
  - knowledge-base
sources:
  - knowledge: "knowledge/tooling/opencode/skills/full-text-search.md"
  - knowledge: "knowledge/tooling/opencode/skills/cross-reference.md"
references:
  - url: "https://opencode.ai/docs/tools"
    title: "OpenCode Tools Documentation"
last_audit_date: 2026-06-07
---

# KB Discovery Mechanism Design

## Problem

The `@runicengines/opencode-runesmith` plugin operates inside arbitrary code
repositories — for example, `github.com/RunicEngines/project-x`. These repos
have no inherent relationship to the Knowledge Base repository at
`github.com/RunicEngines/knowledge-base`. When a RuneSmith agent needs to look
up a technical reference, verify an architectural pattern, or retrieve prior
research, it must first discover and then access the Knowledge Base.

This is a bootstrap problem: the agent must know _how_ to find the KB before it
can use the KB. The discovery mechanism must be reliable (always works),
performant (minimal latency), and secure (no unnecessary credential exposure).

A secondary concern is separation of concerns: RuneSmith agents are generalist
coding agents. They handle issue triage, PR review, test writing, and
architecture discussion. They are not Knowledge Base agents. They must not
delegate to or invoke KB-specific agents. However, they do need to _search_ the
Knowledge Base for reference content relevant to their current task. The
discovery mechanism is the bridge that makes this possible without coupling the
agent systems.

## Discovery Approaches

Three approaches were evaluated, each representing a different trade-off
between simplicity, reliability, and runtime overhead.

### Approach A: Config URL (Recommended)

The simplest approach: embed the Knowledge Base repository URL directly into
the RuneSmith agent prompt or a plugin-level configuration file (e.g.,
`.opencode/runesmith.json`).

**Mechanism:**

1. The agent prompt includes a constant such as:
   `KB_REPO = "github.com/RunicEngines/knowledge-base"`
2. On first use, the agent runs `gh repo clone` or `git clone` using this URL.
3. Subsequent searches read from the cloned copy.

**Pros:**

- No runtime resolution logic required.
- Works offline after initial clone.
- Fully predictable — the URL is known at prompt-authoring time.
- Compatible with any CI/CD or local environment that has `git` and `gh`.

**Cons:**

- Hardcoded — if the KB moves to a new organization or renames, every agent
  prompt and config file must be updated.
- No automatic failover — a stale URL means silent failure unless the agent is
  programmed to detect clone failures.
- Requires coordination between plugin releases and repository moves.

**Implementation detail:** The URL should be stored in a single well-known
location rather than duplicated across agent prompts. A plugin-level config
file (`.opencode/runesmith.json`) with a `kb_repo` field is the recommended
storage point. Agent prompts reference this config at runtime via OpenCode's
`config` tool or environment variable resolution.

### Approach B: GitHub API Lookup

The agent queries the GitHub API to discover the Knowledge Base repository at
runtime.

**Mechanism:**

1. The agent calls `gh repo list RunicEngines --json name --jq '.[] | select(.name == "knowledge-base")'`
2. If found, the canonical clone URL is extracted from the response.
3. The agent clones or pulls from that URL.

**Pros:**

- No hardcoded URL — always discovers the canonical location.
- Resilient to repository renames (within the same org).
- Can verify repository existence before attempting a clone.

**Cons:**

- Requires `gh` CLI authentication and `bash: { "gh *": "allow" }` permission.
- Network call on every fresh discovery adds latency (~500ms–2s).
- No offline fallback — if GitHub is unreachable, discovery fails entirely.
- Rate limits and token scopes may block unauthenticated lookups in CI
  environments.
- The `gh repo list` approach requires listing all repos in the org; a targeted
  `gh repo view RunicEngines/knowledge-base` is more efficient but still
  requires a network round trip.

**Permission requirements:**

```yaml
bash:
  "gh repo view RunicEngines/knowledge-base": "allow"
  "gh repo clone RunicEngines/knowledge-base": "ask"
```

### Approach C: Convention-based Path

Assume the Knowledge Base is cloned at a predetermined filesystem path relative
to the current repository.

**Mechanism:**

1. Define a convention, e.g., `../knowledge-base/` relative to the project root,
   or `$HOME/.runicengines/knowledge-base/`.
2. The agent checks for the existence of this path on startup.
3. If present, searches operate directly on the local filesystem.

**Pros:**

- Zero network overhead — fully offline once cloned.
- No API tokens or permissions required for discovery.
- Instantaneous — just a filesystem stat call.

**Cons:**

- Extremely fragile — depends on the developer manually cloning the KB to the
  right location.
- No fallback or error messaging if the path doesn't exist.
- Breaks in CI/CD environments where the KB is unlikely to be pre-cloned.
- Different operating systems, shell configurations, and project structures
  would all need to agree on the convention.
- No version pinning — the agent cannot know if the local clone is the intended
  branch or commit.

## Comparison Summary

| Criterion | A: Config URL | B: GitHub API | C: Convention Path |
|---|---|---|---|
| Setup complexity | Low | Medium | Low |
| Runtime latency | None (cached) | ~500ms–2s per discovery | None |
| Offline capable | Yes (after clone) | No | Yes |
| Hardcoded dependency | Yes (URL in config) | No | No |
| Permission scope | `git` + `gh clone` | `gh *` + API token | Filesystem read |
| Resilience to move | None | High (same org) | None |
| CI/CD compatibility | Good (clone on demand) | Good (if token available) | Poor |
| Implementation effort | Minimal | Moderate | Minimal |

## Recommended Approach

**Approach A (Config URL) is recommended as the primary mechanism**, with
Approach B (GitHub API) as an automatic fallback when the config URL fails.

### Justification

1. **Simplicity wins.** The Knowledge Base is a single, well-known repository
   under the RunicEngines organization. The likelihood of it moving is low. A
   hardcoded URL in the plugin config is the simplest thing that works.

2. **Separation of configuration from agent prompts.** By storing the URL in
   `.opencode/runesmith.json` rather than in agent prompt text, the URL can be
   updated without modifying agent definitions. The config file is installed by
   the plugin itself and can be patched in a plugin update.

3. **Optional API fallback covers the edge case.** If the config URL clone
   fails (404, DNS error), the agent can fall back to a `gh repo view` API call
   to rediscover the canonical URL. This covers repository renames without
   adding latency to the common case.

4. **Convention path is rejected.** It introduces fragility without meaningful
   upside. The config URL approach achieves the same zero-latency benefit with
   better discoverability and error reporting.

### Recommended rs-kb-search Skill Interface

The discovery mechanism is exposed through a `rs-kb-search` skill or custom
tool that agents call when they need to find content in the Knowledge Base. Its
contract is:

1. **Locate** — resolve the KB repository URL from config (primary) or GitHub
   API (fallback). Cache the result per session.
2. **Acquire** — if no local clone exists, clone the KB into
   `.opencode/runesmith/cache/knowledge-base/`. If a clone exists, `git pull`
   to refresh. Use a persistent cache directory rather than a temp directory to
   avoid repeated cloning across agent invocations.
3. **Search** — run `grep`, `glob`, or `rg` against the local clone. Return
   structured results (file path, match line, surrounding context).
4. **Respond** — present the results to the calling agent in a consistent
   format.

```yaml
# Permission profile for rs-kb-search
bash:
  "gh repo view RunicEngines/knowledge-base": "allow"
  "git clone": "ask"
  "git pull": "allow"
read: "allow"
glob: "allow"
```

### Stale Clone Refresh Policy

Once the KB is cloned to `.opencode/runesmith/cache/knowledge-base/`, the
agent must decide when to refresh. The recommended policy:

- **On every `rs-kb-search` invocation:** run `git pull --ff-only` with a
  timeout of 5 seconds. If the pull succeeds, the clone is up to date. If it
  fails (network down, large fetch), fall back to the existing clone.
- **Stale window:** if the clone is less than 1 hour old and a `git pull`
  fails, the agent may use the stale clone without error. If the clone is older
  than 24 hours and refresh fails, warn the user that the KB may be outdated.

## Open Questions

1. **Persistent vs. ephemeral cache:** Should the KB be cloned into a
   temporary directory that is destroyed when the agent session ends, or a
   persistent location like `.opencode/runesmith/cache/`? Persistent caching
   avoids repeated cloning (each clone is ~50MB+) but must handle garbage
   collection and concurrent agent access. The recommendation is persistent
   with a simple lock file for concurrent safety.

2. **Refresh granularity:** Should the agent `git pull` on every search, or
   only periodically? Pulling on every search adds <1s latency when the remote
   is reachable, but can delay the agent on a slow connection. The recommended
   policy above balances freshness with responsiveness.

3. **Branch pinning:** Should the agent pin to a specific branch (e.g.,
   `main`) or always use the default branch? Pinning to `main` avoids
   surprises if the default branch changes but risks staleness. Recommendation:
   pin to `main` and pull on every access.

4. **Search scope:** Should `rs-kb-search` support full-text regex searches,
   or only structured queries (by tag, by path, by frontmatter field)?
   Initially, full-text grep with path filtering is sufficient. Structured
   query support can be added later as a frontmatter-aware indexer.
