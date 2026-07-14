---
title: "Plugin SDK API for Python Developers"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-08
tags:
  - opencode
  - plugins
  - sdk
  - python
  - typescript
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://www.npmjs.com/package/@opencode-ai/plugin"
    title: "@opencode-ai/plugin on npm"
  - url: "https://docs.python.org/3/library/asyncio.html"
    title: "asyncio — Python Documentation"
  - url: "https://docs.python.org/3/library/pathlib.html"
    title: "pathlib — Python Documentation"
  - url: "https://docs.python.org/3/library/subprocess.html"
    title: "subprocess — Python Documentation"
  - url: "https://bun.sh/docs/runtime/shell"
    title: "Bun Shell API"
last_audit_date: 2026-06-08
---

# Plugin SDK API for Python Developers

This reference maps the OpenCode Plugin SDK (`@opencode-ai/plugin`) API surface to Python equivalents. It is designed for Python developers who need to understand, write, or reason about OpenCode plugins without deep TypeScript/Node.js knowledge.

For the **init hook lifecycle** specifically (the factory function, context object, version stamping), see [Init Hook Lifecycle](../init-hook-lifecycle.md) — this note covers the **entire SDK API** beyond the init hook.

## 1. Plugin Type Signature and Async activate() Pattern

### 1.1 The `Plugin` Type

In TypeScript, a plugin is a typed async function:

```typescript
// TypeScript — Plugin type from @opencode-ai/plugin
import type { Plugin } from "@opencode-ai/plugin";

export const MyPlugin: Plugin = async ({
  project,
  client,
  $,
  directory,
  worktree,
}) => {
  // Startup logic here
  return {
    "tool.execute.before": async (input, output) => {
      // Handler logic
    },
  };
};
```

There is **no equivalent single type** in Python's type system. The closest analogs, depending on how you structure your mental model:

| TypeScript concept | Python equivalent |
|---|---|
| `Plugin` type (callable signature) | `Protocol` with `__call__` or a `Callable` type alias |
| Context object destructuring | `@dataclass` with named fields |
| Return value (hooks dict) | `dict[str, Callable]` or a class with handler methods |
| `async` factory | `async def activate(ctx: PluginContext) -> dict[str, ...]` |

### 1.2 Context Object — Python Dataclass

The destructured context `{ project, client, $, directory, worktree }` becomes a typed dataclass in Python:

```python
# Python — Dataclass equivalent of the TypeScript context object
from dataclasses import dataclass, field
from typing import Any

@dataclass
class PluginContext:
    """The context object passed to every plugin factory."""
    project: "ProjectInfo"
    client: "OpenCodeClient"
    shell: "ShellAPI"       # Bun's $ API equivalent
    directory: str          # Current working directory
    worktree: str | None    # Git worktree path, if any

@dataclass
class ProjectInfo:
    name: str
    path: str
    config: dict[str, Any]
```

In TypeScript, destructuring at the parameter level is idiomatic. In Python, the idiomatic equivalent is to accept a single context object and access fields by name:

```python
# Python — Using the dataclass
async def activate(ctx: PluginContext) -> dict[str, Any]:
    # Access fields via named attributes
    project_root = ctx.project.path
    logger = ctx.client

    # Startup logic here

    return {
        "tool.execute.before": on_tool_execute,
    }
```

### 1.3 Return Value — Hooks Dict vs Handler Class

TypeScript returns a plain object with event-name keys:

```typescript
return {
  "tool.execute.before": async (input, output) => { /* ... */ },
  "chat.message": async (input, output) => { /* ... */ },
};
```

Python can use the same dict-of-callbacks pattern:

```python
# Python — Dict of async callbacks
async def on_tool_execute(input_data: ToolInput, output_data: ToolOutput) -> None:
    """Handle tool.execute.before event."""
    # ... handler logic ...

async def on_chat_message(input_data: ChatMessageInput, output_data: ChatMessageOutput) -> None:
    """Handle chat.message event."""
    # ... handler logic ...

async def activate(ctx: PluginContext) -> dict[str, Any]:
    return {
        "tool.execute.before": on_tool_execute,
        "chat.message": on_chat_message,
    }
```

