---
title: "Plugin Init Hook Lifecycle"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - plugins
  - lifecycle
  - init
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-08
---

# Plugin Init Hook Lifecycle

The plugin init hook — the factory function exported from a plugin module — is OpenCode's equivalent of a startup routine: it runs every time OpenCode loads the plugin (which is every startup, not just on install). Think of it as a cross between Python's `__init__.py` module-level code (runs on import), Django's `AppConfig.ready()` (runs when the app is fully loaded), and a `setup.py` install hook (runs to provision resources). The factory receives a context object with everything needed to inspect the project, run shell commands, make API calls, and register event handlers. This note breaks down every aspect of that lifecycle so Python developers can map it to familiar mental models.

## 1. When the Factory Runs — Every Startup, Not Once

The most important thing to understand: **the factory function executes on every OpenCode startup**, not just when the plugin is first installed.

```typescript
// This function runs on EVERY OpenCode startup, like Python's __init__.py
export const MyPlugin = async ({ project, client, $, directory, worktree }) => {
  // -- Startup code here --
  console.log("Plugin loaded for project:", project.name);
  return {
    // Event handlers registered here
  };
};
```

**Line-by-line explanation:**

| Line | What it does | Python analogy |
|---|---|---|
| `export const MyPlugin = async (...) => {` | Exports the plugin factory as a named export. OpenCode imports the module and calls this function. | `def setup(app):` in a Django AppConfig — Django calls your `ready()` method. |
| `{ project, client, $, directory, worktree }` | Destructures the context object that OpenCode passes in. These five properties give you everything you need. | The `**kwargs` a framework passes to your callback. |
| `console.log(...)` | Runs on every startup. You can read files, check versions, copy assets, etc., here. | Code at module level in `__init__.py` — runs when Python imports the package. |
| `return { ... }` | Returns a hooks object. Event handlers are registered here, not inline. | Returning a dict of callbacks, like Flask `before_request` / `after_request` registration. |

**Key mental model:** The factory function is **re-entrant**. OpenCode calls it every time the program starts, not once in a lifetime. Side effects (like copying files) must account for repeated execution — check if work is already done before doing it again.

### Why Not Just Once?

| Approach | Behavior | Problem |
|---|---|---|
| One-time install script | Runs only when `npm install` or `bun install` executes. | Files can be deleted, versions can drift, users can switch projects. |
| Factory on every startup | Runs every time. Can check state, repair, or update. | Must be idempotent — safe to call repeatedly. |

The factory-on-every-startup pattern is safer: the plugin can self-heal if a user deletes a copied file, or can auto-update agent definitions when the plugin is bumped to a new version. The tradeoff is you must write idempotent code.

## 2. The Context Object — The Five Properties

OpenCode passes a single context object with five properties. Here is each one, with a Python developer analogy and a concrete use case.

### `project`

```typescript
// Type signature (conceptual)
interface ProjectInfo {
  name: string;       // project name from opencode.json or directory name
  path: string;       // absolute path to project root
  config: object;     // parsed opencode.json contents
}
```

| Property | What it holds | Python analogy |
|---|---|---|
| `project.name` | The project display name. Used for logging or tagging. | `settings.PROJECT_NAME` in Django |
| `project.path` | Absolute filesystem path to the project root (where `opencode.json` lives). | `os.path.dirname(__file__)` in a Django settings module |
| `project.config` | The full parsed `opencode.json` as an object. Lets you inspect what agents, plugins, and tools are registered. | `django.conf.settings` — the entire parsed configuration |

**Typical usage:** Read project name for log messages, use `project.path` as the base for constructing paths to `.opencode/agents/` or `.opencode/skills/`.

### `client`

```typescript
// The OpenCode SDK client — your API gateway
const result = await client.app.log({
  body: { service: "my-plugin", level: "info", message: "Plugin started" },
});
```

The `client` object is an instance of the OpenCode SDK client. It provides methods for:

