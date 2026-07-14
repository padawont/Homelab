---
title: "JavaScript/TypeScript for Python Developers"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - javascript
  - typescript
  - python
  - reference
sources:
  - url: "https://opencode.ai/docs/sdk"
    title: "OpenCode SDK Documentation"
  - url: "https://opencode.ai/docs/plugins"
    title: "OpenCode Plugins Documentation"
last_audit_date: 2026-06-07
---

# JavaScript/TypeScript for Python Developers

This note is a bridging guide for Python developers at RunicEngines who need to work with OpenCode plugin code written in JavaScript or TypeScript.

The `@runicengines/opencode-runesmith` plugin (and all OpenCode plugins) must be written in JavaScript or TypeScript. The Python SDK (`opencode-ai`) is an HTTP client only — it does **not** support plugin creation, event hooks, or the `@opencode-ai/plugin` package. This note helps Python developers navigate the JS ecosystem when writing or maintaining OpenCode plugins.

## 1. The Python SDK Limitation (Critical)

```python
# Python can connect to a running OpenCode server
from opencode_ai import Opencode  # Install with: pip install opencode-ai
client = Opencode(base_url="http://localhost:8000")
client.session.chat("Hello")
```

> **Caution:** The Python package name on PyPI is `opencode-ai` (with a hyphen). The Python import uses the underscored form `opencode_ai` (as is standard for Python packages with hyphens in their distribution name). If you encounter import errors, verify the package is installed with `pip install opencode-ai` and that the installed version matches your OpenCode server version.

```python
# But Python CANNOT:
# - Register event hooks (tool.execute.before, etc.)
# - Export plugin functions
# - Use @opencode-ai/plugin types
# - Spawn or manage the OpenCode server process
```

**This means any custom behavior must be a JS/TS plugin.** Python can only automate the client side — sending chat messages, reading files, and interacting with a server that is already running. If you need to hook into tool execution, modify environment variables before commands run, or add custom permissions logic, you must write those extensions in JavaScript or TypeScript.

The Python SDK is effectively a remote-control library. The Node.js plugin SDK (`@opencode-ai/plugin`) is the only way to register event hooks and extend the OpenCode runtime itself.

## 2. Bun vs Node vs npm

OpenCode uses **Bun** for auto-installing plugins. Bun is a JavaScript runtime and package manager that is faster than Node and has built-in TypeScript support, so no separate `tsc` compilation step is needed during development.

| Concept | Python Equivalent | JS/TS Equivalent |
|---|---|---|
| Runtime | `python3` | `bun` (or `node`) |
| Package manager | `pip` / `poetry` | `bun` / `npm` |
| Package file | `pyproject.toml` / `requirements.txt` | `package.json` |
| Lock file | `poetry.lock` | `bun.lock` / `package-lock.json` |
| Virtual env | `.venv` / `venv` | `node_modules/` |
| Install deps | `pip install -r requirements.txt` | `bun install` |
| Install tool | `pip install <pkg>` | `npm install <pkg>` |
| Publish | `twine upload dist/*` | `npm publish` / `bun publish` |

Key differences for Python devs:

- **`node_modules/`** is like `.venv/` — it holds installed dependencies. Unlike Python's global site-packages, each project has its own `node_modules/` tree.
- **`package.json`** combines the roles of `pyproject.toml`, `requirements.txt`, and `setup.py` into one file.
- **Lock files** (`bun.lock`) pin exact dependency versions, analogous to `poetry.lock`.
- Bun caches downloaded packages globally (like `~/.cache/pip/`) but resolves imports from the local `node_modules/` first.

## 3. package.json Explained (for Python Devs)

```json
{
  "name": "@runicengines/opencode-runesmith",
  "version": "1.0.0",
  "type": "module",
  "main": "./dist/index.js",
  "dependencies": {
    "@opencode-ai/plugin": "^1.0.0"
  },
  "publishConfig": {
    "registry": "https://npm.pkg.github.com",
    "access": "restricted"
  }
}
```

