---
title: "Testing OpenCode Plugins"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-08
tags:
  - opencode
  - plugins
  - testing
  - ci-cd
  - typescript
sources:
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
  - url: "https://vitest.dev/"
    title: "Vitest Documentation"
  - url: "https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html"
    title: "TypeScript 4.9 Release Notes"
  - url: "https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-nodejs"
    title: "Building and testing Node.js — GitHub Docs"
last_audit_date: 2026-06-08
---

# Testing OpenCode Plugins

OpenCode plugins are TypeScript/JavaScript modules that export factory functions receiving a context object (`{ project, client, $, directory, worktree }`) and return event handler hooks. This note covers every aspect of testing them: mocking the plugin context, asserting file-copy and version-stamp behavior, testing event handler guards and transformations, and wiring everything into CI.

The patterns here build on the plugin creation conventions described in [`../creation.md`](../creation.md), the init hook lifecycle in [`../init-hook-lifecycle.md`](../init-hook-lifecycle.md), and the component bundling patterns in [`../bundling-components.md`](../bundling-components.md).

## Testing Init Hook File-Copy Logic

The most common init hook behavior in an OpenCode plugin is **provisioning files** — copying agents, skills, or tools from the npm package into the project's `.opencode/` directory. The init hook may also manage a **version stamp** to track which version of each component is deployed, enabling update propagation and self-healing.

### Temp Project Directory Setup

Every test that exercises file-copy logic should operate inside an isolated temporary directory. This prevents tests from touching real project files and makes cleanup trivial.

```typescript
import { describe, expect, it, beforeEach, afterEach } from "vitest";
import { mkdtempSync, existsSync, readFileSync, writeFileSync, rmSync, mkdirSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";

/**
 * Creates a fresh temp project directory for each test.
 * Structure mirrors a real OpenCode project:
 *   <tmp>/
 *     .opencode/
 *       agents/
 *       skills/
 */
function createTempProject(): { root: string; opencodeDir: string } {
  const root = mkdtempSync(join(tmpdir(), "opencode-test-"));
  const opencodeDir = join(root, ".opencode");
  mkdirSync(join(opencodeDir, "agents"), { recursive: true });
  mkdirSync(join(opencodeDir, "skills"), { recursive: true });
  return { root, opencodeDir };
}

describe("init hook file-copy", () => {
  let projectDir: string;
  let opencodeDir: string;

  beforeEach(() => {
    const temp = createTempProject();
    projectDir = temp.root;
    opencodeDir = temp.opencodeDir;
  });

  afterEach(() => {
    rmSync(projectDir, { recursive: true, force: true });
  });

  it("creates temp project structure", () => {
    expect(existsSync(opencodeDir)).toBe(true);
    expect(existsSync(join(opencodeDir, "agents"))).toBe(true);
    expect(existsSync(join(opencodeDir, "skills"))).toBe(true);
  });
});
```

### Mock Context Object

The plugin factory expects a context object. Build a minimal mock that matches the `PluginInput` type:

```typescript
import { vi } from "vitest";

/**
 * Creates a minimal mock OpenCode plugin context.
 *
 * Uses TypeScript's `satisfies` keyword to ensure the mock
 * conforms to the expected shape without widening the type.
 */
function createMockContext(overrides: Partial<PluginInput> = {}) {
  const mockLog = vi.fn();
  const mockShell = vi.fn().mockResolvedValue({
    stdout: Buffer.from(""),
    stderr: Buffer.from(""),
    exitCode: 0,
  });

  const context = {
    project: {
      name: "test-project",
      path: projectDir,
      config: {},
    },
    client: {
      app: {
        log: mockLog,
      },
    },
    $: mockShell as unknown as PluginInput["$"],
    experimental_workspace: { register: vi.fn() },
    serverUrl: new URL("http://localhost:4096"),
    directory: projectDir,
    worktree: projectDir,
    ...overrides,
  } satisfies Partial<PluginInput> as unknown as PluginInput;

  return context;
}
```

**Key points:**