| Method | Use case | Python analogy |
|---|---|---|
| `client.app.log(...)` | Structured logging (levels: debug, info, warn, error) | `logging.getLogger(__name__).info(...)` |
| `client.app.chat(...)` | Send messages into the active chat session | An AI agent posting to a Slack channel |
| `client.app.tool(...)` | Invoke tools programmatically (not just from AI) | Calling a Celery task synchronously |

Unlike Python's `print()`, `client.app.log()` produces structured entries that show up in OpenCode's internal logs and UI. Always prefer it over `console.log` in production plugins.

### `$` — Bun's Shell API

```typescript
// Run any shell command — like Python's subprocess but with template literals
const branch = (await $`git rev-parse --abbrev-ref HEAD`.text()).trim();
```

| Aspect | Description | Python analogy |
|---|---|---|
| Syntax | Tagged template literal: `` $`command` `` — Bun parses it, handles escaping automatically | `subprocess.run(["command"], capture_output=True, text=True)` |
| Security | **Auto-escapes** interpolated values. `` $`echo ${userInput}` `` escapes `userInput` to prevent shell injection. | Passing a list to `subprocess.run` instead of a string with `shell=True` |
| Return value | `{ stdout, stderr, exitCode }` — always available | `subprocess.CompletedProcess` with `.stdout`, `.stderr`, `.returncode` |
| Pipe support | `` await $`cmd1 \| cmd2` `` — pipes work naturally within the template literal | `p1 = subprocess.Popen(...); p2 = subprocess.Popen(...)` manual piping |

**Why `$` exists:** Python developers typically reach for `os.system()`, `subprocess.run()`, or `sh` library. The `$` API is Bun's built-in shell — it ships with the runtime, requires no imports, and is designed for async/await from the ground up.

**Warning:** `$` is **not** Bash. It's Bun's lightweight shell parser. It supports common syntax (`|`, `&&`, `>`, `<`, `$(...)`) but not Bash-specific features like brace expansion or process substitution. Keep commands simple.

### `directory`

```typescript
const cwd = directory; // Current working directory — same as process.cwd()
```

| Value | Meaning | Python analogy |
|---|---|---|
| `directory` | The current working directory when OpenCode was launched | `os.getcwd()` |
| Not the plugin directory | This is the **user's project** directory, not where the plugin is installed | Not `/path/to/venv/lib/...` — it's the project root |

**Typical usage:** `directory` is often interchangeable with `project.path` but can differ if OpenCode is launched from a subdirectory. Use `project.path` for project-root decisions; use `directory` for relative paths the user intended.

### `worktree`

```typescript
const wt = worktree; // e.g., "/path/to/project-main" or undefined if not in a worktree
```

| Value | Meaning | Python analogy |
|---|---|---|
| `worktree` | The git worktree path (if OpenCode was launched from a `git worktree` checkout) | `None` or a path — think of a `git worktree` as a Python virtual env for branches |
| `undefined` | If not in a worktree, this is `undefined` (not `null`) | Not applicable — always check with `if (worktree)` |

**Why this matters:** In a `git worktree`, the actual git directory is separate from the working tree. The `worktree` property tells plugins where the current branch's working files live. Use it when you need to resolve git-aware paths.

## 3. What You Can Do in the Factory — It's an Async Sandbox

Because the factory is `async`, you can `await` any async operation. Here is what you can do, with Python analogies for each:

### Read and Write Files

```typescript
import { readFileSync, existsSync, mkdirSync, copyFileSync } from "fs";
import { join } from "path";

export const MyPlugin = async ({ project, client }) => {
  const agentsDir = join(project.path, ".opencode", "agents");
  const stampFile = join(project.path, ".opencode", ".plugin-stamp");

  // Read existing stamp
  if (existsSync(stampFile)) {
    const previousVersion = readFileSync(stampFile, "utf-8").trim();
    client.app.log({ body: { level: "info", message: `Previous version: ${previousVersion}` } });
  }

  // mkdir + copy files — idempotent
  mkdirSync(agentsDir, { recursive: true });
  // ... copy files ...
};
```