| Field | Python Equivalent | Purpose |
|---|---|---|
| `name` | Package name in `pyproject.toml` | Unique package identifier. The `@scope/` prefix is like a namespace package (`runicengines.*`). |
| `version` | `version = "1.0.0"` | SemVer string: `MAJOR.MINOR.PATCH`. |
| `type` | No direct equivalent | `"module"` enables ESM imports (like Python's `import`). `"commonjs"` or omitted uses `require()` (like `importlib`). |
| `main` | `[tool.poetry.scripts]` entry point | The file loaded when your package is imported or required. |
| `dependencies` | `[tool.poetry.dependencies]` | Runtime deps listed with SemVer ranges. `^1.0.0` means `>=1.0.0 <2.0.0`. |
| `devDependencies` | `[tool.poetry.dev-dependencies]` | Build-time or dev-only deps (testing, linting). |
| `publishConfig` | PyPI token / `.pypirc` | Registry URL and access level for publishing. GitHub Packages uses `restricted`. |
| `scripts` | Makefile / `[tool.poetry.scripts]` | Aliases for common commands: `"build": "tsc"`, `"test": "vitest run"`. Run with `bun run build`. |

### Version Ranges (SemVer)

| Range | Meaning | Python Equivalent |
|---|---|---|
| `^1.0.0` | `>=1.0.0 <2.0.0` | `^1.0.0` |
| `~1.0.0` | `>=1.0.0 <1.1.0` | `~=1.0.0` |
| `>=1.0.0` | `>=1.0.0` | `>=1.0.0` |
| `*` | Any version | No direct equivalent (avoid) |

## 4. ESM vs CJS (for Python Devs)

JavaScript has two module systems. OpenCode plugins should always use ESM.

| Aspect | ESM (Modern) | CJS (Legacy) |
|---|---|---|
| Import syntax | `import { x } from "y"` | `const { x } = require("y")` |
| Export syntax | `export const x = 1` | `module.exports = { x: 1 }` |
| Python analogy | `from y import x` | `importlib.import_module("y")` |
| File extension | `.mjs` or `.js` with `"type": "module"` | `.cjs` or `.js` without `"type": "module"` |
| Top-level await | Yes | No |
| Tree-shakeable | Yes | No |

```javascript
// ESM — use this (set "type": "module" in package.json)
import { type Plugin } from "@opencode-ai/plugin";

export const MyPlugin: Plugin = async (ctx) => {
  // plugin logic
};
```

```javascript
// CJS — avoid for new code
const { Plugin } = require("@opencode-ai/plugin");

module.exports.MyPlugin = async (ctx) => {
  // plugin logic
};
```

If you see `require(...)` or `module.exports` in a codebase, that's CJS. Modern TypeScript compiles to ESM when `"module": "esnext"` is set in `tsconfig.json`.

## 5. TypeScript Basics for Python Devs

TypeScript adds static typing to JavaScript. If you know Python type hints, you already understand most of TypeScript's type system.

| TypeScript | Python Equivalent | Notes |
|---|---|---|
| `: string` | `-> str` | Unicode text |
| `: number` | `-> float` / `-> int` | One type for all numbers (no separate int/float) |
| `: boolean` | `-> bool` | `true` / `false` (lowercase, unlike Python's `True`/`False`) |
| `: null` | `-> None` | `null` is a value (use `??` for nullish coalescing) |
| `: undefined` | `None` (unset) | A variable that hasn't been assigned a value |
| `: Promise<T>` | `async -> T` | Return type of an async function |
| `: T[]` | `list[T]` | Array of T |
| `: Record<K, V>` | `dict[K, V]` | Object/map type |
| `interface` | `Protocol` / `TypedDict` | Defines the shape of an object |
| `type` | `TypeAlias` | Creates a type alias |
| Generics `<T>` | `TypeVar('T')` | Parameterized types |

### Interface vs Type Aliases

```typescript
// interface (like TypedDict)
interface PluginContext {
  project: ProjectInfo;
  client: OpenCodeClient;
}

// type alias (like TypeAlias)
type PluginResult = {
  "tool.execute.before"?: EventHook;
};
```

Use `interface` for object shapes that may be extended. Use `type` for unions, intersections, or aliases. In practice, either works for OpenCode plugins.

### Common Pitfalls for Python Devs

1. **`null` and `undefined` are distinct** in JS. Python has only `None`.
   - `undefined` = variable declared but not assigned.
   - `null` = explicitly empty value.
   - Use `??` (nullish coalescing) to handle both: `value ?? defaultValue`.

2. **`===` not `==`**. Always use strict equality (`===` / `!==`) in JS. The loose `==` does type coercion and is a common source of bugs.

3. **Arrays use bracket indexing**, not tuple unpacking:
   ```python
   a, b = [1, 2]     # Python: works
   ```
   ```javascript
   const [a, b] = [1, 2];  // JS: destructuring required
   ```

4. **No keyword arguments**. JavaScript functions don't support keyword arguments. Use a single options object instead:
   ```javascript
   // Instead of: func(a=1, b=2)
   function func(options: { a?: number; b?: number }) { ... }
   func({ a: 1, b: 2 });
   ```

5. **`const` means rebind protection, not immutability**. `const x = { a: 1 }; x.a = 2;` is allowed. For true immutability use `Object.freeze()` or libraries like `immer`.

## 6. The @opencode-ai/plugin SDK

The `@opencode-ai/plugin` package provides the TypeScript types and runtime helpers for writing OpenCode plugins.

```typescript
import type { Plugin, EventHooks } from "@opencode-ai/plugin";

export const MyPlugin: Plugin = async ({
  project,
  client,
  $,
  directory,
  worktree
}) => {
  // project   — like a Python dataclass with project metadata (name, path, language, etc.)
  // client    — like an HTTP session for the OpenCode API
  // $         — like subprocess.run() but returns stdout/stderr/exitCode
  // directory — like os.getcwd() — the current working directory
  // worktree  — like the git worktree root (may differ from directory)

  return {
    // Event hooks — like Django signals or pluggy hooks
    "tool.execute.before": async (input, output) => {
      // input  — the tool call parameters
      // output — the mutable result (you can modify it before the tool runs)
    },
  };
};
```

### Available Context Properties

| Property | Type | Python Analogy | Description |
|---|---|---|---|
| `project` | `ProjectInfo` | Dataclass | Current project metadata |
| `client` | `OpenCodeClient` | `httpx.Client` | Authenticated API client for the OpenCode server |
| `$` | `Shell` | `subprocess.run` | Run shell commands with tagged template literals: `` await $`cmd` `` |
| `directory` | `string` | `os.getcwd()` | Working directory of the current session |
| `worktree` | `string \| undefined` | `Path(git_root) \| None` | Git root of the project (undefined if not in a worktree) |

### Plugin Return Type

The `Plugin` type returns an `EventHooks` object. All hooks are optional. The available event hook names follow a `domain.action.phase` pattern:

```typescript
type EventHooks = {
  "tool.execute.before"?: (input: ToolInput, output: ToolOutput) => void | Promise<void>;
  "tool.execute.after"?: (input: ToolInput, output: ToolOutput) => void | Promise<void>;
  "command.executed"?: (command: string) => string | Promise<string>;
  "message.updated"?: (message: ChatMessage) => void | Promise<void>;
  "message.removed"?: (message: ChatMessage) => void | Promise<void>;
  "permission.asked"?: (request: PermissionRequest) => PermissionResponse | Promise<PermissionResponse>;
  "permission.replied"?: (request: PermissionRequest) => PermissionResponse | Promise<PermissionResponse>;
  // ... and more (this list is not exhaustive)
};
```

### Helper: The `$` Shell Object

The `$` object is Bun's built-in shell API — it uses **tagged template literals** (`` await $`command` ``), not the `zx`-style `$.exec()` pattern. The sibling note [Plugin Init Hook Lifecycle](../plugins/init-hook-lifecycle.md) documents this correctly. Below are the key usage patterns with Python analogies:

```typescript
// Basic command — like subprocess.check_output("npm list --depth=0")
const { stdout } = await $`npm list --depth=0`;

// Variable interpolation with auto-escaping (like passing a list to subprocess.run)
const script = "script.py";
const flag = "--flag";
await $`python ${script} ${flag}`;  // Auto-escaped — no shell injection risk

// Return shape — always available as destructured properties
const { stdout, stderr, exitCode } = await $`npm test`;
console.log(stdout);    // like result.stdout
console.log(stderr);    // like result.stderr
console.log(exitCode);  // like result.returncode

// Pipe support — pipes work naturally within the template literal
const { stdout: grepResult } = await $`cat package.json | grep "name"`;
```

| Aspect | Bun Shell (`$`) | Python Equivalent |
|---|---|---|
| Syntax | Tagged template literal: `` $`command` `` — Bun parses it, handles escaping automatically | `subprocess.run(["command"], capture_output=True, text=True)` |
| Security | **Auto-escapes** interpolated values. `` $`echo ${userInput}` `` escapes `userInput` to prevent shell injection. | Passing a list to `subprocess.run` instead of a string with `shell=True` |
| Return value | `{ stdout, stderr, exitCode }` — always available | `subprocess.CompletedProcess` with `.stdout`, `.stderr`, `.returncode` |
| Pipe support | `` await $`cmd1 \| cmd2` `` — pipes work naturally within the template literal | `p1 = subprocess.Popen(...); p2 = subprocess.Popen(...)` manual piping |

**Why `$` exists:** Python developers typically reach for `os.system()`, `subprocess.run()`, or the `sh` library. The `$` API is Bun's built-in shell — it ships with the runtime, requires no imports, and is designed for async/await from the ground up.

**Warning:** `$` is **not** Bash. It is Bun's lightweight shell parser. It supports common syntax (`|`, `&&`, `>`, `<`, `$(...)`) but not Bash-specific features like brace expansion or process substitution. Keep commands simple.

**Note:** Unlike the legacy `zx` library's `$.exec()` pattern, Bun's `$` always returns `{ stdout, stderr, exitCode }` and does not accept an options object for `cwd` or `env`. For working directory changes, use `cd` within the template literal or set the directory context via Bun's `Shell` constructor.

## 7. Common JS Patterns for Python Devs

### Destructuring

```python
# Python
a, b = my_tuple
name, age = user_dict["name"], user_dict["age"]
x, y = get_coords()
```

```javascript
// JavaScript
const [a, b] = myArray;
const { name, age } = userObj;
const { x, y } = getCoords();
```

Array destructuring uses `[]` (not tuple unpacking). Object destructuring uses `{}` (like dictionary unpacking in Python but for any object).

### Arrow Functions

```python
# Python
f = lambda x: x * 2
squares = list(map(lambda x: x**2, range(10)))
```

```javascript
// JavaScript
const f = (x) => x * 2;
const squares = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((x) => x ** 2);
```

Arrow functions are the most common way to write inline functions in modern JS. Unlike Python's `lambda`, they can have block bodies with multiple statements: `(x) => { const y = x * 2; return y + 1; }`.

### Template Literals

```python
# Python
name = "World"
greeting = f"Hello {name}"
```

```javascript
// JavaScript
const name = "World";
const greeting = `Hello ${name}`;
```

Template literals use backticks (`` ` ``) and `${}` for interpolation. They also support multiline strings without `\n`:

```javascript
const multiline = `
  Line 1
  Line 2
`;
```

### Async/Await

Same concept as Python — both use the same keywords:

```python
# Python
async def fetch_data():
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.example.com")
    return resp.json()
```

```javascript
// JavaScript
async function fetchData() {
  const resp = await fetch("https://api.example.com");
  return resp.json();
}
```

Key differences:
- `async function` declaration (JS) vs `async def` (Python).
- `Promise.all([...])` (JS) vs `asyncio.gather(...)` (Python) for concurrent execution.
- No `asyncio.run()` equivalent — JS `async` functions run automatically in the event loop.

### Promises

```python
# Python
future = asyncio.ensure_future(some_coro())
result = await future
```

```javascript
// JavaScript
const promise = fetch("https://api.example.com");
const result = await promise;

// Or chain with .then()
promise.then((data) => console.log(data));
```

A `Promise` is like Python's `Future` — it represents a value that may be available now, later, or never. In modern code you use `async`/`await` instead of `.then()` chains.

### Optional Chaining

```python
# Python
value = getattr(obj, "prop", None)
nested = obj and obj.get("nested", {}).get("value")
```

```javascript
// JavaScript
const value = obj?.prop;             // undefined if obj is null/undefined
const nested = obj?.nested?.value;   // undefined if any chain member is null/undefined
```

Optional chaining (`?.`) short-circuits to `undefined` if the left side is `null` or `undefined`. Python's closest equivalent is `getattr()` or a series of `and` guards.

### Nullish Coalescing

```python
# Python
value = a or b          # Falls back if a is falsy (0, "", None, etc.)
value = a if a is not None else b  # Falls back only if a is None
```

```javascript
// JavaScript
const value = a ?? b;   // Falls back only if a is null or undefined
const value = a || b;   // Falls back if a is falsy (0, "", null, undefined, NaN, false)
```

Use `??` when you want to distinguish between `null`/`undefined` and other falsy values like `0` or `""`. Use `||` when any falsy value should trigger the fallback.

### Spread Operator

```python
# Python
merged = {**dict1, **dict2}
combined = [*list1, *list2]
```

```javascript
// JavaScript
const merged = { ...obj1, ...obj2 };
const combined = [...arr1, ...arr2];
```

The spread operator (`...`) unpacks iterables and objects, similar to Python's `*` and `**` unpacking.

### Array Methods (like Python's list comprehensions)

| Task | Python | JavaScript |
|---|---|---|
| Map | `[f(x) for x in items]` | `items.map(x => f(x))` |
| Filter | `[x for x in items if p(x)]` | `items.filter(x => p(x))` |
| Reduce | `functools.reduce(f, items)` | `items.reduce((acc, x) => f(acc, x))` |
| Any/All | `any(p(x) for x in items)` | `items.some(x => p(x))` / `items.every(x => p(x))` |
| Find | `next(x for x in items if p(x))` | `items.find(x => p(x))` |
| Sort | `sorted(items, key=f)` | `items.toSorted((a, b) => a - b)` |

JavaScript's array methods chain naturally: `items.filter(x => x.active).map(x => x.name).sort()`.

## 8. File System Operations

Node.js provides the `fs` module (like Python's `os` and `shutil`) and the `path` module (like `os.path`).

### Setup for ESM

```javascript
import { copyFileSync, mkdirSync, existsSync, readdirSync, writeFileSync, readFileSync } from "fs";
import { join, dirname, basename, extname, resolve } from "path";
import { fileURLToPath } from "url";

// __dirname equivalent in ESM (not available natively)
const __dirname = dirname(fileURLToPath(import.meta.url));
```

### Common Operations

| Task | Python | JavaScript |
|---|---|---|
| Read file | `open(path).read()` | `readFileSync(path, "utf-8")` |
| Write file | `open(path, "w").write(text)` | `writeFileSync(path, text, "utf-8")` |
| List directory | `os.listdir(path)` | `readdirSync(path)` |
| Check exists | `os.path.exists(path)` | `existsSync(path)` |
| Create dirs | `os.makedirs(path, exist_ok=True)` | `mkdirSync(path, { recursive: true })` |
| Copy file | `shutil.copy(src, dst)` | `copyFileSync(src, dst)` |
| Join paths | `os.path.join(a, b)` | `join(a, b)` |
| Get parent dir | `os.path.dirname(path)` | `dirname(path)` |
| Get filename | `os.path.basename(path)` | `basename(path)` |
| Get extension | `os.path.splitext(path)[1]` | `extname(path)` |
| Absolute path | `os.path.abspath(path)` | `resolve(path)` |

### Async Filesystem (preferred in plugins)

All `*Sync` methods have async counterparts. Prefer async in plugins to avoid blocking the event loop:

```javascript
import { readFile, writeFile, readdir, mkdir, copyFile } from "fs/promises";
import { join } from "path";

const content = await readFile(join(__dirname, "config.json"), "utf-8");
await writeFile(join(__dirname, "output.txt"), content);
const files = await readdir(somePath);
await mkdir(somePath, { recursive: true });
await copyFile(src, dest);
```

## 9. Quick Reference Card

### One-Line Syntax Comparisons

```javascript
// Variable declaration
const x = 1;  // immutable binding (like a constant reference)
let y = 2;    // mutable variable (like a regular variable)

// Function (named)
function add(a: number, b: number): number { return a + b; }

// Function (arrow, const)
const add = (a: number, b: number): number => a + b;

// Type guard
if (typeof value === "string") { ... }

// Loop
for (const item of items) { ... }         // like for item in items:
for (const [key, value] of map) { ... }   // like for k, v in dict.items():

// Ternary
const result = condition ? valueIfTrue : valueIfFalse;

// Default parameter
function greet(name: string = "World") { ... }

// Rest parameters
function sum(...numbers: number[]) { ... }  // like def sum(*numbers):

// Error handling
try { ... } catch (error) { ... } finally { ... }
```

### Plugin Template (Copy-Paste Ready)

```typescript
import type { Plugin } from "@opencode-ai/plugin";

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  console.log(`Plugin loaded for project: ${project.name}`);

  return {
    "tool.execute.before": async (input, output) => {
      console.log(`Tool ${input.name} is about to execute`);
    },
    "tool.execute.after": async (input, output) => {
      console.log(`Tool ${input.name} finished with exit code ${output.exitCode}`);
    },
  };
};
```

### Key Rules of Thumb

1. **Use ESM, not CJS** — set `"type": "module"` in `package.json`.
2. **Use `const` by default** — only use `let` when you need to reassign.
3. **Use `===`, never `==`** — strict equality only.
4. **Use async/await** — never use raw `.then()` chains in new code.
5. **Use `??` for defaults** — `value ?? defaultValue` (not `||`).
6. **Use template literals** — `` `Hello ${name}` `` not `"Hello " + name`.
7. **Use array methods** — `.map()`, `.filter()`, `.find()` instead of `for` loops.
8. **Use TypeScript** — always add types. The `@opencode-ai/plugin` package provides `Plugin` and related types.
9. **Run `bun run build`** — to compile TypeScript before publishing.
10. **Test with `bun test`** — Bun has a built-in test runner compatible with Jest/Vitest APIs.