- `client.app.log` is a `vi.fn()` spy so tests can assert on call count and arguments.
- `$` (Bun's shell) is a `vi.fn()` that returns a mock result by default. Tests can override the return value per assertion.
- `satisfies Partial<PluginInput>` performs a compile-time shape check (TS 4.9+) — it verifies the object literal conforms to the expected type without widening. `as unknown as PluginInput` then forces the narrowed type for the return signature. For environments without `satisfies`, use the `as` cast alone: `as unknown as PluginInput`.
- `overrides` lets individual tests customize specific fields (e.g., a different `directory` path).

### Testing Version-Stamping

A common pattern is writing a `.version` stamp file so the plugin can detect when a component has already been deployed.

```typescript
import { readFileSync, writeFileSync } from "fs";
import { join } from "path";

// The actual stamp file path used by the plugin under test
const STAMP_FILE = join(opencodeDir, "agents", ".version");

it("writes a version stamp on first copy", async () => {
  // Simulate the plugin's init hook running
  const plugin = await MyPlugin(createMockContext());
  // ... trigger the hook ...

  // Assert stamp was written
  expect(existsSync(STAMP_FILE)).toBe(true);
  const stamp = readFileSync(STAMP_FILE, "utf-8").trim();
  expect(stamp).toBe("1.0.0"); // or whatever version the plugin declares
});

it("reads an existing stamp without overwriting", async () => {
  // Write a stamp manually (simulating a prior install)
  writeFileSync(STAMP_FILE, "1.0.0\n");

  // Run the plugin
  const plugin = await MyPlugin(createMockContext());
  // ... trigger the hook ...

  // Stamp should still be "1.0.0" (unchanged)
  const stamp = readFileSync(STAMP_FILE, "utf-8").trim();
  expect(stamp).toBe("1.0.0");
});
```

### Testing Update Propagation

When the plugin version changes, the init hook should detect a stamp mismatch and re-copy the components.

```typescript
it("re-copies agents when version stamp differs", async () => {
  // Simulate an older version stamp
  writeFileSync(STAMP_FILE, "0.9.0\n");

  // Run the plugin with the newer version
  const plugin = await MyPlugin(createMockContext());
  // ... trigger the hook ...

  // Assert stamp was updated
  const stamp = readFileSync(STAMP_FILE, "utf-8").trim();
  expect(stamp).toBe("1.0.0");

  // Assert component files were refreshed (check a known file)
  const agentFile = join(opencodeDir, "agents", "my-agent.md");
  expect(existsSync(agentFile)).toBe(true);
});

it("logs update message when propagating", async () => {
  const mockLog = vi.fn();
  writeFileSync(STAMP_FILE, "0.9.0\n");

  const plugin = await MyPlugin(createMockContext({
    client: { app: { log: mockLog } },
  }));
  // ... trigger the hook ...

  expect(mockLog).toHaveBeenCalledWith(
    expect.stringContaining("updating agent from 0.9.0 to 1.0.0")
  );
});
```

### Testing Self-Healing (File Deletion Recovery)

If a component file is deleted but the version stamp still exists, the init hook should detect the missing file and re-copy it.

```typescript
it("re-copies deleted agent file when stamp exists", async () => {
  // Arrange: stamp exists but agent file is missing
  writeFileSync(STAMP_FILE, "1.0.0\n");
  const agentFile = join(opencodeDir, "agents", "my-agent.md");

  // Manually ensure it does NOT exist
  expect(existsSync(agentFile)).toBe(false);

  // Act: run the plugin
  const plugin = await MyPlugin(createMockContext());
  // ... trigger the hook ...

  // Assert: file was recreated
  expect(existsSync(agentFile)).toBe(true);
});

it("logs self-healing message", async () => {
  const mockLog = vi.fn();
  writeFileSync(STAMP_FILE, "1.0.0\n");

  const plugin = await MyPlugin(createMockContext({
    client: { app: { log: mockLog } },
  }));
  // ... trigger the hook ...

  expect(mockLog).toHaveBeenCalledWith(
    expect.stringContaining("self-heal")
  );
});
```

**Edge case — version mismatch with deletion:**

```typescript
it("handles stamp mismatch AND missing file: re-copies and updates stamp", async () => {
  writeFileSync(STAMP_FILE, "0.9.0\n");
  const agentFile = join(opencodeDir, "agents", "my-agent.md");

  const plugin = await MyPlugin(createMockContext());
  // ... trigger the hook ...

  const stamp = readFileSync(STAMP_FILE, "utf-8").trim();
  expect(stamp).toBe("1.0.0");
  expect(existsSync(agentFile)).toBe(true);
});
```

## Mocking @opencode-ai/plugin Types

Properly typed mocks prevent regressions when the plugin SDK types change. Below is a complete mock setup that can be shared across test files.

### Full Mock Context Factory

This is an expanded version of the factory from the previous section, suitable for a shared test utility file (e.g., `test-utils.ts`):

```typescript
// test-utils.ts
import { vi } from "vitest";
import { type PluginInput } from "@opencode-ai/plugin";

/**
 * Type representing Bun's `$` shell function.
 * In reality `$` is a tagged template literal, but for tests
 * we mock it as a regular async function.
 */
interface MockShellResult {
  stdout: Buffer;
  stderr: Buffer;
  exitCode: number;
}

type MockShell = (...args: unknown[]) => Promise<MockShellResult>;

/**
 * Creates a fully typed mock OpenCode plugin context.
 *
 * Usage:
 *   const ctx = createMockContext({ project: { name: "my-app" } });
 *   const plugin = MyPlugin(ctx);
 */
export function createMockContext(
  overrides: Partial<PluginInput> = {}
): PluginInput {
  const mockLog = vi.fn();
  const mockShell: MockShell = vi.fn().mockResolvedValue({
    stdout: Buffer.from(""),
    stderr: Buffer.from(""),
    exitCode: 0,
  });

  const defaultContext = {
    project: {
      name: "test-project",
      path: "/tmp/test-project",
      config: {},
    },
    client: {
      app: {
        log: mockLog,
      },
      // Add other client APIs as needed (e.g., via partial overrides in tests)
    },
    $: mockShell as unknown as PluginInput["$"],
    experimental_workspace: { register: vi.fn() },
    serverUrl: new URL("http://localhost:4096"),
    directory: "/tmp/test-project",
    worktree: "/tmp/test-project",
  };

  return { ...defaultContext, ...overrides } satisfies Partial<PluginInput> as unknown as PluginInput;
}
```

### Mocking fs Operations

Use `vi.mock` to mock Node.js `fs` module at the module level. This is useful when the plugin under test imports and uses `fs` directly (rather than receiving it via the context).

```typescript
import { vi } from "vitest";
import { existsSync, readFileSync, writeFileSync } from "fs";

vi.mock("fs", async (importOriginal) => {
  const actual = await importOriginal<typeof import("fs")>();
  return {
    ...actual,
    existsSync: vi.fn(actual.existsSync),
    readFileSync: vi.fn(actual.readFileSync),
    writeFileSync: vi.fn(actual.writeFileSync),
  };
});

beforeEach(() => {
  vi.clearAllMocks();
});

it("detects missing file via mocked existsSync", () => {
  vi.mocked(existsSync).mockReturnValue(false);

  // The plugin should attempt the copy path
  const plugin = await MyPlugin(createMockContext());
  // ... trigger hook ...

  expect(vi.mocked(writeFileSync)).toHaveBeenCalled();
});

it("skips copy when file exists", () => {
  vi.mocked(existsSync).mockReturnValue(true);

  const plugin = await MyPlugin(createMockContext());
  // ... trigger hook ...

  expect(vi.mocked(writeFileSync)).not.toHaveBeenCalled();
});
```

**Isolation tip:** Use `vi.mock` with `importOriginal` to preserve real `fs` behavior for tests that need it, while allowing selective spy overrides. For tests that need fully isolated filesystem access, prefer the temp-directory pattern from the first section instead of mocking `fs`.

### Type Safety with satisfies + vi.mocked

```typescript
// Best practice: use satisfies for mock object shape, then vi.mocked for function spies
it("logs an info message on startup", async () => {
  const mockLog = vi.fn();
  const context = {
    ...createMockContext(),
    client: { app: { log: mockLog } },
  } satisfies PluginInput;

  await MyPlugin(context);

  expect(mockLog).toHaveBeenCalledWith(
    expect.stringContaining("initialized")
  );
});
```

## Testing Event Handlers

Event handlers are the functions returned by the plugin factory. They receive event-specific payloads and can modify inputs, perform side effects, or throw to block operations.

### Unit Tests for tool.execute.before Guards

The `tool.execute.before` hook fires before any custom tool executes. A common use case is blocking dangerous commands.

```typescript
import { describe, it, expect } from "vitest";

describe("tool.execute.before guard", () => {
  async function createGuard() {
    const plugin = await DangerousToolGuard(createMockContext());
    return plugin["tool.execute.before"]!;
  }

  it("allows safe commands", async () => {
    const guard = await createGuard();
    await guard(
      { tool: "list-files", sessionID: "test-session", callID: "test-call" },
      { args: { path: "/safe" } }
    );
    // Handler does not throw — guard passed
  });

  it("blocks commands with dangerous arguments", async () => {
    const guard = await createGuard();
    await expect(
      guard(
        { tool: "shell-exec", sessionID: "test-session", callID: "test-call" },
        { args: { command: "rm -rf /" } }
      )
    ).rejects.toThrow(/blocked|dangerous/i);
  });

  it("modifies tool arguments before execution", async () => {
    const guard = await createGuard();
    const output = { args: { path: "../outside" } };
    await guard(
      { tool: "read-file", sessionID: "test-session", callID: "test-call" },
      output
    );

    // Guard resolved the relative path to an absolute one
    expect(output.args.path).not.toBe("../outside");
    expect(output.args.path).toMatch(/^\//);
  });
});
```

### Unit Tests for session.created Event

The `session.created` event fires when a new conversation session starts. It is dispatched through the generic `event` hook with `event.type === "session.created"`. This is commonly used for logging or telemetry.

```typescript
describe("session.created event", () => {
  it("logs session ID on creation", async () => {
    const mockLog = vi.fn();
    const context = createMockContext({
      client: { app: { log: mockLog } },
    });
    const plugin = await MyPlugin(context);
    const handler = plugin.event!;

    await handler({
      type: "session.created",
      data: { session: { id: "sess_abc123", project: "test" } },
    });

    expect(mockLog).toHaveBeenCalledWith(
      expect.stringContaining("sess_abc123")
    );
  });

  it("does not throw when log is unavailable", async () => {
    const context = createMockContext({
      client: { app: {} as any },
    });
    const plugin = await MyPlugin(context);
    const handler = plugin.event!;

    // Handler should not throw — if it does, the awaited call will fail the test
    await handler({ type: "session.created", data: { session: { id: "sess_001" } } } as any);
  });
});
```

### Testing Input/Output Modification

Some event handlers transform or enrich tool definitions. These handlers receive an `input` object (identifying the resource) and an `output` object (which they modify in-place). Test both the input selection and the output shape.

```typescript
describe("input/output modification", () => {
  it("enriches tool definition with metadata", async () => {
    const plugin = await MyPlugin(createMockContext());
    const handler = plugin["tool.definition"]!;

    const output = { description: "", parameters: {} };
    await handler({ toolID: "my-tool" }, output);

    expect(output.description).toBeTruthy();
    expect(output.parameters).toMatchObject({
      metadata: { source: "my-plugin" },
    });
  });

  it("leaves unrelated tools unchanged", async () => {
    const plugin = await MyPlugin(createMockContext());
    const handler = plugin["tool.definition"]!;

    const output = { description: "", parameters: {} };
    await handler({ toolID: "other-tool" }, output);

    expect(output).toEqual({ description: "", parameters: {} });
  });
});
```

### Testing Error-Throwing Guards

When a guard needs to block execution entirely, it throws. Use `expect().rejects.toThrow()` to test this.

```typescript
describe("error-throwing guards", () => {
  it("throws PermissionDenied for unauthorized tools", async () => {
    const plugin = await PermissionGuard(createMockContext());
    const handler = plugin["tool.execute.before"]!;

    await expect(
      handler(
        { tool: "admin-only", sessionID: "test-session", callID: "test-call" },
        { args: {} }
      )
    ).rejects.toThrow(/PermissionDenied/i);
  });

  it("throws with a descriptive message", async () => {
    const plugin = await PermissionGuard(createMockContext());
    const handler = plugin["tool.execute.before"]!;

    try {
      await handler(
        { tool: "admin-only", sessionID: "test-session", callID: "test-call" },
        { args: {} }
      );
      // Force failure if no error was thrown
      expect.unreachable("should have thrown");
    } catch (error) {
      expect(error).toBeInstanceOf(Error);
      expect((error as Error).message).toMatch(/not authorized/i);
    }
  });

  it("does not throw for authorized tools", async () => {
    const plugin = await PermissionGuard(createMockContext());
    const handler = plugin["tool.execute.before"]!;

    await expect(
      handler(
        { tool: "list-files", sessionID: "test-session", callID: "test-call" },
        { args: {} }
      )
    ).resolves.toBeUndefined();
  });
});
```

## CI Workflow for npm test

A robust CI pipeline ensures plugins are tested across Node.js versions, with caching for fast installs, and vitest configured for single-run mode.

### Basic GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18, 20, 22]

    steps:
      - uses: actions/checkout@v6

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v6
        with:
          node-version: ${{ matrix.node-version }}
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test
```

### package.json Script Configuration

Ensure your `package.json` scripts are set up for CI compatibility:

```jsonc
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage"
  }
}
```

The `vitest run` command (as opposed to plain `vitest`, which starts watch mode) executes all tests once in CI mode — it does not start the interactive watcher, so it exits cleanly with the appropriate exit code.

### vitest.config.ts

A minimal vitest configuration for an OpenCode plugin:

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: false,
    environment: "node",
    include: ["test/**/*.test.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      include: ["src/**/*.ts"],
    },
  },
});
```

