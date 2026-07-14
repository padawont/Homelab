# OpenCode Plugins

Reference documentation for the OpenCode plugin system: architecture, loading, installation, creation, events, and examples.

## Files

- `overview.md` -- Plugin system reference: loading methods, load order, creation guide, event hooks, examples

### Architecture & Creation
- `architecture.md` -- Local vs npm plugins, installation mechanics, publishing overview
- `loading.md` -- Load order (global → project → local) and deduplication rules
- `creation.md` -- Basic plugin structure, TypeScript support, dependencies, configuration patterns
- `examples.md` -- Complete code examples: notifications, .env protection, custom tools, logging, compaction hooks

### Distribution
- `npm-packaging.md` -- Package naming, `@opencode-ai/plugin` dependency, package.json conventions, Bun auto-install, caching
- `private-distribution.md` -- GitHub npm registry, .npmrc, authentication tokens, consumer configuration
- `versioning.md` -- SemVer strategy, changelog conventions, breaking change migration
- `publishing-workflow.md` -- Manual publishing, version bumps, CI/CD via GitHub Actions, GitHub Release integration

### Bundle Components
- `bundling-components.md` -- Bundling agents, skills, and custom tools in a single npm plugin; directory layout; auto-discovery boundary; registration mechanisms

### Event Reference
- `event-command.md` -- `command.execute.before`
- `event-chat.md` -- `chat.message`, `chat.params`, `chat.headers`
- `event-permission.md` -- `permission.ask`
- `event-shell.md` -- `shell.env`
- `event-tool.md` -- `tool.execute.before`, `tool.execute.after`, `tool.definition`
- `event-session.md` -- All 8 session SSE events
- `event-file.md` -- `file.edited`, `file.watcher.updated`
- `event-system.md` -- Installation, LSP, Message, Server, Todo SSE events
- `event-tui.md` -- `tui.prompt.append`, `tui.command.execute`, `tui.toast.show`
- `event-compaction.md` -- All 6 experimental hooks
- `event-patterns.md` -- Named handlers vs wildcard event handler
