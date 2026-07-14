---
title: "MCP Concepts"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - mcp
  - concepts
sources:
  - url: "https://opencode.ai/docs/mcp-servers"
    title: "OpenCode MCP Servers Documentation"
last_audit_date: 2026-06-07
---

# MCP Concepts

## What MCP Is

The Model Context Protocol (MCP) is an open standard that adds external tools to OpenCode agents. MCP servers expose tools, resources, and prompts that agents can invoke directly during a session. This allows agents to interact with real systems — databases, APIs, file systems, and services — through a unified interface.

### Local vs Remote Servers

MCP servers can run in two modes:

- **Local**: A subprocess spawned by OpenCode on the user's machine. The `command` array specifies the executable and arguments. OpenCode communicates via stdio.
- **Remote**: An HTTP endpoint reachable over the network. OpenCode sends JSON-RPC messages over HTTP POST. Supports authentication via headers or OAuth.

### Caveats

MCP servers add to the model's context window. Each tool exposed by an MCP server consumes tokens in the system prompt. Be selective about which servers you enable — too many can degrade agent performance and increase latency. Only enable servers that provide tools your agents actually need for their tasks.

### MCP vs Custom Tools

MCP tools come from external servers — either local subprocesses or remote HTTP endpoints — and integrate via the Model Context Protocol. Custom tools are TypeScript/JavaScript files placed in `.opencode/tools/` (project-level) or `~/.config/opencode/tools/` (global) that use the `tool()` helper from `@opencode-ai/plugin`. They are auto-discovered by OpenCode rather than declared in configuration. This fundamental difference in integration mechanism is why they live as sibling topics under `knowledge/tooling/opencode/`.

## See Also

- [MCP Configuration](configuration.md)
- [Custom Tools](../custom-tools/overview.md)