Alternatively, a class-based approach groups related handlers:

```python
# Python — Class with handler methods
class PluginHandlers:
    """Grouped event handlers."""

    async def on_tool_execute(self, input_data: ToolInput, output_data: ToolOutput) -> None:
        """Handle tool.execute.before event."""
        ...

    async def on_chat_message(self, input_data: ChatMessageInput, output_data: ChatMessageOutput) -> None:
        """Handle chat.message event."""
        ...

    def as_dict(self) -> dict[str, Any]:
        """Return the hooks dict for the factory."""
        return {
            "tool.execute.before": self.on_tool_execute,
            "chat.message": self.on_chat_message,
        }


async def activate(ctx: PluginContext) -> dict[str, Any]:
    handlers = PluginHandlers()
    return handlers.as_dict()
```

### 1.4 Structural Comparison Summary

| TypeScript | Python |
|---|---|
| `Plugin` type from `@opencode-ai/plugin` | `Callable[[PluginContext], Awaitable[dict]]` or a `Protocol` |
| `async (ctx) => { return { ... }; }` | `async def activate(ctx: PluginContext) -> dict[str, Any]:` |
| Destructured `{ project, client, $, directory, worktree }` | `@dataclass PluginContext` with named fields |
| Hooks object with string keys | `dict[str, Callable]` with string keys |
| `import type { Plugin }` (type-only import) | `from typing import Protocol` for type-checking only |

## 2. Event Handler Signatures

### 2.1 The Input/Output Middleware Pattern

Every named event handler receives two parameters:

| Parameter | TypeScript | Python | Mutability |
|---|---|---|---|
| `input` | Read-only event info | Read-only dataclass/dict | Immutable (read) |
| `output` | Mutable response object | Mutable dataclass/dict | Mutable (write) |

This is the **Django request/response middleware pattern**:

```python
# Python — Django middleware analogy
def simple_middleware(get_response):
    def middleware(request):       # ← TypeScript "input" equivalent
        response = get_response(request)
        return response            # ← TypeScript "output" equivalent
    return middleware
```

The `input` carries what the event is about. The `output` is what you modify to change behavior.

### 2.2 `tool.execute.before`

```typescript
// TypeScript — Before any tool runs
"tool.execute.before": async (input, output) => {
  // input:  { tool: string, sessionID: string, callID: string }
  // output: { args: object } ← set properties to modify tool arguments

  if (input.tool === "read") {
    output.args.maxTokens = 1000;  // Override default
  }

  // Throw to block execution entirely
  if (input.tool === "bash" && output.args.command?.includes("rm -rf")) {
    throw new Error("Dangerous command blocked");
  }
}
```

```python
# Python — Equivalent pattern
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ToolBeforeInput:
    """Read-only event info for tool.execute.before."""
    tool: str
    session_id: str
    call_id: str

@dataclass
class ToolBeforeOutput:
    """Mutable output for tool.execute.before."""
    args: dict[str, Any] = field(default_factory=dict)


async def on_tool_execute_before(
    input_data: ToolBeforeInput,
    output_data: ToolBeforeOutput,
) -> None:
    """Handle tool.execute.before."""

    # Modify tool arguments
    if input_data.tool == "read":
        output_data.args["maxTokens"] = 1000

    # Raise to block execution
    if input_data.tool == "bash":
        command = output_data.args.get("command", "")
        if "rm -rf" in command:
            raise RuntimeError("Dangerous command blocked")
```

### 2.3 `chat.message`

```typescript
// TypeScript — Chat message event
"chat.message": async (input, output) => {
  // input:  { sessionID, agent?, model?, messageID?, variant? }
  // output: { message: UserMessage, parts: Part[] }

  output.parts.push({
    type: "text",
    text: "[Logged by my-plugin]",
  });
}
```

```python
# Python — Chat message handler
@dataclass
class ChatMessageInput:
    session_id: str
    agent: str | None = None
    model: dict[str, str] | None = None  # Actually { providerID, modelID } per SDK
    message_id: str | None = None
    variant: str | None = None

@dataclass
class ChatMessageOutput:
    message: dict[str, Any] = field(default_factory=dict)
    parts: list[dict[str, Any]] = field(default_factory=list)


async def on_chat_message(
    input_data: ChatMessageInput,
    output_data: ChatMessageOutput,
) -> None:
    """Handle chat.message event."""
    output_data.parts.append({
        "type": "text",
        "text": "[Logged by my-plugin]",
    })
```