| Operation | Bun Node.js API | Python equivalent |
|---|---|---|
| Check file exists | `existsSync(path)` | `os.path.exists(path)` |
| Create directory | `mkdirSync(path, { recursive: true })` | `os.makedirs(path, exist_ok=True)` |
| Read file | `readFileSync(path, "utf-8")` | `open(path).read()` |
| Copy file | `copyFileSync(src, dest)` | `shutil.copy2(src, dest)` |

File I/O in the factory is **synchronous** (`*Sync` functions) in most examples because you typically want the copy complete before event handlers are registered. If you need async I/O, you can use `fs.promises` — just `await` it before the `return` statement.

### Check Versions (Version Stamping)

```typescript
import { readFileSync, writeFileSync, existsSync } from "fs";
import { join } from "path";

export const MyPlugin = async ({ project, client }) => {
  const stampFile = join(project.path, ".opencode", ".runesmith-version");
  const currentVersion = "1.2.0"; // Would come from package.json at build time

  if (existsSync(stampFile)) {
    const stampedVersion = readFileSync(stampFile, "utf-8").trim();
    if (stampedVersion === currentVersion) {
      client.app.log({ body: { level: "info", message: "Plugin up-to-date" } });
      // Skip re-copy — already on the right version
    } else {
      client.app.log({ body: { level: "info", message: `Upgrading from ${stampedVersion} to ${currentVersion}` } });
      // Re-copy agents and skills
    }
  } else {
    client.app.log({ body: { level: "info", message: "First run — installing agents and skills" } });
    // First-time copy
  }

  // Write/update the stamp
  writeFileSync(stampFile, currentVersion);
};
```

This is the **version-stamping pattern** referenced in [Bundling Components](bundling-components.md). It solves the update-propagation problem: by comparing the on-disk stamp against the bundled plugin version on every startup, the plugin knows when to re-copy files.

**Python analogy:** Think of this like a Django data migration version table (`django_migrations` table). Django checks which migrations have been applied on every startup and runs any that are missing. The stamp file serves the same purpose — it records what version of assets has been deployed to the project's `.opencode/` directory.

### Run Shell Commands via `$`

```typescript
export const MyPlugin = async ({ $, client }) => {
  // Check if a required CLI tool is installed
  const { exitCode } = await $`which gh`.catch(() => ({ exitCode: 1 }));
  if (exitCode !== 0) {
    client.app.log({
      body: { level: "warn", message: "GitHub CLI (gh) not found — some features disabled" },
    });
    // Plugin continues to load; features that need `gh` will fail gracefully later
  }
};
```

**Python analogy:** This is like calling `subprocess.run(["which", "gh"])` in a Django `AppConfig.ready()` to check if a system dependency is available. The plugin degrades gracefully rather than crashing.

### Make API Calls via `client`

```typescript
export const MyPlugin = async ({ client }) => {
  // Log structured startup info
  await client.app.log({
    body: {
      service: "runesmith",
      level: "info",
      message: "RuneSmith plugin starting",
      extra: { startupTime: new Date().toISOString() },
    },
  });
};
```

The `client` calls are already async — you `await` them. Unlike `console.log()`, these structured entries are visible in OpenCode's UI and log infrastructure.

## 4. The Return Value — The Hooks Object

The factory's return value is a **hooks object** — a plain object whose keys are event names and whose values are async handler functions.

```typescript
export const MyPlugin = async (ctx) => {
  // -- Init logic (runs once at startup) --

  return {
    // -- Event handlers (registered for the lifetime of the session) --

    // Hook into tool execution
    "tool.execute.before": async (input, output) => {
      // input: the tool being called and its arguments
      // output: mutable — modify args before execution
      if (input.tool === "read" && output.args.filePath?.includes(".env")) {
        throw new Error("Reading .env files is not allowed");
      }
    },

    // Hook into session creation
    "session.created": async (input, output) => {
      // input: session metadata (id, type, agent, etc.)
      // output: mutable — modify session configuration
      client.app.log({ body: { level: "info", message: `Session ${input.id} created` } });
    },

    // Register custom tools
    tool: {
      "runesmith-analyze": tool({
        description: "Analyze the RuneSmith project structure",
        args: { path: tool.schema.string() },
        execute: async (args, context) => {
          return `Analyzed ${args.path}`;
        },
      }),
    },
  };
};
```

