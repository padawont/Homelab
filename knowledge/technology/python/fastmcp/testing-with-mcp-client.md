---
title: "Integration Testing with MCP Client"
status: draft
author: refactorartist
date: 2026-06-09
tags:
  - fastmcp
  - testing
  - integration
  - mcp-client
sources:
  - url: "https://github.com/jlowin/fastmcp"
    title: "FastMCP on GitHub"
last_audit_date: 2026-06-09
---

# Integration Testing with MCP Client

Test your full MCP server end-to-end using an MCP client SDK.

## Using the MCP client in tests

```python
import pytest
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from fastmcp import FastMCP

# Create server module
mcp = FastMCP("test-server")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b
```

## Test via stdio subprocess

```python
@pytest.mark.anyio
async def test_tool_via_mcp_client():
    async with stdio_client(["uv", "run", "server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            assert any(t.name == "add" for t in tools)
            
            # Call tool
            result = await session.call_tool("add", {"a": 2, "b": 3})
            assert result.content[0].text == "5"
```

## Testing resources

```python
@pytest.mark.anyio
async def test_resource_via_mcp_client():
    async with stdio_client(["uv", "run", "server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Read resource
            content = await session.read_resource("config://app/version")
            assert "version" in content
```

## Fixture pattern

```python
@pytest.fixture
async def mcp_session():
    async with stdio_client(["uv", "run", "server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session
```

## Next steps

- [Testing Tools](./testing-tools.md)
- [Testing Resources](./testing-resources.md)
- [Testing Prompts](./testing-prompts.md)