### 2.4 `command.execute.before`

```typescript
// TypeScript — Before a shell command runs
"command.execute.before": async (input, output) => {
  // input:  { command: string, sessionID: string, arguments: string }
  // output: { parts: Part[] } ← modify to change the command; Part is from @opencode-ai/sdk

  // Rewrite the command
  output.parts = ["git", "log", "--oneline", "-5"];
}
```

```python
# Python — Command handler
@dataclass
class CommandBeforeInput:
    command: str
    session_id: str
    arguments: str

@dataclass
class CommandBeforeOutput:
    parts: list[str | dict[str, Any]] = field(default_factory=list)  # Part[] objects or string tokens; both work at runtime


async def on_command_execute_before(
    input_data: CommandBeforeInput,
    output_data: CommandBeforeOutput,
) -> None:
    """Handle command.execute.before event."""
    # Rewrite the command
    output_data.parts = ["git", "log", "--oneline", "-5"]
```

### 2.5 Wildcard vs Named Event Patterns

TypeScript supports both named handlers and a wildcard `event` handler:

```typescript
// TypeScript — Wildcard handler catches ALL events
return {
  event: async ({ event }) => {
    // event.type contains the event name
    if (event.type === "session.idle") {
      // React to idle events
    }
  },
};
```

```python
# Python — Wildcard receiver equivalent
async def on_any_event(event: dict[str, Any]) -> None:
    """Catch-all wildcard handler."""
    event_type = event.get("type", "")
    if event_type == "session.idle":
        # React to idle events
        ...


async def activate(ctx: PluginContext) -> dict[str, Any]:
    return {
        "event": on_any_event,
    }
```

The wildcard handler receives a single object with `event.type` identifying the event, plus `event.properties` for the payload.

### 2.6 Multiple Handlers for the Same Event

In TypeScript, multiple handlers can register under the same event key. OpenCode invokes all of them in registration order.

```python
# Python — Multiple handlers for the same event
from typing import Any


async def log_every_tool_call(input_data: Any, output_data: Any) -> None:
    """First handler: log every tool execution."""
    ...

async def block_dangerous_commands(input_data: Any, output_data: Any) -> None:
    """Second handler: block dangerous commands."""
    ...


# NOTE: The SDK Hooks type expects a single function per key, not an array.
# Use the compose pattern below. This array syntax is for illustration only.
async def activate_with_handlers(ctx: PluginContext) -> dict[str, Any]:
    """Illustration: returning an array of handlers for the same event key."""
    return {
        # Multiple handlers — both run, in this order
        "tool.execute.before": [
            log_every_tool_call,
            block_dangerous_commands,
        ],
    }
```

If the SDK expects a single callable per key, compose handlers explicitly:

```python
# Python — Composition pattern
from typing import Any, Callable, Awaitable


def compose(*handlers: Callable[..., Awaitable[None]]):
    """Compose multiple handlers into one."""
    async def combined(input_data, output_data) -> None:
        for handler in handlers:
            await handler(input_data, output_data)
    return combined


# Correct pattern: compose multiple handlers into one function.
async def activate(ctx: PluginContext) -> dict[str, Any]:
    """Preferred pattern: use compose to combine handlers per SDK type expectations."""
    return {
        "tool.execute.before": compose(
            log_every_tool_call,
            block_dangerous_commands,
        ),
    }
```

## 3. File-System Operations Mapping

The table below maps every common Node.js `fs` operation used in OpenCode plugins to its Python equivalent.

