---
title: "FastMCP"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - mcp
  - llm
  - python
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
  - url: "https://spec.modelcontextprotocol.io/"
    title: "MCP Specification"
last_audit_date: 2026-06-09
---

# FastMCP

**FastMCP** is a Python framework for building [Model Context Protocol](https://spec.modelcontextprotocol.io/) (MCP) servers. It provides a high-level, decorator-based API for exposing tools, resources, and prompts to LLM clients.

## Architecture

```
┌─────────────────────┐
│   LLM Client        │
│  (OpenCode, Claude) │
└──────────┬──────────┘
           │ JSON-RPC over stdio / SSE
┌──────────▼──────────┐
│   FastMCP Server    │
│                      │
│  @mcp.tool()         │
│  @mcp.resource()     │
│  @mcp.prompt()       │
│                      │
│  Lifecycle Hooks     │
│  Middleware          │
│  Rate Limiting       │
└──────────────────────┘
```

## Atomic Notes

### Getting Started
- [installation.md](./installation.md) — Install with `uv add fastmcp`
- [what-is-fastmcp.md](./what-is-fastmcp.md) — Overview of the framework
- [mcp-protocol-basics.md](./mcp-protocol-basics.md) — JSON-RPC, capabilities, lifecycle

### Server Setup
- [server-initialization.md](./server-initialization.md) — FastMCP() constructor
- [server-configuration.md](./server-configuration.md) — name, version, settings
- [lifecycle-hooks.md](./lifecycle-hooks.md) — Startup/shutdown hooks
- [server-middleware.md](./server-middleware.md) — Middleware for MCP servers

### Transports
- [transport-sse.md](./transport-sse.md) — SSE transport (HTTP)
- [transport-stdio.md](./transport-stdio.md) — stdio transport (stdin/stdout)

### Tools
- [tools-defining.md](./tools-defining.md) — @mcp.tool() decorator
- [tools-pydantic-input.md](./tools-pydantic-input.md) — Pydantic input models
- [tools-async-tools.md](./tools-async-tools.md) — Async tool functions
- [tools-error-handling.md](./tools-error-handling.md) — Error handling in tools
- [tools-context.md](./tools-context.md) — Context object
- [tools-list-tools.md](./tools-list-tools.md) — Tool listing protocol

### Resources
- [resources-defining.md](./resources-defining.md) — @mcp.resource() decorator
- [resources-uri-pattern.md](./resources-uri-pattern.md) — URI template resources
- [resources-static-resources.md](./resources-static-resources.md) — Static vs dynamic
- [resources-list-resources.md](./resources-list-resources.md) — Resource listing
- [resource-templates.md](./resource-templates.md) — ResourceTemplate patterns

### Prompts
- [prompts-defining.md](./prompts-defining.md) — @mcp.prompt() decorator
- [prompt-arguments.md](./prompt-arguments.md) — Prompt with parameters
- [prompt-templates.md](./prompt-templates.md) — Template rendering patterns

### Observability
- [logging-mcp.md](./logging-mcp.md) — MCP logging protocol
- [debugging.md](./debugging.md) — Debug mode and logging
- [troubleshooting.md](./troubleshooting.md) — Common issues

### Security & Control
- [rate-limiting.md](./rate-limiting.md) — Rate limiting
- [authentication.md](./authentication.md) — Auth patterns
- [error-handling.md](./error-handling.md) — Structured error responses

### Testing
- [testing-tools.md](./testing-tools.md) — Testing tool functions
- [testing-resources.md](./testing-resources.md) — Testing resource handlers
- [testing-prompts.md](./testing-prompts.md) — Testing prompt templates
- [testing-with-mcp-client.md](./testing-with-mcp-client.md) — Integration testing

### FastAPI Integration
- [mounting-fastapi.md](./mounting-fastapi.md) — Mount FastMCP on FastAPI
- [fastapi-shared-middleware.md](./fastapi-shared-middleware.md) — Shared middleware
- [fastapi-dependency-injection.md](./fastapi-dependency-injection.md) — DI patterns

### OpenCode Integration
- [opencode-configuration.md](./opencode-configuration.md) — Setup with OpenCode
- [opencode-tools-config.md](./opencode-tools-config.md) — opencode.json tools config
- [opencode-transport-config.md](./opencode-transport-config.md) — SSE vs stdio
