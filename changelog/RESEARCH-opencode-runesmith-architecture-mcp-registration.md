---
title: "MCP Server Registration"
status: exploring
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - mcp
  - runesmith
  - plugins
  - sdk
  - lifecycle
sources:
  - knowledge: "knowledge/tooling/opencode/mcp/overview.md"
  - knowledge: "knowledge/tooling/opencode/mcp/configuration.md"
  - knowledge: "knowledge/tooling/opencode/mcp/concepts.md"
  - knowledge: "knowledge/tooling/opencode/mcp/tool-management.md"
  - knowledge: "knowledge/tooling/opencode/plugins/npm-packaging.md"
  - knowledge: "knowledge/tooling/opencode/plugins/bundling-components.md"
references:
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://opencode.ai/docs/config"
    title: "OpenCode Config Documentation"
  - url: "https://opencode.ai/docs/sdk"
    title: "OpenCode SDK Documentation"
  - url: "https://github.com/anomalyco/opencode/issues/30130"
    title: "Issue #30130: Plugin-injected MCPs ignored in Desktop"
last_audit_date: 2026-06-09
---

# MCP Server Registration

## The Challenge

Unlike agents (`.md` files in `.opencode/agents/`) and skills (`SKILL.md` directories in `.opencode/skills/`), MCP servers are configured in `opencode.json` under the `mcp` key. The plugin cannot modify `opencode.json` directly — that is the user's configuration file. The plugin's init hook could theoretically edit JSON, but that would be destructive and unexpected for the user.

A separate mechanism is needed.

## SDK Issue Tracker Timeline

### Current SDK Status

As of research date (2026-06-09), the `@opencode-ai/plugin` SDK is at version **1.16.2** (latest stable, published 2026-06-05). The `@opencode-ai/plugin` npm package provides the `Plugin` TypeScript type, the `tool()` helper for defining custom tools, and event hooks (e.g., `tool.execute.before`, `session.created`, `shell.env`). However, it does **not** expose any `mcp.register` hook or any mechanism for a plugin to programmatically register MCP servers.