**Line-by-line explanation:**

| Hook key | When it fires | Python analogy |
|---|---|---|
| `"tool.execute.before"` | Before an AI agent calls any tool (read, write, bash, etc.) | A `@receiver(pre_save)` Django signal that fires before a model save |
| `"session.created"` | When a new AI session starts (e.g., a new chat) | Django `request_started` signal |
| `tool` | A special object, not a string key — registers custom tool definitions | Registering a custom management command in `AppConfig.ready()` via `call_command` |

### The `input` / `output` Pattern

Every event handler receives two parameters:

- **`input`** — Read-only information about the event (the tool name, the session ID, the chat message, etc.).
- **`output`** — A mutable object you can modify. Changes to `output` affect the behavior of the tool or session.

```typescript
// Modify tool arguments before execution
"tool.execute.before": async (input, output) => {
  output.args.timeout = 30_000; // Override the default timeout
}
```

**Python analogy:** This is Django's `request` / `response` middleware pattern. The `input` is like `HttpRequest` (you read from it), and `output` is like `HttpResponse` (you write to it). Modifying `output` changes what happens next.

## 5. Complete Worked Example — RuneSmith Init Hook

Here is a complete init hook for `@runicengines/opencode-runesmith`. It bundles every concept from this note into a single, real-world example.

```typescript
// dist/index.ts — Entry point for @runicengines/opencode-runesmith
import { readFileSync, writeFileSync, existsSync, mkdirSync, cpSync, readdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import type { Plugin } from "@opencode-ai/plugin";

const __dirname = dirname(fileURLToPath(import.meta.url));

// This version is set at build time by the CI pipeline
const PLUGIN_VERSION = "1.2.0";

export const RuneSmithPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  // -----------------------------------------------------------------------
  // Step 1: Version stamp check — decide what needs updating
  // -----------------------------------------------------------------------
  const stampFile = join(project.path, ".opencode", ".runesmith-version");
  let needsUpdate = false;

  if (existsSync(stampFile)) {
    const stampedVersion = readFileSync(stampFile, "utf-8").trim();
    if (stampedVersion !== PLUGIN_VERSION) {
      needsUpdate = true;
      await client.app.log({
        body: {
          service: "runesmith",
          level: "info",
          message: `Version changed: ${stampedVersion} → ${PLUGIN_VERSION}. Re-copying assets.`,
        },
      });
    } else {
      await client.app.log({
        body: { service: "runesmith", level: "debug", message: "Plugin up-to-date — skipping copy." },
      });
    }
  } else {
    needsUpdate = true;
    await client.app.log({
      body: { service: "runesmith", level: "info", message: "First run — installing RuneSmith assets." },
    });
  }

  // -----------------------------------------------------------------------
  // Step 2: Copy agents and skills if needed (first run or version change)
  // -----------------------------------------------------------------------
  if (needsUpdate) {
    // --- Agents ---
    const bundledAgentsDir = join(__dirname, "..", ".opencode", "agents");
    const projectAgentsDir = join(project.path, ".opencode", "agents");

    if (existsSync(bundledAgentsDir)) {
      mkdirSync(projectAgentsDir, { recursive: true });
      for (const file of readdirSync(bundledAgentsDir)) {
        if (file.endsWith(".md")) {
          const src = join(bundledAgentsDir, file);
          const dest = join(projectAgentsDir, file);
          // Overwrite on update (version changed); skip on first run if already there
          cpSync(src, dest, { force: true });
        }
      }
      await client.app.log({
        body: { service: "runesmith", level: "info", message: "Agent definitions copied." },
      });
    }

    // --- Skills ---
    const bundledSkillsDir = join(__dirname, "..", ".opencode", "skills");
    const projectSkillsDir = join(project.path, ".opencode", "skills");

    if (existsSync(bundledSkillsDir)) {
      mkdirSync(projectSkillsDir, { recursive: true });
      for (const skillDir of readdirSync(bundledSkillsDir)) {
        const src = join(bundledSkillsDir, skillDir);
        const dest = join(projectSkillsDir, skillDir);
        cpSync(src, dest, { recursive: true, force: true });
      }
      await client.app.log({
        body: { service: "runesmith", level: "info", message: "Skill directories copied." },
      });
    }

    // --- Write the version stamp ---
    writeFileSync(stampFile, PLUGIN_VERSION);
  }

  // -----------------------------------------------------------------------
  // Step 3: Optional — check for CLI dependencies using Bun's shell
  // -----------------------------------------------------------------------
  const { exitCode: ghExitCode } = await $`which gh`.catch(() => ({ exitCode: 1 }));
  if (ghExitCode !== 0) {
    await client.app.log({
      body: {
        service: "runesmith",
        level: "warn",
        message: "GitHub CLI (gh) not found. RuneSmith GitHub tools will be unavailable.",
      },
    });
  }

  // -----------------------------------------------------------------------
  // Step 4: Return event hooks — these run for the lifetime of the session
  // -----------------------------------------------------------------------
  return {
    // --- Log every tool execution and block dangerous commands ---
    "tool.execute.before": async (input, output) => {
      // Log first
      await client.app.log({
        body: {
          service: "runesmith",
          level: "debug",
          message: `Tool called: ${input.tool}`,
          extra: { args: output.args },
        },
      });

      // Then block dangerous shell commands
      if (input.tool === "bash" && typeof output.args.command === "string") {
        const blocked = ["rm -rf /", "sudo ", "> /dev/sda"];
        for (const pattern of blocked) {
          if (output.args.command.includes(pattern)) {
            throw new Error(`Blocked dangerous command pattern: ${pattern}`);
          }
        }
      }
    },
  };
};
```

