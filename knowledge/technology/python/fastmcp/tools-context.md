---
title: "Tool Context"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - tools
  - context
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Tool Context

FastMCP provides a `Context` object to tools, giving access to request metadata, logging, and server state.

## Using context

Add a `Context` parameter — FastMCP injects it automatically:

```python
from fastmcp import FastMCP, Context

mcp = FastMCP("demo")

@mcp.tool()
async def long_task(duration: int, ctx: Context) -> str:
    """Run a task with progress reporting."""
    for i in range(duration):
        await ctx.report_progress(i, duration)
        ctx.info(f"Step {i + 1}/{duration}")
    return "Done"
```

## Context methods

Most Context methods are async. See [Async in sync tools](#async-context-methods-in-sync-functions) for calling them from synchronous tools.

### Properties

| Property | Type | Purpose |
|---|---|---|
| `ctx.request_id` | `str` | Current request identifier |
| `ctx.client_id` | `str \| None` | Connected client identifier |
| `ctx.fastmcp` | `FastMCP` | Reference to the FastMCP server instance |
| `ctx.transport` | `Transport` | Underlying transport layer |
| `ctx.session_id` | `str` | Current session identifier |
| `ctx.request_context` | `RequestContext` | Full request context (includes `client_id`, `meta`, etc.) |
| `ctx.state` | `StateNamespace` | Namespaced state storage per request (read/write) |

### Methods

| Method | Purpose |
|---|---|
| `ctx.info(msg)` | Log at INFO level via MCP logging |
| `ctx.warning(msg)` | Log at WARNING level |
| `ctx.error(msg)` | Log at ERROR level |
| `ctx.debug(msg)` | Log at DEBUG level |
| `ctx.report_progress(current, total)` | Send progress notification |
| `ctx.read_resource(uri)` | Read an MCP resource by URI |
| `ctx.list_resources()` | List available MCP resources |
| `ctx.sample(params)` | Sample from an LLM (MCP sampling) |
| `ctx.elicit(prompt)` | Higher-level LLM elicitation helper |
| `ctx.get_state(key, default=None)` | Retrieve a value from tool-level state |
| `ctx.set_state(key, value)` | Store a value in tool-level state |
| `ctx.delete_state(key)` | Remove a value from tool-level state |
| `ctx.send_notification(method, params)` | Send a custom notification to the client |
| `ctx.list_prompts()` | List available prompts |
| `ctx.get_prompt(name)` | Get a specific prompt by name |

## Context with sync tools

```python
@mcp.tool()
def sync_tool(ctx: Context) -> str:
    ctx.info("Running sync tool")
    return "ok"
```

> **Note**: In a sync tool you can call synchronous methods (`info`, `warning`, `error`, `debug`, `get_state`, `set_state`, `delete_state`) directly. Async methods (`report_progress`, `read_resource`, `sample`, etc.) require special handling — see [below](#async-context-methods-in-sync-functions).

## Async Context methods in sync functions

Because `Context` methods like `report_progress`, `read_resource`, and `sample` are async, you **cannot** simply `await` them inside a synchronous tool. Two workarounds:

1. **Use `asyncio.run()`** — suitable when no event loop is already running:
   ```python
   import asyncio

   @mcp.tool()
   def sync_tool(ctx: Context) -> str:
       asyncio.run(ctx.report_progress(0, 10))
       return "ok"
   ```

2. **Make the tool async** — the simplest approach for most cases:
   ```python
   @mcp.tool()
   async def async_tool(ctx: Context) -> str:
       await ctx.report_progress(0, 10)
       return "ok"
   ```

## The `CurrentContext()` dependency pattern

FastMCP also provides `CurrentContext` as an alternative to declaring a `ctx: Context` parameter. This is useful when you need the context from a nested helper function:

```python
from fastmcp import CurrentContext

def helper():
    ctx = CurrentContext.get()
    ctx.info("Inside a helper")

@mcp.tool()
async def my_tool(ctx: Context) -> str:
    helper()
    return "done"
```

`CurrentContext.get()` returns the active `Context` for the current request, or `None` if called outside a request. You can also use `CurrentContext.get_required()` to raise if no context is available.

## Next steps

- [Defining Tools](./tools-defining.md)
- [Logging (MCP)](./logging-mcp.md)
