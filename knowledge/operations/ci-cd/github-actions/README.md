# GitHub Actions & OpenCode

CI/CD platform and running OpenCode agents within GitHub Actions workflows.

## Contents

- [overview.md](./overview.md) — Topic hub and index

### Workflow Structure
- [workflow-syntax-basics.md](./workflow-syntax-basics.md) — name, on, jobs, steps
- [workflow-triggers.md](./workflow-triggers.md) — push, pull_request, schedule, workflow_dispatch
- [workflow-triggers-paths.md](./workflow-triggers-paths.md) — paths, paths-ignore
- [workflow-triggers-types.md](./workflow-triggers-types.md) — opened, synchronized, labeled, closed

### Jobs
- [jobs-runners.md](./jobs-runners.md) — runs-on, ubuntu-latest, self-hosted
- [jobs-strategy-matrix.md](./jobs-strategy-matrix.md) — Matrix builds, include, exclude
- [jobs-concurrency.md](./jobs-concurrency.md) — concurrency groups, cancel-in-progress
- [jobs-needs.md](./jobs-needs.md) — Job dependencies and ordering
- [jobs-outputs.md](./jobs-outputs.md) — Job outputs to pass data
- [jobs-conditionals.md](./jobs-conditionals.md) — if: expressions, github.* context
- [jobs-timeout.md](./jobs-timeout.md) — timeout-minutes

### Steps
- [steps-uses.md](./steps-uses.md) — actions/checkout, reusable actions reference
- [steps-run.md](./steps-run.md) — Run shell commands
- [steps-env.md](./steps-env.md) — Step-level environment variables
- [steps-id.md](./steps-id.md) — Step IDs for outputs
- [steps-if-conditionals.md](./steps-if-conditionals.md) — if: on steps
- [steps-working-directory.md](./steps-working-directory.md) — working-directory

### Secrets & Variables
- [env-vs-secrets.md](./env-vs-secrets.md) — env vs secrets, when each
- [secrets-org-repo.md](./secrets-org-repo.md) — Organization vs repo secrets
- [secrets-usage.md](./secrets-usage.md) — ${{ secrets.MY_SECRET }}
- [secrets-environment.md](./secrets-environment.md) — Environment-level secrets

### GitHub Token
- [github-token-permissions.md](./github-token-permissions.md) — GITHUB_TOKEN default scopes
- [github-token-custom.md](./github-token-custom.md) — permissions block

### Contexts
- [github-context.md](./github-context.md) — github object fields reference
- [env-context.md](./env-context.md) — env context fields
- [vars-context.md](./vars-context.md) — vars for org-level variables
- [needs-context.md](./needs-context.md) — needs.job.outputs, needs.job.result

### Actions & Reusable Workflows
- [actions-marketplace.md](./actions-marketplace.md) — Finding/sharing actions
- [reusable-workflows-intro.md](./reusable-workflows-intro.md) — workflow_call trigger
- [reusable-workflows-inputs.md](./reusable-workflows-inputs.md) — Workflow inputs
- [reusable-workflows-secrets.md](./reusable-workflows-secrets.md) — Passing secrets to reusable workflows
- [reusable-workflows-strategy.md](./reusable-workflows-strategy.md) — Matrix for reusable workflows

### OpenCode in CI
- [opencode-installation.md](./opencode-installation.md) — npm install -g @opencode/cli
- [opencode-config-in-ci.md](./opencode-config-in-ci.md) — opencode.json in CI
- [opencode-auth-in-ci.md](./opencode-auth-in-ci.md) — GitHub token or API keys
- [opencode-agent-issue-comment.md](./opencode-agent-issue-comment.md) — Run agent responding to issue
- [opencode-agent-pr-review.md](./opencode-agent-pr-review.md) — Run agent on PR diff
- [opencode-agent-custom.md](./opencode-agent-custom.md) — Arbitrary agent invocation
- [opencode-caching-config.md](./opencode-caching-config.md) — Cache .opencode/ directory
- [opencode-llm-provider.md](./opencode-llm-provider.md) — Configure LLM for agent in CI
- [opencode-permissions.md](./opencode-permissions.md) — Permission config for CI

### Python + uv in GHA
- [python-setup-uv.md](./python-setup-uv.md) — astral-sh/setup-uv action
- [python-cache-uv.md](./python-cache-uv.md) — uv caching in GHA (cache-dependency-glob)
- [python-run-pytest.md](./python-run-pytest.md) — Run pytest with uv in GHA
- [python-run-ruff.md](./python-run-ruff.md) — Lint with ruff in GHA
- [python-run-mypy.md](./python-run-mypy.md) — Type-check with mypy in GHA
- [python-run-ty.md](./python-run-ty.md) — Type-check with ty in GHA

### Deployment
- [deployment-fastapi.md](./deployment-fastapi.md) — Deploy FastAPI to cloud run
- [deployment-fastmcp.md](./deployment-fastmcp.md) — Deploy FastMCP to cloud run
- [deployment-docker.md](./deployment-docker.md) — Build and push Docker image
- [deployment-environments.md](./deployment-environments.md) — GHA Environments for approvals
- [deployment-continuous.md](./deployment-continuous.md) — Continuous deployment patterns

### Troubleshooting
- [troubleshooting.md](./troubleshooting.md) — Common CI failures
