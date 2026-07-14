---
title: "Worktrunk Troubleshooting"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags: ["worktrunk", "troubleshooting", "faq"]
sources:
  - "https://worktrunk.dev/faq/"
last_audit_date: 2026-06-07
---

# Worktrunk Troubleshooting

Common Worktrunk issues, their causes, and solutions.

## Shell Integration Not Working

**Symptom:** `wt switch` does not auto-cd into the new worktree directory. Shell completions are missing. `wt` is not found as a shell function.

**Causes:**
- The shell integration was never installed, or was installed before the shell config was sourced.
- The rc file line was added but the shell has not been restarted.
- Another tool or config override removed the Worktrunk shell function.

**Solutions:**

1. Run `wt config show` to inspect your current configuration state:
   ```bash
   wt config show
   ```
   This displays the location and contents of your user config and project config. For a deeper diagnostic that also checks CI tools, commit generation, and version information, use `--full`:
   ```bash
   wt config show --full
   ```
   Review the output for any misconfigurations or missing values. The official FAQ recommends including the output of `wt config show` when reporting issues.

2. Re-run the installation:
   ```bash
   wt config shell install
   ```

3. Verify the rc file was modified:
   - **Bash:** `~/.bashrc` should contain a line sourcing the Worktrunk shell function.
   - **Zsh:** `~/.zshrc` (or `$ZDOTDIR/.zshrc`) should contain the same.
   - **Fish:** A `wt.fish` function should exist under `~/.config/fish/functions/`.
   - **Nushell:** A `wt.nu` file should exist under the vendor autoload directory (`$nu.data-dir`/vendor/autoload).
   - **PowerShell:** Profile files under `Documents/PowerShell/` and `Documents/WindowsPowerShell/` should contain the function.

4. Restart your shell or source the config:
   ```bash
   source ~/.bashrc    # bash
   source ~/.zshrc     # zsh
   ```

5. If the function is present but `wt switch` still does not cd, inspect the shell function definition in the rc file. It should look like an eval'd function that calls the Worktrunk binary then changes directory.

## Windows Terminal `wt` Conflict

**Symptom:** Running `wt` on Windows launches Windows Terminal instead of Worktrunk.

**Cause:** Windows Terminal ships with a built-in `wt.exe` alias registered system-wide. When both are on `PATH`, Windows Terminal's `wt` takes precedence.

**Solutions:**

1. Use the `git-wt` binary name instead:
   ```bash
   git wt switch --create feature
   ```
   Worktrunk registers itself as `git-wt` during installation, so all `wt` commands work as `git wt` subcommands.

2. Disable the Windows Terminal alias by removing it from `PATHEXT` or renaming the `wt.exe` that comes with Windows Terminal (not recommended).

3. Create a shell alias or wrapper script that calls the Worktrunk binary by its full path.

## Stale Agent Markers

**Symptom:** `wt switch` or `wt list` shows a marker indicator for a worktree whose agent process has been killed (e.g., Claude Code was force-terminated). The marker prevents switching or creates confusion about active sessions.

**Cause:** Worktrunk sets a marker in `.git/` (via `git config worktrunk.<branch>.marker`) when an agent starts. If the agent is killed without going through the normal shutdown path, the marker is never cleared.

**Solution:** Clear the stale marker manually:
```bash
wt config state marker clear
```
This removes all worktrunk markers from the git config. Run `wt list` afterward to verify the stale entry is gone.

## C Compilation Errors During Install

**Symptom:** `cargo install worktrunk` fails with errors related to tree-sitter, C99 mode, or `le16toh` being undefined.

**Cause:** Worktrunk's syntax highlighting feature requires a C99-compatible compiler for the tree-sitter C grammar parser. Older systems or minimal Docker images may lack this.

**Solution:** Install without syntax highlighting:
```bash
cargo install worktrunk --no-default-features --features cli
```
This disables bash syntax highlighting in command output but keeps all core Worktrunk functionality.

## PR Checkout Auth Failures

**Symptom:** `wt switch pr:123` fails with an authentication error or "not found" message.

**Cause:** Worktrunk uses `gh` (GitHub CLI) or `glab` (GitLab CLI) to resolve PR numbers to branch names. If the CLI is not installed or not authenticated, the PR lookup fails.

**Solutions:**

1. Ensure the GitHub CLI is installed:
   ```bash
   gh --version
   ```

2. Authenticate:
   ```bash
   gh auth login
   ```

3. For GitLab repositories, ensure `glab` is installed and authenticated instead:
   ```bash
   glab auth login
   ```

4. Verify authentication status:
   ```bash
   gh auth status
   ```

## Bare Repo Path Detection

**Symptom:** Worktrunk reports an issue detecting the repository path or shows unexpected behavior in a repo with a bare `.git` or `.bare` directory structure.

**Cause:** Some repositories use a bare repo layout where the git directory is not the standard `.git` folder inside the working tree.

**Solution:** Worktrunk detects bare repos at `.git` or `.bare` paths and offers a fix automatically. If the automated detection does not work, configure the path explicitly in the project's `.config/wt.toml`. Refer to the error message output — it typically includes a suggested fix command.

