---
title: "Git Worktree Workflows"
status: draft
author: "Khalid Zubair"
date: 2026-06-07
tags: ["git", "worktree", "workflows"]
sources:
  - "https://git-scm.com/docs/git-worktree"
  - "https://www.anthropic.com/engineering/claude-code-best-practices"
  - "https://incident.io/blog/shipping-faster-with-claude-code-and-git-worktrees"
last_audit_date: 2026-06-07
---

# Git Worktree Workflows

Git worktrees allow checking out multiple branches of the same repository into separate directories, all sharing a single `.git` directory. This enables parallel development workflows without stashing, cloning multiple copies of a repo, or switching branches back and forth.

## Requirements

- Git 2.5+ for basic worktree support
- Git 2.6+ for worktree `lock` functionality
- Git 2.27+ for worktree `add --orphan` (bare orphan branches)
- Git 2.19+ for worktree `list --porcelain` (scripting)

Verify your version:

```bash
git --version
```

## Common Setup

All workflows assume a base repository with a single main working tree:

```bash
# Start in your main repository
cd ~/projects/my-project

# Main working tree is at ~/projects/my-project
# Check it with:
git worktree list
```

The output of `git worktree list` shows every worktree currently registered, including the main one.

## Workflow: Parallel Feature Branches

Develop two features simultaneously without context switching or stash management.

```bash
# Create worktrees for two feature branches
git worktree add ../my-project-feature-a feature-a
git worktree add ../my-project-feature-b feature-b

# Each worktree is already on its respective branch — just cd and work
cd ../my-project-feature-a
# Ready to work on feature-a

cd ../my-project-feature-b
# Ready to work on feature-b
```

Each worktree is a fully functional working directory. Changes committed in one worktree are immediately visible to the others because they share the same object database.

```bash
# In worktree A, commit a change
cd ../my-project-feature-a
echo "change" >> file.txt
git add file.txt && git commit -m "feat: implement feature A"

# In worktree B, you can rebase onto the updated branch
cd ../my-project-feature-b
git fetch origin
git rebase origin/main
```

When a branch is merged and no longer needed:

```bash
cd ../my-project-feature-a
# Ensure all changes are committed
git add . && git commit -m "finish feature A"

# Go back to the main worktree
cd ~/projects/my-project

# Remove the worktree
git worktree remove ../my-project-feature-a

# If the worktree directory has uncommitted changes or is dirty:
git worktree remove --force ../my-project-feature-a

# Clean up the branch if merged
git branch -d feature-a
```

## Workflow: Hotfix Isolation

Emergency fix on the production branch while actively developing features.

```bash
# From the main worktree on main
cd ~/projects/my-project

# Create a hotfix worktree based on the production branch
git worktree add ../my-project-hotfix production

# Apply the fix
cd ../my-project-hotfix
git checkout -b hotfix/security-patch
# make changes...
git add . && git commit -m "fix: patch XSS vulnerability"

# Push and create PR
git push origin hotfix/security-patch

# After merge, clean up
cd ~/projects/my-project
git worktree remove ../my-project-hotfix
git branch -d hotfix/security-patch
```

The feature worktrees remain untouched throughout the entire hotfix lifecycle. No stashing, no interrupted rebase, no partial commits.

## Workflow: PR Review Sandboxes

Check out a PR branch for local review, testing, or inspection without affecting your current work.

```bash
# Fetch the PR ref
cd ~/projects/my-project
git fetch origin pull/42/head:review/pr-42

# Create a worktree for the PR review
git worktree add ../my-project-review-pr-42 review/pr-42

# Run tests, inspect code, check build
cd ../my-project-review-pr-42
npm test
npm run build
```

This is especially useful for AI-assisted workflows where a reviewer needs to examine the actual file tree, run tests, or check compilation before approving.

```bash
# After review is done, clean up
cd ~/projects/my-project
git worktree remove ../my-project-review-pr-42
git branch -D review/pr-42
```

## Workflow: Long-Running Experiments

Isolate a risky or long-running experimental branch so it does not interfere with daily work.

```bash
# Create a dedicated worktree for the experiment
git worktree add ../my-project-experiment

# Set up the experiment branch
cd ../my-project-experiment
git checkout -b experiment/new-architecture

# Work on the experiment independently for days or weeks
# without ever touching the main worktree
```

The experiment worktree maintains its own index, staging area, and working tree state. It can have its own `.env` files, local config overrides, or even a different Node/npm version via `.nvmrc` or direnv.

```bash
# The experiment has its own direnv/.envrc
cat ../my-project-experiment/.envrc
# use node 20
# export EXPERIMENT_MODE=true

# The main worktree remains on stable tooling
cat ~/projects/my-project/.envrc
# use node 18
```

When the experiment is ready to merge or be abandoned:

```bash
# Merge back
cd ../my-project-experiment
git checkout main
git merge experiment/new-architecture
git push origin main

# Clean up
cd ~/projects/my-project
git worktree remove ../my-project-experiment
git branch -d experiment/new-architecture
```

## Workflow: Stacked Branches

Manage dependent branches (a stack of changes where each branch builds on the previous) using separate worktrees.

```bash
# Start from main
git checkout main

# Create the base branch
git checkout -b step-1
echo "change 1" >> file.txt
git add . && git commit -m "step 1"

# Switch back to main to release step-1
git checkout main

# Create a worktree for step-2 based on step-1
git worktree add ../my-project-step-2 step-1
cd ../my-project-step-2
git checkout -b step-2
echo "change 2" >> file.txt
git add . && git commit -m "step 2"

# Go back to main worktree; use --detach since step-2 is checked out in step-2 worktree
cd ~/projects/my-project
git worktree add --detach ../my-project-step-3 step-2
cd ../my-project-step-3
git checkout -b step-3
echo "change 3" >> file.txt
git add . && git commit -m "step 3"
```