| Node.js `fs` (sync) | Node.js `fs.promises` | Python (`pathlib` / `os` / `shutil`) | Notes |
|---|---|---|---|
| `readFileSync(path, 'utf-8')` | `(await) readFile(path, 'utf-8')` | `Path(path).read_text()` | Returns `str` in both |
| `writeFileSync(path, content)` | `(await) writeFile(path, content)` | `Path(path).write_text(content)` | Creates file; fails if parent dir missing |
| `existsSync(path)` | `(await) access(path).then(...)` | `Path(path).exists()` | Also: `os.path.exists(path)` |
| `mkdirSync(path, {recursive: true})` | `(await) mkdir(path, {recursive: true})` | `os.makedirs(path, exist_ok=True)` | Both suppress "already exists" errors |
| `copyFileSync(src, dest)` | `(await) copyFile(src, dest)` | `shutil.copy2(src, dest)` | Preserves metadata in Python |
| `cpSync(src, dest, {recursive: true})` | `(await) cp(src, dest, {recursive: true})` | `shutil.copytree(src, dest, dirs_exist_ok=True)` | Python 3.8+: `dirs_exist_ok` |
| `readdirSync(path)` | `(await) readdir(path)` | `os.listdir(path)` | Returns list of filename strings |
| `rmSync(path, {recursive: true})` | `(await) rm(path, {recursive: true})` | `shutil.rmtree(path)` | Deletes directory tree |
| `unlinkSync(path)` | `(await) unlink(path)` | `Path(path).unlink()` | Deletes a single file |
| `statSync(path)` | `(await) stat(path)` | `Path(path).stat()` | Returns file metadata |
| `renameSync(old, new)` | `(await) rename(old, new)` | `Path(old).rename(new)` | Move/rename file |
| `appendFileSync(path, data)` | `(await) appendFile(path, data)` | `with open(path, 'a') as f: f.write(data)` | Append to existing file |

### Async File I/O Patterns

For non-blocking file operations inside the factory or event handlers, Python offers several strategies:

```python
# Python — Option 1: asyncio.to_thread (stdlib, Python 3.9+)
import asyncio
from pathlib import Path


async def read_file_async(path: str) -> str:
    """Read a file without blocking the event loop."""
    return await asyncio.to_thread(Path(path).read_text)


async def write_file_async(path: str, content: str) -> None:
    """Write a file without blocking the event loop."""
    await asyncio.to_thread(Path(path).write_text, content)
```

```python
# Python — Option 2: aiofiles (third-party, requires pip install aiofiles)
import aiofiles


async def read_file_aio(path: str) -> str:
    """Read a file using aiofiles."""
    async with aiofiles.open(path, mode="r") as f:
        return await f.read()


async def write_file_aio(path: str, content: str) -> None:
    """Write a file using aiofiles."""
    async with aiofiles.open(path, mode="w") as f:
        await f.write(content)
```

| Strategy | Pros | Cons |
|---|---|---|
| `asyncio.to_thread` | No extra dependencies; stdlib only | Thread-pool overhead for tiny files |
| `aiofiles` | True async I/O; no thread pool | Requires `pip install aiofiles` |
| Sync in factory | Simple; fine for small files | Blocks event loop during startup |

**Pattern recommendation:** Use synchronous `Path` operations inside the init factory (it runs once at startup, blocking is acceptable). Use `asyncio.to_thread` or `aiofiles` inside event handlers that may fire frequently.

## 4. Error Handling Patterns

### 4.1 Try/Catch vs Try/Except

```typescript
// TypeScript — Try/catch with structured logging
try {
  const data = readFileSync(somePath, "utf-8");
  // Process data...
} catch (error) {
  console.warn(`Could not read ${somePath}:`, error);
}
```

```python
# Python — Try/except with logging
import logging

logger = logging.getLogger("my-plugin")

try:
    data = Path(some_path).read_text()
    # Process data...
except OSError as error:
    logger.warning("Could not read %s: %s", some_path, error)
```

### 4.2 Unhandled Promise Rejections vs Unhandled Async Exceptions

```typescript
// TypeScript — BAD: unhandled promise rejection
export const BadPlugin = async ({ $ }) => {
  const { stdout } = await $`which missing-tool`;  // Rejects if not found
  return {};
};

// GOOD: catch safely
export const SafePlugin = async ({ $ }) => {
  const result = await $`which missing-tool`.nothrow();
  return {};
};
```