**Line-by-line walkthrough of the critical sections:**

| Lines | What's happening | Why it matters |
|---|---|---|
| `const PLUGIN_VERSION = "1.2.0"` | Hardcoded version constant. In production, this would be injected at build time (e.g., from `package.json` via `esbuild --define`). | Without a build-time version, you risk forgetting to bump this string. |
| `const stampFile = join(project.path, ".opencode", ".runesmith-version")` | The stamp lives in `.opencode/` — the same directory OpenCode uses for agents, skills, and tools. Hidden file (dot prefix) because it's a machine artifact, not user content. | Following OpenCode's existing conventions. |
| `if (stampedVersion !== PLUGIN_VERSION)` | String comparison of the previous stamped version vs the current bundled version. | Simple and reliable. Works even if someone deleted and re-created the stamp file. |
| `cpSync(src, dest, { force: true })` | `force: true` means "overwrite if exists." On version change, we always overwrite. On first run, it overwrites nothing because the file doesn't exist yet. | Prevents leaving stale agent/skill definitions when the plugin upgrades. |
| `await $`which gh`.catch(...)` | Shell command wrapped in `.catch()` to prevent unhandled rejections. | **Crucial** — an uncaught promise rejection in the factory can crash the entire plugin load. |
| `return { "tool.execute.before": async ... }` | Two handlers for the same event name. OpenCode invokes **both** in registration order. | Think of it like Django signals: multiple receivers can subscribe to the same signal. |

### Why `cpSync` with `force: true` on Every Update?

| Scenario | Before `cpSync` | After `cpSync` |
|---|---|---|
| First run | File doesn't exist → created | Plugin assets are available |
| No version change (stamp matched) | Factory returns early — `needsUpdate` is `false` | Nothing is copied; stamp not written (already correct) |
| Version changed | `cpSync` with `force: true` overwrites old agent/skill files | Updated definitions in place |
| User deleted a copied file | Version stamp still exists, matches → skip copy | **Gap:** The file is gone but stamp says it's fine |

The last row reveals a limitation: the version stamp only detects version changes, not file deletions. If you need self-healing, check for specific file existence rather than relying solely on the stamp.

```typescript
// Self-healing: check if the target file actually exists
if (!existsSync(targetFile)) {
  needsUpdate = true;
}
```

## 6. Error Handling Patterns — Design for Fail-Open