Each worktree corresponds to one branch in the stack. You can work on any layer independently. When the base branch changes, rebase the dependent worktrees:

```bash
# Step 1 needs changes after review (in the main worktree)
cd ~/projects/my-project
git checkout step-1
# Make changes...
git add . && git commit -m "step 1: address review feedback"

# Switch back to main to release step-1
git checkout main

# Rebase step-2 and step-3
cd ../my-project-step-2
git rebase step-1

cd ../my-project-step-3
git rebase step-2
```

Visualize the stack:

```bash
git worktree list
# /home/user/projects/my-project          main
# /home/user/projects/my-project-step-2   step-2
# /home/user/projects/my-project-step-3   step-3
```

## Workflow: AI Agent Sessions

Dedicate one worktree per AI coding agent (Claude Code, GitHub Copilot, etc.) to prevent agents from interfering with each other or with your manual work.

```bash
# Create a worktree for an AI agent to work in
git worktree add ../my-project-agent-1

# Set up the agent worktree
cd ../my-project-agent-1
git checkout -b ai/feature-search

# Run the AI agent in this directory
# The agent can read, write, commit, and push freely
# without affecting any other worktree

# Create another worktree for a second agent
git worktree add ../my-project-agent-2

cd ../my-project-agent-2
git checkout -b ai/feature-auth

# Both agents run simultaneously, each in their own sandbox
```

Key advantages for AI agents:

- **Isolated context**: Each agent sees only its own files and git state.
- **No conflicts**: Agents cannot accidentally overwrite each other's work or your in-progress changes.
- **Separate branches**: Each agent operates on its own branch with a clear ownership boundary.
- **Independent tooling**: Each worktree can have its own `.claude.json`, `.cursorrules`, or agent configuration.
- **Parallel execution**: Agents can run at the same time, each making commits, running tests, and pushing to their own remote branches.

For a tool that wraps git worktree specifically for this workflow, see [Worktrunk](../../dev-environments/worktrunk/overview.md).

```bash
# Agent A might have its own config
cat ../my-project-agent-1/.claude.json
#  { "permissions": ["read", "write"] }

# Agent B has different instructions
cat ../my-project-agent-2/INSTRUCTIONS.md
#  Implement the authentication module using JWT

# The main worktree is untouched — you can continue working
# or review PRs while agents run.
```

When the agent finishes:

```bash
# Review and merge the agent's work from the main worktree
cd ~/projects/my-project
git fetch origin ai/feature-search
git log origin/ai/feature-search

# Clean up the agent worktree
git worktree remove ../my-project-agent-1
git branch -d ai/feature-search
```

## Workflow: CI/Build Verification

Test a specific branch's build without interrupting your current development session.

```bash
# From your main worktree on a feature branch
cd ~/projects/my-project

# Create a worktree from the branch you want to test
git worktree add ../my-project-verify-ci origin/main

# Run the full CI pipeline locally
cd ../my-project-verify-ci
npm ci && npm run build && npm test

# Or test a specific PR/commit
git fetch origin pull/57/head:ci/test-pr-57
git worktree add ../my-project-ci-test ci/test-pr-57
cd ../my-project-ci-test
npm run typecheck && npm run lint
```

This avoids the common cycle of `git stash`, `git checkout main`, run tests, `git checkout feature`, `git stash pop` — which risks losing stashed changes or forgetting to restore the working state.

```bash
# Verify a release candidate without touching development
git worktree add ../my-project-rc-v2.0 v2.0-rc
cd ../my-project-rc-v2.0
npm run build:production
# If build fails, investigate without interrupting feature work

# Clean up
cd ~/projects/my-project
git worktree remove ../my-project-rc-v2.0
```

## Worktree Management Commands

### List all worktrees

```bash
git worktree list
# /home/user/projects/my-project          main        [81b5e1c]
# /home/user/projects/my-project-feature   feature-a  [a3f2b1d]
# /home/user/projects/my-project-hotfix   production  [c7e8d9f]
```

### Lock a worktree

Prevent a worktree from being pruned or removed accidentally:

```bash
git worktree lock ../my-project-experiment --reason "Long-running experiment, do not remove"
```

### Move a worktree

Relocate a worktree directory:

```bash
git worktree move ../my-project-feature ../archived/my-project-feature
```

### Prune stale worktree records

Remove worktree administrative records for worktrees that no longer exist:

```bash
git worktree prune
```

### Repair worktree after directory move

If a worktree directory was moved without `git worktree move`:

```bash
git worktree repair /new/path/to/worktree
```

## Restrictions and Caveats

- A branch can be checked out in only one worktree at a time. To check it out elsewhere, either move it or use `git worktree add --detach` for a detached HEAD.
- Submodules are shared by default but their working trees are independent. Each worktree sees the same submodule commit.
- The main worktree (where `.git` lives) cannot be removed — only secondary worktrees can be pruned.
- `git gc` may need `--prune=now` to clean objects still referenced by worktree reflogs. Use `git worktree prune` first.
- Some editors (VS Code, IntelliJ) may index worktrees separately. Use `code ../my-project-worktree` to open a new window for that worktree.
- CI tools and git hooks that assume `.git` is at the project root may need adjustment for worktrees (which use `.git` as a file, not a directory).

---

## See Also

- [Git Worktree Overview](./overview.md) — Core concepts, use cases, and subcommand overview
- [CLI Reference](./cli-reference.md) — All `git worktree` subcommands with flags and examples