### Caching Details

The `setup-node` action with `cache: "npm"` automatically handles `node_modules` caching:

```yaml
- uses: actions/setup-node@v6
  with:
    node-version: ${{ matrix.node-version }}
    cache: "npm"
```

This caches `~/.npm` (the global npm cache), which speeds up `npm ci` significantly. For projects with large `node_modules`, you can also add explicit `actions/cache` steps for the `node_modules` directory itself:

```yaml
- name: Cache node_modules
  uses: actions/cache@v5
  with:
    path: node_modules
    key: ${{ runner.os }}-node-${{ matrix.node-version }}-${{ hashFiles('package-lock.json') }}
```

### Full Matrix Workflow with Coverage

```yaml
name: Test & Coverage

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]

    steps:
      - uses: actions/checkout@v6

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v6
        with:
          node-version: ${{ matrix.node-version }}
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npx tsc --noEmit

      - name: Run tests with coverage
        run: npx vitest run --coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v7
        with:
          flags: node-${{ matrix.node-version }}
          token: ${{ secrets.CODECOV_TOKEN }}  # Recommended for non-fork PRs (v5+ supports tokenless opt-in, but token ensures reliability)
        continue-on-error: true
```

## Summary

| Concern | Pattern |
|---|---|
| **Isolated filesystem** | `mkdtempSync()` + `rmSync()` in `beforeEach`/`afterEach` |
| **Mock context** | Factory function with `satisfies` keyword + `vi.fn()` for spies |
| **Version stamps** | Read/write `.version` file; assert content after init hook |
| **Update propagation** | Write old stamp → run hook → assert updated stamp + re-copied files |
| **Self-healing** | Write stamp, delete file → run hook → assert file restored |
| **fs mocking** | `vi.mock("fs", async (importOriginal) => ({ ... }))` |
| **Event handlers** | Return from plugin factory and invoke directly with mock payload |
| **Guards (block)** | `expect().rejects.toThrow()` |
| **CI** | GitHub Actions matrix across Node 18/20/22, `npm ci`, `vitest run` |
| **Type safety** | `satisfies` for mocks; `vi.mocked()` for module spies |

## References

- OpenCode Plugins Documentation: <https://opencode.ai/docs/plugins>
- Vitest Documentation: <https://vitest.dev/>
- TypeScript 4.9 Release Notes: <https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html>
- Building and testing Node.js — GitHub Docs: <https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-nodejs>
- [Plugin Creation](../creation.md) — Plugin structure and factory function pattern
- [Init Hook Lifecycle](../init-hook-lifecycle.md) — Version-stamping, file-copy, self-healing lifecycle
- [Bundling Components](../bundling-components.md) — Component copy patterns for agents, skills, and tools