The `@opencode-ai/sdk` package (a separate SDK for building integrations that connect to OpenCode's server API) is also available but is designed for client-side interaction with sessions, files, and configuration — not for plugin-level MCP registration.

### Existing Issue: Plugin-Injected MCPs Not Supported

GitHub issue **#30130** ("Desktop v1.15.13: MCP servers not loaded (race condition in PR #28937 + plugin-injected MCPs ignored)") documents a concrete case where a plugin (oh-my-openagent v4.5.12) injects MCPs via the config hook by setting `config.mcp`, but the Desktop app does not process those entries. The CLI does load them, confirming a Desktop-specific gap, but more importantly it reveals that the **plugin config hook is not an officially supported path for MCP registration**. The fact that it works in the CLI is incidental — it is not a documented, stable API.

No dedicated feature request or issue specifically asking for a `mcp.register` SDK hook has been filed in the opencode repository as of this research date.

### Timeline Projection

| Horizon | Approach | Feasibility |
|---|---|---|
| **Short-term** (now — Q3 2026) | Approach A: Manual setup via documented snippets. Document exact `opencode.json` MCP configuration in plugin README. User copies snippet into their own config. | Fully viable today. No SDK changes needed. |
| **Medium-term** (Q3 2026 — Q1 2027) | If the `@opencode-ai/plugin` SDK adds an `mcp` configuration hook (e.g., returning MCP definitions from the plugin function alongside `tool`), the plugin could auto-register servers. This would require the SDK team to add a new hook type. No public roadmap indicates this is planned. | Speculative — depends on SDK evolution. |
| **Long-term** (beyond Q1 2027) | Full plugin-driven MCP management: plugins could register, configure, enable/disable, and remove MCP servers dynamically. This would require both an SDK hook and changes to how OpenCode's core processes plugin-contributed MCPs. | Highly speculative. Would need SDK and core changes. |

### Recommendation

Anchor on the short-term path (manual setup via documentation). Monitor the `@opencode-ai/plugin` SDK releases and the opencode issue tracker for any new hooks related to MCP configuration. If the SDK adds an `mcp` hook in a future version, this research should be revisited and Approach B re-evaluated.

## Approaches

### Approach A: Document and Manual Setup (Fallback)

The plugin README documents recommended MCPs with their exact `opencode.json` snippets. The user copies them into their config.

```json
{
  "mcp": {
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
      "enabled": true
    }
  }
}
```

**Pros**: Zero code, user has full control, no surprises.
**Cons**: Manual step, easy to miss or misconfigure, no automation.

### Approach B: Init Hook Writes a Config File (Practical Middle Ground)

The plugin init hook writes a `.opencode/runesmith-mcp.json` file with the MCP configurations. The README instructs users to add a reference in their `opencode.json` using whatever mechanism OpenCode supports for external MCP config includes.

```json
// .opencode/runesmith-mcp.json
{
  "github": {
    "type": "local",
    "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
    "enabled": true
  }
}
```

**Pros**: Semi-automated, user can review before accepting, file is versioned with the plugin.
**Cons**: Still requires a manual step to wire it up in `opencode.json`.

## Enhanced Workaround Details

### Config File Injection via Init Hook

The plugin's init hook can write arbitrary files into the `.opencode/` directory using the standard `fs` APIs. However, OpenCode does **not** support a `$ref` or `include` mechanism in `opencode.json` that would allow external JSON files to be merged into the `mcp` key. The OpenCode config system uses JSON merge semantics across config layers (remote, global, project, custom) but does not support file-level imports or references for specific keys.

This means writing a `.opencode/runesmith-mcp.json` file is only useful if the user manually copies its contents into their `opencode.json`. The init hook can produce the file, reducing the configuration surface to a copy-paste step, but it cannot eliminate the manual wiring entirely.

One enhancement to Approach B: the init hook could write the snippet and then log the exact path to copy from at startup:

```
[RuneSmith] MCP configuration snippet written to .opencode/runesmith-mcp.json
[RuneSmith] Copy this file's contents into your opencode.json under the "mcp" key.
```

This is marginally better than documenting the snippet in the README alone — the file is always up-to-date with the installed plugin version.

### Post-Install Hook Workaround

npm packages support `postinstall` scripts in `package.json` that run after `npm install`:

```json
{
  "scripts": {
    "postinstall": "node scripts/setup-mcp.mjs"
  }
}
```

However, this approach has significant limitations in the OpenCode plugin context:

1. **Bun auto-install does not run lifecycle scripts for dependencies.** OpenCode uses Bun to auto-install npm plugins at startup (`bun install` in the cache directory). By default, Bun does **not** execute lifecycle scripts (`preinstall`, `postinstall`) for installed dependencies — only packages listed in `trustedDependencies` in the project's `package.json` get their lifecycle scripts executed. The OpenCode cache installation path may not support this at all. Testing would be required to confirm whether `postinstall` hooks fire in the OpenCode cache context.

2. **Installed location is in the Bun cache.** Even if `postinstall` did run, the files would be written relative to `~/.cache/opencode/node_modules/@runicengines/opencode-runesmith/`, not the project's `.opencode/` directory. The script would need to determine the project root dynamically, which is unreliable during npm lifecycle events.

3. **No access to plugin context.** A `postinstall` script runs as a standalone Node.js process, not inside the OpenCode plugin runtime. It cannot access the `project` context, `directory`, or `client` that the plugin function receives. This makes it strictly inferior to the init hook for this purpose.

**Conclusion**: Post-install hooks are not a viable mechanism for MCP configuration. The init hook is strictly more capable because it runs inside the OpenCode plugin runtime with access to project context.

### SDK Hook Workaround: Init Hook Writing to .opencode/

The plugin's init hook (the plugin function itself) can write files to the project's `.opencode/` directory. The init hook receives the `project` and `directory` context, making it trivial to determine where to write:

```typescript
export const RuneSmithPlugin: Plugin = async ({ project }) => {
  const mcpConfigPath = join(project.path, ".opencode", "runesmith-mcp.json");
  writeFileSync(mcpConfigPath, JSON.stringify(mcpServers, null, 2));
  return { /* hooks */ };
};
```

The critical limitation, however, is that **OpenCode does not auto-discover MCP configurations from files in `.opencode/`**. MCP servers must be declared directly in `opencode.json` under the `mcp` key. The auto-discovery boundary documented in the bundling-components knowledge note confirms that OpenCode scans the project worktree and global config directory for agents, skills, tools, and plugins — but MCP configs are read exclusively from the merged `opencode.json` configuration.

This is in contrast to custom tools, which CAN be registered via the plugin's `tool` hook. There is no analogous `mcp` hook in the `@opencode-ai/plugin` SDK.

### Summary of Workaround Viability

| Technique | Can write to .opencode/ | Auto-discovered | Removes manual step |
|---|---|---|---|
| Init hook writes agent files | Yes | Yes (agents auto-discovered) | Yes |
| Init hook writes skill files | Yes | Yes (skills auto-discovered) | Yes |
| Init hook writes tool files via `tool` hook | N/A | Yes (plugin tool hook registers them) | Yes |
| Init hook writes MCP config file | Yes | **No** — MCPs not auto-discovered | No |
| Post-install script writes MCP config | Unreliable | **No** | No |
| Plugin config hook sets `config.mcp` | N/A | Partial — CLI only, not Desktop | Partially |

None of the available workarounds eliminate the manual step for MCP registration. The user must always modify `opencode.json`.

## Recommended Approach

Use **Approach A** (manual setup via documented snippets). This is the only viable approach because:

- Programmatic MCP registration (`mcp.register` hook) does not exist in the current `@opencode-ai/plugin` SDK (v1.16.2).
- The init hook cannot safely modify `opencode.json`, which belongs to the user.
- Writing a separate config file would still require a manual step to wire it up.
- Post-install hooks are unreliable in the OpenCode Bun cache installation context.
- The plugin config hook's ability to inject `config.mcp` is undocumented and only partially supported (CLI only, not Desktop).

Document the exact `opencode.json` snippet in the plugin README so users can copy it directly. This keeps the user in full control of their configuration while providing clear, copy-paste-ready instructions.

Monitor the `@opencode-ai/plugin` SDK changelog and opencode issue tracker for future MCP registration hooks. If the SDK adds an `mcp` hook, revisit this decision.

## MCPs to Consider Bundling

| MCP | Purpose | Priority |
|---|---|---|
| **GitHub MCP** (`@modelcontextprotocol/server-github`) | Repository operations, issues, PRs, file access | High — agents need GitHub interaction |
| **KB Search** (custom) | Query the Knowledge Base from any repo | Medium — see the [kb-discovery documentation](../kb-discovery/discovery-mechanism.md) |

## Key Decision

Do NOT bundle MCPs that require API keys or authentication configuration. The GitHub MCP works with the existing `GITHUB_TOKEN` the developer already has configured. Any custom MCP must also work with existing credentials to avoid adding auth overhead.