## Default Branch Detection - Stale Cache

**Symptom:** `wt switch --create` bases the new branch on the wrong default branch (e.g., creates a branch off `master` when the remote renamed it to `main`).

**Cause:** Worktrunk caches the default branch name locally. If the remote's default branch changes, the cache becomes stale.

**Solution:** Clear the cached default branch:
```bash
wt config state default-branch clear
```
Worktrunk will re-detect the default branch from the remote on the next command.

## What Files Does Worktrunk Create?

Worktrunk creates files in four locations:

| Location | Contents | How to Remove |
|---|---|---|
| Worktree directories (sibling to main repo, e.g. `../repo.branch`) | Full working tree for each branch | `wt remove <branch>` |
| `~/.config/worktrunk/config.toml` | User preferences | `rm ~/.config/worktrunk/config.toml` |
| `.config/wt.toml` (inside repo) | Project hooks, checked into version control | `rm .config/wt.toml` (and commit) |
| Shell integration files | Rc file modifications and function files | `wt config shell uninstall` |
| `.git/wt/` internal metadata | Caches, logs, markers, trash | `wt config state clear` |

**What Worktrunk does NOT create:**
- No files outside `.git/`, config directories, or worktree directories.
- No global git hooks.
- No modifications to `~/.gitconfig`.
- No long-running background processes or daemons.

## What Commands Does Worktrunk Execute?

Worktrunk runs commands in four contexts:

1. **Internal git commands** — All git operations (add, branch, merge, worktree, etc.) are performed by Worktrunk internally.
2. **`gh` / `glab`** — Used for CI status queries and PR number resolution. Requires installation and authentication.
3. **User hooks** (`~/.config/worktrunk/config.toml`) — Personal automation scripts run on lifecycle events (post-start, pre-merge, post-merge, etc.). Defined by the user, no approval required.
4. **Project hooks** (`.config/wt.toml`) — Repository-specific automation. Requires approval on first run. Approved commands are saved to `~/.config/worktrunk/approvals.toml`.

Use `--yes` to bypass approval prompts (useful for CI or automation).

All hook executions are logged to `.git/wt/logs/commands.jsonl`:
```bash
# View recent commands
tail -5 .git/wt/logs/commands.jsonl | jq .

# Find failed commands
jq 'select(.exit != 0 and .exit != null)' .git/wt/logs/commands.jsonl
```

## Verbose Debugging

Worktrunk supports three verbosity levels:

| Level | Output | Use Case |
|---|---|---|
| (none) | Warnings only on stderr | Normal use |
| `-v` | Warnings + info: hook output, alias template resolution | Debugging hooks/aliases |
| `-vv` | Same as `-v`; writes `trace.log`, `subprocess.log`, and `diagnostic.md` to `.git/wt/logs/` | Filing a bug report |

At `-vv`:
- **`trace.log`** — Bounded preview (~1000 lines) of `[wt-trace]` timing records and subprocess calls.
- **`subprocess.log`** — Raw uncapped stdout/stderr of every subprocess Worktrunk spawns (can be multi-MB).
- **`diagnostic.md`** — Markdown bug-report bundle that inlines `trace.log`. Worktrunk prints a `gh gist create` command pointing at it for easy sharing.

Override the baseline with `RUST_LOG`:
```bash
RUST_LOG=debug wt -v   # Lifts -v to debug-on-stderr
```

## Windows Support

**Symptom:** Worktrunk behaves unexpectedly on Windows, hooks fail, or `wt switch` crashes.

**Limitations and requirements:**

- **Git for Windows is required.** Hooks use bash syntax and execute via Git Bash, even when PowerShell is the interactive shell.
- **`wt switch` interactive picker is unavailable.** The picker uses `skim`, which does not support Windows. Use `wt list` and `wt switch <branch>` (with the branch name as an argument) instead.
- **Windows Terminal `wt` conflict.** See the [Windows Terminal conflict section](#windows-terminal-wt-conflict) above.
- **PowerShell detection:** When running from cmd.exe or PowerShell, both PowerShell 7+ and Windows PowerShell 5.1 profile files are created automatically. When running from Git Bash or MSYS2, PowerShell is skipped. Use `wt config shell install powershell` to create the profiles explicitly.

## Stacked Branch Support

**Symptom:** You need to work on multiple dependent branches (a stack), but Worktrunk treats each branch as independent.

**Cause:** Worktrunk does not natively support stacked-branch workflows. Stacked branches are a large design space that Worktrunk treats as an extension rather than a built-in.

**Solution:** Use the community tool `worktrunk-sync`:
```bash
cargo install worktrunk-sync
```
`worktrunk-sync` auto-detects the branch dependency tree from git history and rebases each branch onto its parent in topological order. It installs as a custom subcommand and is invoked as:
```bash
wt sync
```

---

## See Also

- [Git Worktree Troubleshooting](../../version-control/git/worktree/troubleshooting.md) — Underlying worktree-level issues
- [CLI Reference](./cli-reference.md) — All `wt` commands with flags and examples