```python
# Python — BAD: unhandled async exception
async def bad_activate(ctx):
    result = await run_shell("which missing-tool")  # Raises if not found
    return {}

# GOOD: try/except wraps the await
async def safe_activate(ctx):
    try:
        result = await run_shell("which missing-tool")
    except Exception:
        result = None  # Graceful degradation
    return {}
```

### 4.3 Structured Logging

```typescript
// TypeScript — Structured logging via SDK client
await client.app.log({
  body: {
    service: "my-plugin",
    level: "info",
    message: "Plugin initialized successfully",
    extra: { startupTime: new Date().toISOString() },
  },
});

// Fallback: console.warn
console.warn("Deprecated API call detected");
```

```python
# Python — Logging via stdlib logging module
import logging

logger = logging.getLogger("my-plugin")

# Level mapping:
# client.app.log({level: "debug"})   → logger.debug(...)
# client.app.log({level: "info"})    → logger.info(...)
# client.app.log({level: "warn"})    → logger.warning(...)
# client.app.log({level: "error"})   → logger.error(...)

logger.info("Plugin initialized successfully", extra={
    "startupTime": "2026-06-08T00:00:00Z",
})

# Fallback: logging.warning
logging.warning("Deprecated API call detected")
```

| `client.app.log` level | Python logging level |
|---|---|
| `debug` | `logging.DEBUG` |
| `info` | `logging.INFO` |
| `warn` | `logging.WARNING` |
| `error` | `logging.ERROR` |

### 4.4 Fail-Open Philosophy

**Rule:** Factory errors should never crash the OpenCode host. The host catches exceptions from the factory, logs them, and continues without the plugin.

```python
# Python — Wrapping the entire factory in try/except

async def activate(ctx: PluginContext) -> dict[str, Any]:
    """Safe factory with fail-open behavior."""
    try:
        # Perform all startup checks
        await perform_startup_checks(ctx)
    except Exception as error:
        # Log the failure but return empty hooks — plugin is inert
        logging.getLogger("my-plugin").error(
            "Plugin init failed: %s", error, exc_info=True,
        )
        return {}  # Empty hooks = no-op plugin

    # Only reached if startup succeeded
    return {
        "tool.execute.before": on_tool_execute,
    }


async def perform_startup_checks(ctx: PluginContext) -> None:
    """Run all startup checks. Any exception here degrades gracefully."""
    # Check CLI dependencies
    # Check file system state
    # Verify configuration
    pass
```

### 4.5 Graceful Degradation with Feature Toggles

```python
# Python — Feature toggles for graceful degradation
from dataclasses import dataclass, field


@dataclass
class PluginFeatures:
    """Runtime feature flags."""
    gh_available: bool = False
    network_available: bool = False
    all_features: bool = True


# Module-level feature flags, populated at startup by the activate factory
plugin_features: PluginFeatures = PluginFeatures()


async def detect_features(ctx: PluginContext) -> PluginFeatures:
    """Detect which features are available."""
    features = PluginFeatures()

    try:
        # Check for gh CLI
        import subprocess
        result = subprocess.run(
            ["which", "gh"],
            capture_output=True,
            text=True,
        )
        features.gh_available = result.returncode == 0
    except Exception:
        features.gh_available = False

    try:
        # Check network connectivity
        result = subprocess.run(
            ["ping", "-c", "1", "example.com"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        features.network_available = result.returncode == 0
    except Exception:
        features.network_available = False

    # All features check
    features.all_features = all([
        features.gh_available,
        features.network_available,
    ])

    return features


# In your activate() factory, call detect_features and store the result:
#
#   async def activate(ctx: PluginContext) -> dict[str, Any]:
#       global plugin_features
#       plugin_features = await detect_features(ctx)
#       return {"tool.execute.before": on_gh_dependent_tool}
#


async def on_gh_dependent_tool(input_data, output_data) -> None:
    """Handler that depends on gh CLI."""
    # plugin_features is populated at module level by the activate factory
    if not plugin_features.gh_available:
        raise RuntimeError(
            "GitHub CLI (gh) is required for this feature. "
            "Install it with: brew install gh"
        )
    # ... handler logic ...
```

### 4.6 Error Handling Comparison Summary

