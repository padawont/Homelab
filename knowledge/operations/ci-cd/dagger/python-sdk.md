---
title: "Dagger — Python SDK"
status: draft
author: "padawont"
date: 2026-07-22
tags: ["dagger", "python", "sdk", "async"]
sources:
  - url: "https://pypi.org/project/dagger-io/"
    title: "dagger-io on PyPI"
  - url: "https://docs.dagger.io/getting-started/quickstarts/basics"
    title: "Dagger Python Quickstart"
  - url: "https://github.com/dagger/dagger/tree/main/sdk/python"
    title: "Dagger Python SDK on GitHub"
last_audit_date: 2026-07-22
---

# Dagger Python SDK

The Python SDK (`dagger-io`) is the primary SDK for this repository. Pipelines are defined as async Python code using type-safe decorators.

## Installation

```bash
pip install dagger-io
```

Requires Python >= 3.10.

## Core Pattern

```python
import sys
import anyio
import dagger
from dagger import dag

async def main():
    async with dagger.connection():
        result = await (
            dag.container()
            .from_("python:alpine")
            .with_exec(["python", "-V"])
            .stdout()
        )
        print(result)

anyio.run(main)
```

Key points:
- `dagger.connection()` opens a session to the Dagger Engine (async context manager)
- `dag` is a global singleton for accessing the Dagger API root
- All container mutations return new `Container` objects (immutable builder pattern)
- `await` only on terminal/scalar values — non-scalar returns (Container, Directory) are lazy

## Module Development

### `@object_type` and `@function` Decorators

```python
from dagger import function, object_type, dag

@object_type
class MyModule:
    @function
    def build(self, src: dagger.Directory) -> dagger.Container:
        return (
            dag.container()
            .from_("node:21-slim")
            .with_directory("/src", src)
            .with_workdir("/src")
            .with_exec(["npm", "install"])
            .with_exec(["npm", "run", "build"])
        )

    @function
    async def test(self, src: dagger.Directory) -> str:
        return await (
            self.build(src)
            .with_exec(["npm", "test"])
            .stdout()
        )
```

### Annotated Arguments

Use `typing.Annotated` for richer argument metadata:

```python
from typing import Annotated
from dagger import DefaultPath, Doc, Ignore

@function
async def test(
    self,
    source: Annotated[
        dagger.Directory,
        DefaultPath("/"),
        Doc("Source directory"),
        Ignore([".git", "node_modules"]),
    ],
) -> str: ...
```

## Working Example: Build, Test, Lint

```python
import anyio
from dagger import function, object_type, dag

@object_type
class CiPipeline:
    @function
    def base(self, src: dagger.Directory) -> dagger.Container:
        return (
            dag.container()
            .from_("python:3.12-slim")
            .with_directory("/src", src)
            .with_workdir("/src")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
        )

    @function
    async def lint(self, src: dagger.Directory) -> str:
        return await (
            self.base(src)
            .with_exec(["pip", "install", "ruff"])
            .with_exec(["ruff", "check", "."])
            .stdout()
        )

    @function
    async def test(self, src: dagger.Directory) -> str:
        return await (
            self.base(src)
            .with_exec(["pip", "install", "pytest"])
            .with_exec(["pytest", "-v"])
            .stdout()
        )
```

## Local Development Workflow

```bash
dagger init --sdk=python --name=ci-pipeline
dagger call test --source=.     # run locally
dagger call lint --source=.     # run locally
dagger check                     # verify all functions compile
```

## Debugging

Pass `dagger.Config(log_output=sys.stderr)` to stream engine logs:

```python
async with dagger.connection(dagger.Config(log_output=sys.stderr)):
    ...
```
