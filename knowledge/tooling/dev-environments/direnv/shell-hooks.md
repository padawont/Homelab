---
title: "direnv — Shell Hook Setup"
status: draft
author: "Khalid"
date: 2026-05-24
tags: ["direnv", "shell", "bash", "zsh", "fish"]
sources:
  - "https://direnv.net/docs/hook.html"
last_audit_date: 2026-05-24
---

# Shell Hook Setup

After installing, hook direnv into your shell. Restart your shell after adding the hook.

## Bash (`~/.bashrc`)

```bash
eval "$(direnv hook bash)"
```

## Zsh (`~/.zshrc`)

```bash
eval "$(direnv hook zsh)"
```

## Oh My Zsh

Add `direnv` to the plugins array in `.zshrc`:

```bash
plugins=(... direnv)
```

## Fish (`~/.config/fish/config.fish`)

```fish
direnv hook fish | source
```

Fish supports three modes via `direnv_fish_mode`:

```fish
set -g direnv_fish_mode eval_on_arrow     # default — trigger on prompt + arrow nav
set -g direnv_fish_mode eval_after_arrow  # trigger on prompt + after arrow nav
set -g direnv_fish_mode disable_arrow     # trigger on prompt only
```

## Other Shells

| Shell | Hook command | File |
|---|---|---|
| Tcsh | `` eval `direnv hook tcsh` `` | `~/.cshrc` |
| Elvish | `direnv hook elvish > ~/.config/elvish/lib/direnv.elv` then `use direnv` in `rc.elv` | `~/.config/elvish/rc.elv` |
| PowerShell | `Invoke-Expression "$(direnv hook pwsh)"` | `$PROFILE` |
| Nushell | Add hook to `$env.config.hooks.env_change.PWD` | `config.nu` |
| Murex | `direnv hook murex -> source` | `~/.murex_profile` |