| TypeScript | Python | Purpose |
|---|---|---|
| `try { ... } catch (e) { ... }` | `try: ... except Exception as e: ...` | Catch and handle errors |
| `promise.catch(...)` | `await` wrapped in `try/except` | Catch async rejections |
| `client.app.log({body: {level, message}})` | `logger.info(...)` / `logger.error(...)` | Structured logging |
| `console.warn(...)` | `logging.warning(...)` | Warning output |
| `.catch(() => fallback)` | `except: fallback` | Safe rejection handling |
| `return {}` on failure | `return {}` on exception | Fail-open: empty hooks |

## 5. Bun `$` Shell vs Python subprocess

### 5.1 Basic Command Execution

```typescript
// TypeScript — Bun's tagged template literal shell API
const branch = (await $`git rev-parse --abbrev-ref HEAD`.text()).trim();
```

```python
# Python — Equivalent with subprocess.run
import subprocess

result = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    capture_output=True,
    text=True,
)
branch = result.stdout.strip()
exit_code = result.returncode
stderr = result.stderr
```

### 5.2 Return Value Comparison

| Bun `$` return shape | `subprocess.CompletedProcess` | Notes |
|---|---|---|
| `{ stdout: Buffer }` | `.stdout` | Raw stdout as Buffer (Uint8Array); use `.text()` for string |
| `{ stderr: Buffer }` | `.stderr` | Raw stderr as Buffer (Uint8Array); use `.text()` for string |
| `{ exitCode: number }` (with `.nothrow()`) | `.returncode` | Exit code — available without catching with `.nothrow()`; also on `ShellError` when caught |

### 5.3 Auto-Escaping vs Injection Prevention

```typescript
// TypeScript — Auto-escaping: Bun escapes interpolated values
const userInput = "'; rm -rf /; echo '";
const { stdout } = await $`echo ${userInput}`;
// Bun escapes userInput automatically — safe even with special chars
```

```python
# Python — Using list form prevents injection
import subprocess

user_input = "'; rm -rf /; echo '"
result = subprocess.run(
    ["echo", user_input],  # List form = no shell injection
    capture_output=True,
    text=True,
)

# BAD: shell=True with string interpolation — vulnerable to injection
# result = subprocess.run(f"echo {user_input}", shell=True, capture_output=True, text=True)
```

**Rule:** Always use the list form (`["command", "arg1", "arg2"]`) in Python. This is equivalent to Bun's auto-escaping. Never use `shell=True` with string interpolation from untrusted input.

### 5.4 Pipe Support

```typescript
// TypeScript — Bun $ supports pipes natively
const { stdout } = await $`git log --oneline | head -5`;
```

```python
# Python — subprocess.Popen chaining for pipes
import subprocess

p1 = subprocess.Popen(
    ["git", "log", "--oneline"],
    stdout=subprocess.PIPE,
    text=True,
)
p2 = subprocess.Popen(
    ["head", "-5"],
    stdin=p1.stdout,
    stdout=subprocess.PIPE,
    text=True,
)
p1.stdout.close()  # Allow p1 to receive SIGPIPE if p2 exits
stdout, _ = p2.communicate()
```

```python
# Python — Alternative: subprocess.run with shell=True for simple pipes
result = subprocess.run(
    "git log --oneline | head -5",
    shell=True,  # Acceptable for hardcoded piped commands
    capture_output=True,
    text=True,
)
```

For simple piped commands, `shell=True` with a hardcoded string is acceptable. For any command involving user input, always use `Popen` chaining with list forms.

### 5.5 Catch for Safe Rejection Handling

```typescript
// TypeScript — .nothrow() prevents unhandled rejections
const result = await $`which gh`.nothrow();

if (result.exitCode !== 0) {
  // Gracefully handle missing tool
}
```

```python
# Python — try/except around subprocess.run
import subprocess

try:
    result = subprocess.run(
        ["which", "gh"],
        capture_output=True,
        text=True,
    )
except FileNotFoundError:
    # which itself is not found (unusual but possible)
    result = subprocess.CompletedProcess(
        args=["which", "gh"],
        returncode=1,
        stdout="",
        stderr="gh not found",
    )

if result.returncode != 0:
    # Gracefully handle missing tool
    ...
```

