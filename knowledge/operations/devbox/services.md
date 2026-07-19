---
title: "Devbox — Services"
status: exploring
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "services", "process-compose", "databases"]
sources:
  - "https://www.jetify.com/docs/devbox/guides/services/"
last_audit_date: 2026-05-24
---

# Services

Devbox manages background processes (databases, caches, web servers) using process-compose.

## Starting Services

```bash
devbox services up
```

Start in the background:

```bash
devbox services up -b
```

Start a specific service:

```bash
devbox services up postgresql
```

## Managing Services

```bash
devbox services ls          # list running services
devbox services restart     # restart all services
devbox services stop        # stop all services
devbox services stop postgresql  # stop a specific service
devbox services attach      # attach process-compose TUI to background services
```

## Custom Services

Define custom services with a `process-compose.yml` in the project root:

```yaml
version: "0.5"
processes:
  django:
    command: python manage.py runserver
    availability:
      restart: "always"
```

## Plugins with Pre-Configured Services

The following plugins provide a pre-configured service: Apache, Caddy, Nginx, PostgreSQL, Redis, Valkey, PHP.