**Golden rule:** OpenCode logs the error but continues without the plugin if the factory throws or returns a rejected promise. Your plugin should degrade gracefully, not crash the host.

### Pattern A: Guard Everything with Try/Catch

```typescript
export const SafePlugin = async ({ client }) => {
  try {
    // Risky operation — file copy, shell command, network call
    await $`which gh`;
  } catch (error) {
    await client.app.log({
      body: { service: "my-plugin", level: "error", message: `Init failed: ${error.message}` },
    });
    // Return an empty hooks object — plugin is a no-op but OpenCode continues
    return {};
  }

  return {
    "tool.execute.before": async (input, output) => {
      // This only runs if init succeeded
    },
  };
};
```

**Python analogy:** This is like a Django startup check that logs a warning but doesn't prevent `runserver` from starting. The app runs, but the faulty feature is disabled.

### Pattern B: Graceful Feature Toggle

```typescript
export const TogglePlugin = async ({ $, client }) => {
  let ghAvailable = false;

  try {
    const { exitCode } = await $`which gh`;
    ghAvailable = exitCode === 0;
  } catch {
    ghAvailable = false;
  }

  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "runesmith-publish" && !ghAvailable) {
        throw new Error("GitHub CLI is required for publishing. Install it with: brew install gh");
      }
    },
  };
};
```

This pattern lets the plugin load fully even when a dependency is missing. Individual features check their own preconditions and provide clear error messages.

### Pattern C: Return an Empty Hooks Object

```typescript
export const DegradeGracefully = async ({ client }) => {
  try {
    await expensiveInit();
  } catch (error) {
    await client.app.log({
      body: { service: "my-plugin", level: "error", message: `Init failed: ${error.message}` },
    });
    return {}; // No hooks registered — plugin is inert but OpenCode works fine
  }

  return { /* hooks */ };
};
```

### What NOT to Do

```typescript
// BAD: Unhandled promise rejection
export const BadPlugin = async () => {
  await $`which missing-tool`; // No .catch() — this rejects and crashes the factory
  return { /* never reached */ };
};

// BAD: Synchronous throw outside try/catch
export const WorsePlugin = async () => {
  throw new Error("Kaboom"); // Unhandled sync throw in an async function
  return {};
};
```

| What happens | Error behavior |
|---|---|
| Sync throw in factory | OpenCode catches it, logs, and skips the plugin entirely. |
| Async rejection (unhandled) | Depending on the runtime, this could be an unhandled promise rejection warning. Always `.catch()` your `$` calls. |
| Both cases | OpenCode continues. The plugin's hooks are never registered. |

## 7. Comparison with npm Lifecycle Scripts (for Python Devs)

Python developers are used to several package lifecycle concepts. Here is how the plugin factory maps to each:

### `setup.py install` / `pip install` hooks

| Python | OpenCode Plugin |
|---|---|
| `python setup.py install` runs build steps once during install | The factory runs **every startup**, not once. No direct equivalent — use the factory for ongoing setup, not one-time install. |
| Post-install scripts in `setup.py` / `pyproject.toml` | No built-in post-install hook in OpenCode plugins. The factory is the closest equivalent but is intentionally not a one-time hook. |
| `pip install` places files in `site-packages/` | Bun auto-installs the npm package into `~/.cache/opencode/node_modules/`. The factory then copies bundled assets into `.opencode/`. |

### `__init__.py` module-level code

| Python | OpenCode Plugin |
|---|---|
| `__init__.py` code runs when `import package` executes | The factory runs when OpenCode imports the plugin module. Both are "on import" execution. |
| Can define `__all__` to control exports | The factory returns a hooks object that controls what events the plugin subscribes to. |
| Module-level code runs once per interpreter session | The factory runs once per OpenCode startup (which is typically one per session). |

### Django `AppConfig.ready()`

```python
# Django
class MyAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "my_app"

    def ready(self):
        # Runs when Django is fully loaded
        import my_app.signals  # Register signal handlers
```

