---
title: "Devbox"
status: exploring
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "nix", "developer-experience", "reproducible-environments"]
sources:
  - "https://www.jetify.com/docs/devbox/"
  - "https://www.jetify.com/docs/devbox/quickstart/"
  - "https://www.jetify.com/docs/devbox/installing-devbox/"
  - "https://www.jetify.com/docs/devbox/configuration/"
last_audit_date: 2026-05-24
---

# Devbox

Devbox is a CLI tool that creates isolated, reproducible development environments using the Nix package manager. You define your toolchain in a `devbox.json` file, and Devbox provisions the exact versions in an isolated shell.

## How It Works

Devbox uses Nix under the hood but abstracts away the Nix language. Packages are installed into the Nix store and linked into your project environment. The result is a shell with only the tools you declared — no conflicts with system packages or other projects.

## Quickstart

```bash
mkdir my-project && cd my-project
devbox init                        # creates devbox.json
devbox add python@3.10 ripgrep     # add packages
devbox shell                        # enter isolated shell
exit                                # leave shell
```

Commit the generated `devbox.json` and `devbox.lock` files to source control so all contributors get the same environment.

## Detailed Guides

| File | Description |
|---|---|
| [installation.md](./installation.md) | Install, update, and version-pin Devbox |
| [configuration.md](./configuration.md) | `devbox.json` reference — packages, env, scripts, plugins |
| [cli-reference.md](./cli-reference.md) | Full CLI commands reference |
| [services.md](./services.md) | Background services (databases, caches) with process-compose |
| [ide-integration.md](./ide-integration.md) | VS Code, direnv, and manual IDE setup |
| [plugins.md](./plugins.md) | Built-in and custom plugins |
| [global-packages.md](./global-packages.md) | Devbox as a global package manager |
| [usage.md](./usage.md) | End-to-end workflow, Docker integration, global vs project, OpenChoreo pilot patterns |
| [best-practices.md](./best-practices.md) | Best practices, good examples, and common pitfalls |
| [troubleshooting.md](./troubleshooting.md) | FAQ, common issues, and uninstall |
