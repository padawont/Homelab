---
title: "Devbox — Global Packages"
status: exploring
author: "Khalid"
date: 2026-05-24
tags: ["devbox", "global", "package-management"]
sources:
  - "https://www.jetify.com/docs/devbox/devbox-global/"
last_audit_date: 2026-05-24
---

# Global Packages (devbox global)

Install tools available across all Devbox projects:

```bash
devbox global add ripgrep vim git
devbox global list
devbox global rm ripgrep
```

## Using Global Packages in Your Host Shell

```bash
eval "$(devbox global shellenv --init-hook)"
```

Add to `~/.bashrc` or `~/.zshrc`. For Fish, add to `~/.config/fish/config.fish`:

```bash
devbox global shellenv --init-hook | source
```

## Sharing Global Config via Git

```bash
devbox global push <remote>
devbox global pull <remote>
```

Your global config is stored at `$XDG_DATA_HOME/devbox/global/default` (defaults to `~/.local/share/devbox/global/default`).