| Django `ready()` | OpenCode factory |
|---|---|
| Runs once when Django starts | Runs once per OpenCode startup |
| Used to register signal handlers (`@receiver`) | Used to register event hooks (return value) |
| Can perform startup checks (e.g., database connectivity) | Can perform startup checks (e.g., CLI availability, file system state) |
| `ready()` is synchronous — no `async` support | The factory is `async` — can `await` shell commands, API calls, file I/O |
| Import signals at module level to register them | Return hooks object to register event handlers |

The most direct analogy: **the factory function is `AppConfig.ready()` made async**, where the initialization logic runs in the function body and the event handler registration happens via the return value rather than import-time side effects.

## Common Mistakes

### Mistake 1: Treating the Factory as a One-Time Install Script

```typescript
// WRONG: Assumes init code runs only on first install
export const MyPlugin = async ({ project }) => {
  const dest = join(project.path, ".opencode", "agents", "architect.md");
  copyFileSync(bundledPath, dest);
  // Every startup overwrites the user's custom architect.md!
};
```

**Fix:** Always check if the operation has already been done (version stamp, file existence check, etc.).

### Mistake 2: Unhandled Promise Rejections

```typescript
// WRONG: $`which gh` can reject if gh is not installed or command fails
export const MyPlugin = async ({ $ }) => {
  const { stdout } = await $`which gh`;
};
```

**Fix:** Always add `.catch()` to `$` calls, or wrap in try/catch.

### Mistake 3: Sync File Operations Blocking Startup

```typescript
// WORKS but blocks the event loop for large copies
mkdirSync(agentsDir, { recursive: true });
for (const file of manyFiles) {
  copyFileSync(src, dest);
}
return { ... }; // Nothing runs until copy finishes
```

The factory is called during startup — synchronous file operations block the entire OpenCode load. For small numbers of files (typical plugin: 3-10 agents, 2-5 skills), synchronous `*Sync` is fine. For hundreds of files, use `fs.promises` and `await`:

```typescript
import { mkdir, copyFile } from "fs/promises";
await mkdir(agentsDir, { recursive: true });
await Promise.all(manyFiles.map(f => copyFile(f.src, f.dest)));
```

### Mistake 4: Assuming `worktree` Is Always a String

```typescript
// WRONG: TypeScript might not catch this at runtime
const worktreePath = worktree.toUpperCase(); // TypeError if worktree is undefined
```

**Fix:** Always check for `undefined`:

```typescript
if (worktree) {
  const worktreePath = worktree.toUpperCase();
  // ...
}
```

### Mistake 5: Using `console.log` Instead of `client.app.log`

```typescript
// WRONG: console.log is not a crime but lacks structure
console.log("Plugin loaded");

// RIGHT: Structured logging visible in OpenCode's UI
await client.app.log({
  body: { service: "my-plugin", level: "info", message: "Plugin loaded" },
});
```

`client.app.log()` entries are structured, filterable, and appear in OpenCode's own logging infrastructure. `console.log` goes to stdout and is invisible in the OpenCode UI.

### Mistake 6: Forgetting That Multiple Handlers Can Share an Event Key

```typescript
// Both handlers run for "tool.execute.before" — in registration order
return {
  "tool.execute.before": async (input, output) => { /* handler A */ },
  "tool.execute.before": async (input, output) => { /* handler B */ },
};
```

JavaScript object semantics allow duplicate keys — the last one wins in a plain object literal. **But** TypeScript's `Plugin` type actually supports arrays of handlers or spread pattern. Check the `@opencode-ai/plugin` types for your version. When in doubt, use different event keys or compose handlers:

```typescript
return {
  "tool.execute.before": async (input, output) => {
    await handlerA(input, output);
    await handlerB(input, output);
  },
};
```

## See Also

- [Plugin Creation](creation.md) — Basic plugin structure, TypeScript support, and dependencies
- [Bundling Components](bundling-components.md) — Version stamping pattern, agent/skill copying, auto-discovery boundary
- [Loading](loading.md) — Load order, deduplication, global vs project plugins
- [Plugin Examples](examples.md) — More code examples for common plugin patterns
- [Event Patterns](event-patterns.md) — Named handlers, wildcard handlers, and event composition