### 5.6 `subprocess` Error Handling Summary

```python
# Python — Common subprocess error patterns

import subprocess
import logging

logger = logging.getLogger("my-plugin")


async def run_shell_safe(
    cmd: list[str],
    timeout: float | None = None,
) -> subprocess.CompletedProcess:
    """Run a shell command safely with graceful error handling."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result
    except FileNotFoundError:
        logger.warning("Command not found: %s", cmd[0])
        return subprocess.CompletedProcess(
            args=cmd, returncode=127, stdout="", stderr="Command not found",
        )
    except subprocess.TimeoutExpired:
        logger.warning("Command timed out after %ss: %s", timeout, cmd)
        return subprocess.CompletedProcess(
            args=cmd, returncode=124, stdout="", stderr="Timed out",
        )
    except Exception as error:
        logger.error("Unexpected error running %s: %s", cmd, error)
        return subprocess.CompletedProcess(
            args=cmd, returncode=1, stdout="", stderr=str(error),
        )
```

### 5.7 Complete Example — Dependency Check

```typescript
// TypeScript — Using Bun $ for dependency checks
export const MyPlugin = async ({ $, client }) => {
  const { exitCode } = await $`which gh`.nothrow();

  if (exitCode !== 0) {
    await client.app.log({
      body: {
        service: "my-plugin",
        level: "warn",
        message: "GitHub CLI not found — some features disabled",
      },
    });
  }

  return {
    "tool.execute.before": async (input, output) => {
      // ...
    },
  };
};
```

```python
# Python — Equivalent dependency check
import logging
import subprocess

logger = logging.getLogger("my-plugin")


async def activate(ctx: PluginContext) -> dict[str, Any]:
    """Plugin factory with dependency check."""

    # Check for gh CLI
    gh_available = False
    try:
        result = subprocess.run(
            ["which", "gh"],
            capture_output=True,
            text=True,
        )
        gh_available = result.returncode == 0
    except Exception:
        gh_available = False

    if not gh_available:
        logger.warning("GitHub CLI not found — some features disabled")

    return {
        "tool.execute.before": on_tool_execute,
    }
```

## 6. Cross-Reference Index

This note is part of the OpenCode Plugins knowledge cluster. Related notes:

| Note | What it covers | How this note relates |
|---|---|---|
| [Init Hook Lifecycle](../init-hook-lifecycle.md) | Factory function, context object, version stamping, error handling patterns | **Complement** — that note covers init-hook-specific Python analogies. This note covers the entire SDK API beyond the init hook. |
| [Plugin Creation](../creation.md) | Plugin structure, TypeScript support, dependencies, configuration | **Prerequisite** — understand basic plugin structure before mapping to Python. |
| [Event System](../event-system.md) | All event types: installation, LSP, messages, server, todo via SSE | **Reference** — event details this note does not duplicate. |
| [Event Patterns](../event-patterns.md) | Named handlers, wildcard handlers, and event composition | **Reference** — handler pattern details. |
| [Event Chat](../event-chat.md) | `chat.message`, `chat.params`, `chat.headers` event details | **Reference** — chat-specific event details. |
| [Event Tool](../event-tool.md) | `tool.execute.before`, `tool.execute.after`, `tool.definition` event details | **Reference** — tool-specific event details. |
| [Event Command](../event-command.md) | `command.execute.before` event details | **Reference** — command-specific event details. |

## References

- [OpenCode Plugins Documentation](https://opencode.ai/docs/plugins) — Official OpenCode plugin documentation
- [`@opencode-ai/plugin` on npm](https://www.npmjs.com/package/@opencode-ai/plugin) — npm package for the plugin SDK
- [asyncio — Python Documentation](https://docs.python.org/3/library/asyncio.html) — Python async I/O standard library
- [pathlib — Python Documentation](https://docs.python.org/3/library/pathlib.html) — Python object-oriented file system paths
- [subprocess — Python Documentation](https://docs.python.org/3/library/subprocess.html) — Python subprocess management
- [Bun Shell API](https://bun.sh/docs/runtime/shell) — Bun's built-in shell API (`$`)
