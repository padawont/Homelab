# FastMCP

Python framework for building MCP (Model Context Protocol) servers.

## Contents

| # | File | Topic |
|---|---|---|
| 1 | [overview.md](./overview.md) | Topic hub and index |
| | **Getting Started** | |
| 2 | [installation.md](./installation.md) | uv add fastmcp |
| 3 | [what-is-fastmcp.md](./what-is-fastmcp.md) | MCP server framework overview |
| 4 | [mcp-protocol-basics.md](./mcp-protocol-basics.md) | JSON-RPC, capabilities, lifecycle |
| | **Server Setup** | |
| 5 | [server-initialization.md](./server-initialization.md) | FastMCP() constructor |
| 6 | [server-configuration.md](./server-configuration.md) | name, version, settings |
| 7 | [lifecycle-hooks.md](./lifecycle-hooks.md) | Startup/shutdown hooks |
| 8 | [server-middleware.md](./server-middleware.md) | Middleware for MCP servers |
| | **Transports** | |
| 9 | [transport-sse.md](./transport-sse.md) | SSE transport — endpoint, events |
| 10 | [transport-stdio.md](./transport-stdio.md) | stdio transport — stdin/stdout |
| | **Tools** | |
| 11 | [tools-defining.md](./tools-defining.md) | @mcp.tool() decorator |
| 12 | [tools-pydantic-input.md](./tools-pydantic-input.md) | Tool params with Pydantic models |
| 13 | [tools-async-tools.md](./tools-async-tools.md) | Async tool functions |
| 14 | [tools-error-handling.md](./tools-error-handling.md) | Tool exceptions → protocol errors |
| 15 | [tools-context.md](./tools-context.md) | Context object in tools |
| 16 | [tools-list-tools.md](./tools-list-tools.md) | How MCP lists tools to client |
| | **Resources** | |
| 17 | [resources-defining.md](./resources-defining.md) | @mcp.resource() decorator |
| 18 | [resources-uri-pattern.md](./resources-uri-pattern.md) | URI template resources |
| 19 | [resources-static-resources.md](./resources-static-resources.md) | Static vs dynamic resources |
| 20 | [resources-list-resources.md](./resources-list-resources.md) | Resource listing |
| 21 | [resource-templates.md](./resource-templates.md) | ResourceTemplate patterns |
| | **Prompts** | |
| 22 | [prompts-defining.md](./prompts-defining.md) | @mcp.prompt() decorator |
| 23 | [prompt-arguments.md](./prompt-arguments.md) | Prompt with parameters |
| 24 | [prompt-templates.md](./prompt-templates.md) | Template rendering patterns |
| | **Observability** | |
| 25 | [logging-mcp.md](./logging-mcp.md) | MCP logging protocol |
| 26 | [debugging.md](./debugging.md) | Debug mode, logging |
| 27 | [troubleshooting.md](./troubleshooting.md) | Common issues and fixes |
| | **Security & Control** | |
| 28 | [rate-limiting.md](./rate-limiting.md) | Tool rate limiting |
| 29 | [authentication.md](./authentication.md) | Auth patterns for MCP |
| 30 | [error-handling.md](./error-handling.md) | Structured error responses |
| | **Testing** | |
| 31 | [testing-tools.md](./testing-tools.md) | Testing tool functions |
| 32 | [testing-resources.md](./testing-resources.md) | Testing resource handlers |
| 33 | [testing-prompts.md](./testing-prompts.md) | Testing prompt templates |
| 34 | [testing-with-mcp-client.md](./testing-with-mcp-client.md) | Integration testing with MCP client |
| | **FastAPI Integration** | |
| 35 | [mounting-fastapi.md](./mounting-fastapi.md) | FastMCP app on FastAPI |
| 36 | [fastapi-shared-middleware.md](./fastapi-shared-middleware.md) | Shared CORS, auth middleware |
| 37 | [fastapi-dependency-injection.md](./fastapi-dependency-injection.md) | Access FastAPI deps from MCP |
| | **OpenCode Integration** | |
| 38 | [opencode-configuration.md](./opencode-configuration.md) | Setting up OpenCode with FastMCP |
| 39 | [opencode-tools-config.md](./opencode-tools-config.md) | Tools config in opencode.json |
| 40 | [opencode-transport-config.md](./opencode-transport-config.md) | SSE vs stdio for OpenCode |
