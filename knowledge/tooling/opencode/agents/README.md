# OpenCode Agents

Reference documentation for the OpenCode agent system: types, configuration, permissions, discovery, and context loading.

## Files

- `overview.md` — Summary index with links to all atomic notes
- `concepts.md` — What agents are, primary vs subagent, built-in agents
- `interactions.md` — Agent ↔ skill and agent ↔ task tool relationships
- `lifecycle.md` — Agent lifecycle, invocation modes, session navigation
- `configuration.md` — Definition formats (JSON and Markdown), all configuration options
- `permissions.md` — Permission model, keys, object syntax, bash/task/skill granularity
- `discovery.md` — Auto-discovery paths, explicit registration, naming conventions, precedence
- `context-loading.md` — How AGENTS.md is consumed via `instructions`, `prompt`, and lazy loading
- `roles.md` — Pre-assembled subagent role profiles for domain-specific tasks (architect, developer, reviewer, etc.)
- `composition-patterns.md` — Primary + specialist workflows, review pipelines, and best practices
- `orchestration-patterns.md` — Multi-agent coordination: hub-and-spoke, gated pipeline, chain-of-responsibility, skill-routing
