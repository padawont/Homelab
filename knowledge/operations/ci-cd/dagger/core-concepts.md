---
title: "Dagger — Core Concepts"
status: draft
author: "padawont"
date: 2026-07-22
tags: ["dagger", "core-concepts", "dags", "caching", "modules", "daggerverse"]
sources:
  - url: "https://docs.dagger.io/getting-started/concepts"
    title: "Dagger Core Concepts"
  - url: "https://docs.dagger.io/features/caching"
    title: "Dagger Caching"
  - url: "https://docs.dagger.io/features/services"
    title: "Dagger Services"
  - url: "https://docs.dagger.io/features/secrets"
    title: "Dagger Secrets"
last_audit_date: 2026-07-22
---

# Dagger Core Concepts

## DAG Execution Model

Dagger pipelines execute as a **Directed Acyclic Graph (DAG)** of low-level operations. The engine computes the DAG concurrently, running independent branches in parallel and only waiting on dependencies. This is fundamentally different from step-based CI (GitHub Actions, GitLab CI) where each step runs sequentially.

## Content-Addressed Caching

Dagger provides three caching layers:

| Cache Type | Mechanism | Use Case |
|---|---|---|
| **Layer caching** | Build instructions + API call results cached by content hash | Automatic — change one file, only affected ops re-run |
| **Volume caching** | `dag.cache_volume("name")` + `with_mounted_cache(path, volume)` | Package manager caches (npm, pip, maven) |
| **Function call caching** | Cached values from module function calls | Skip execution when cached result exists |

Example — volume caching for npm:

```python
node_cache = dag.cache_volume("node")
container = (
    dag.container()
    .from_("node:21-slim")
    .with_mounted_cache("/root/.npm", node_cache)
    .with_workdir("/src")
    .with_exec(["npm", "install"])
)
```

## Module System

Modules are collections of Dagger functions packaged together. They extend the Dagger API dynamically when loaded.

Create a module:

```bash
dagger init --sdk=python --name=my-module
```

Key decorators:

| Decorator | Purpose |
|---|---|
| `@object_type` | Marks a class as a Dagger module object |
| `@function` | Marks a method as a callable Dagger function |
| `@func()` | Alternative to `@function` for function-level modules |

List available functions in a module:

```bash
dagger functions
```

Run a function:

```bash
dagger call <function-name> --source=.
```

Check all functions compile:

```bash
dagger check
```

## Daggerverse

The [Daggerverse](https://daggerverse.dev) is a public registry of Dagger modules. Modules can be referenced by their Git URL and used as dependencies in other modules.

## Type System

Core Dagger types:

| Type | Description |
|---|---|
| `Container` | An OCI container — the primary unit of computation |
| `Directory` | A filesystem directory (host or container) |
| `File` | A single file |
| `Service` | An ephemeral network service (database, API) |
| `Secret` | A secret value — never exposed in logs or cache |
| `CacheVolume` | A persistent cache volume |
| `GitRepository` | A Git repository reference |

## Services (Ephemeral)

Services allow container-to-container networking within a pipeline. A service is started just-in-time, health-checked before dependent containers use it, and auto-stopped when done.

```python
svc = dag.container().from_("postgres:16").as_service(args=["postgres"])
container = dag.container().with_service_binding("db", svc)
```

## Secrets

Secrets are passed to containers without exposing their values in logs, the filesystem, or cache.

Providers: `env://` (host env), `file://` (file), `cmd://` (command output), `vault://` (HashiCorp Vault), `op://` (1Password), `aws+sm://` (AWS Secrets Manager).

```python
container = container.with_secret_variable("API_KEY", my_secret)
container = container.with_mounted_secret("/etc/key", my_secret)
```
