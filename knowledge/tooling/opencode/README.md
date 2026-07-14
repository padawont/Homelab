# OpenCode

Reference documentation for the OpenCode AI coding agent ecosystem: agents, skills, plugins, custom tools, MCP servers, SDK, and community extensions.

## Topics

### Agents
Agent types, configuration, permissions, discovery, context loading, and role-based agent patterns.

**Files:** `agents/overview.md`, `agents/concepts.md`, `agents/interactions.md`, `agents/lifecycle.md`, `agents/configuration.md`, `agents/permissions.md`, `agents/discovery.md`, `agents/context-loading.md`, `agents/roles.md`, `agents/composition-patterns.md`

### Skills
Reusable instruction bundles loaded on-demand by agents: format, configuration, workflow patterns, discovery patterns, and catalogue registry.

**Files:** `skills/overview.md`, `skills/concepts.md`, `skills/file-format.md`, `skills/tool-mechanism.md`, `skills/configuration.md`, `skills/gh-case-study.md`, `skills/workflow-patterns.md`, `skills/issue-to-plan.md`, `skills/pr-packager.md`, `skills/test-helper.md`, `skills/changelog-manager.md`, `skills/code-reviewer.md`, `skills/dependency-checker.md`, `skills/discovery-patterns.md`, `skills/full-text-search.md`, `skills/cross-reference.md`, `skills/pipeline-trace.md`, `skills/status-query.md`, `skills/recent-content.md`, `skills/convention-registration.md`, `skills/metadata-taxonomy.md`, `skills/maintenance.md`

### Plugins
Plugin architecture, events reference, distribution (npm packaging and private registries), and bundling agents/skills/tools in plugins.

**Files:** `plugins/overview.md`, `plugins/architecture.md`, `plugins/loading.md`, `plugins/creation.md`, `plugins/examples.md`, `plugins/npm-packaging.md`, `plugins/private-distribution.md`, `plugins/versioning.md`, `plugins/publishing-workflow.md`, `plugins/bundling-components.md`, `plugins/event-command.md`, `plugins/event-chat.md`, `plugins/event-permission.md`, `plugins/event-shell.md`, `plugins/event-tool.md`, `plugins/event-session.md`, `plugins/event-file.md`, `plugins/event-system.md`, `plugins/event-tui.md`, `plugins/event-compaction.md`, `plugins/event-patterns.md`

### Custom Tools
Creating custom tools with the `tool()` helper, Zod argument schemas, execution context, multi-tool files, name collisions, and cross-language tools.

**Files:** `custom-tools/overview.md`, `custom-tools/definition.md`, `custom-tools/arguments.md`, `custom-tools/execution-context.md`, `custom-tools/advanced.md`, `custom-tools/permissions.md`

### MCP Servers
Model Context Protocol server integration: local and remote server configuration, OAuth authentication, tool management, and usage examples.

**Files:** `mcp/overview.md`, `mcp/concepts.md`, `mcp/configuration.md`, `mcp/local-servers.md`, `mcp/remote-servers.md`, `mcp/oauth.md`, `mcp/tool-management.md`, `mcp/examples.md`

### SDK
Type-safe clients for the OpenCode server API: JS/TS (`@opencode-ai/sdk`) and Python (`opencode-ai`).

**Files:** `sdk/overview.md`, `sdk/installation.md`, `sdk/client-creation.md`, `sdk/types.md`, `sdk/error-handling.md`, `sdk/structured-output.md`, `sdk/api-sessions.md`, `sdk/api-files.md`, `sdk/api-tui.md`, `sdk/api-misc.md`, `sdk/python.md`

### Ecosystem
Community plugins, projects, and agents extending the OpenCode runtime.

**Files:** `ecosystem/overview.md`, `ecosystem/plugins.md`, `ecosystem/projects.md`, `ecosystem/agents.md`
