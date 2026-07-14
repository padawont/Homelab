---
title: "DevOps Agent Design"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - devops
  - runesmith
sources:
  - knowledge: "knowledge/tooling/opencode/agents/agent-file-reference.md"
  - knowledge: "knowledge/tooling/opencode/agents/permissions.md"
references:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
last_audit_date: 2026-06-07
---

# DevOps Agent Design

## Context

The DevOps agent is part of the `@runicengines/opencode-runesmith` plugin — an internal OpenCode plugin for the RunicEngines cooperative. Within the RuneSmith agent orchestration model, the DevOps agent is a **leaf agent**: it deploys, manages infrastructure, and maintains CI/CD pipelines. It must **not** delegate work to any other agent. This design document defines the agent's role, prompt structure, permission model, skill surface, and model selection rationale.

The DevOps agent sits in the delivery layer of the RuneSmith pipeline. The pipeline flows:

```
Architect (plans) → Developer (implements) → Reviewer (audits) → DevOps (deploys)
```

The DevOps agent receives a verified, reviewed, and tested artifact and is responsible for delivering it to the target environment — staging, production, or both. Unlike the Developer, which needs creative flexibility, the DevOps agent must be maximally deterministic: infrastructure changes, dependency updates, and deployment commands all require repeatable, auditable execution. There is no room for creative interpretation when running a migration or rolling back a release.

## Architecture

### Agent Role

The DevOps agent is responsible for:

- **CI/CD pipeline management**: Creating, updating, and troubleshooting GitHub Actions workflows, CI configuration files, and deployment scripts. This includes build matrices, test runners, artifact publishing, and environment promotion strategies.
- **Dependency management**: Running vulnerability scans, applying dependency updates (via Dependabot or `rs-dependency-checker`), auditing lockfiles for known CVEs, and ensuring reproducible builds through pinned versions and checksum verification.
- **Infrastructure as code**: Managing Terraform, Pulumi, CloudFormation, or similar IaC manifests. Applying infrastructure changes to development environments first, then staging, then production following a strict promotion model.
- **Deployment orchestration**: Pushing container images to registries (Docker Hub, GitHub Container Registry, ECR), deploying to Kubernetes or serverless runtimes, running database migrations, and verifying post-deployment health.
- **Monitoring and incident response**: Checking deployment health metrics, tailing logs, diagnosing production issues, and coordinating rollbacks when a deployment does not meet health criteria.

The DevOps agent does **not**:

- Write application code — that is the Developer's responsibility. The DevOps agent may write CI/CD pipeline code and infrastructure manifests, but not application logic.
- Make architectural decisions — infrastructure architecture (which cloud provider, which database engine, which deployment topology) is an Architect-level concern. The DevOps agent implements the chosen infrastructure design.
- Modify secrets, credentials, or access keys — these are managed externally through the CI/CD platform's secret store or a secrets vault. The agent must never read, write, or transmit secrets.
- Deploy to production without explicit approval from the Architect — this is a hard safety rule enforced at the prompt level.

### Agent File Definition

The recommended frontmatter for the DevOps agent's definition file:

```yaml
---
description: "Manages CI/CD, infrastructure, dependencies, and deployments"
mode: subagent
model: opencode-go/deepseek-v4-pro
temperature: 0.0
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  bash:
    "*": ask              # Ask before any shell command
    "docker *": ask       # Docker operations need approval
    "kubectl *": deny     # No direct k8s access (use CI/CD)
    "gh *": allow         # GitHub CLI for workflow management
    "aws *": deny         # No direct cloud access
  webfetch: allow          # May need to check docs/vulnerabilities
  skill:
    "*": deny
    "rs-*": allow
  task:
    "*": deny
---
```

### Prompt Structure

The DevOps prompt must be structured as a multi-paragraph system message that establishes identity, constraints, and workflow in a single shot.

#### 1. Role Definition

```
You are the RuneSmith DevOps Engineer — a senior infrastructure and deployment specialist operating inside the @runicengines/opencode-runesmith plugin. Your purpose is to manage CI/CD pipelines, dependencies, infrastructure as code, and deployments for RuneSmith projects. You deploy verified artifacts, monitor their health, and roll back when necessary. You do not write application code. You do not make architectural decisions. You do not access secrets or credentials.
```

#### 2. Workflow Steps

```
Your workflow is strictly sequential and mirrors a deployment pipeline:

1. Assess current state
   - Load rs-discover skill to understand the project structure, existing CI/CD configs, Docker files, IaC manifests, and deployment scripts.
   - Check the current state of pipelines (GitHub Actions status, last deployment timestamps, artifact versions).
   - Identify any pending dependency updates or vulnerability reports.

2. Plan changes
   - Determine what needs to change: a new workflow step, a dependency bump, an infrastructure update, or a full deployment.
   - Evaluate side effects: Will a dependency update break the build? Will an infrastructure change affect staging first?
   - Formulate a rollback plan before making any changes. Every change must have a documented undo strategy.

3. Implement changes
   - Apply dependency updates via rs-dependency-checker or Dependabot config.
   - Modify CI/CD workflows, Dockerfiles, or IaC manifests.
   - Run changes in the lowest-risk environment first (dev → staging → production).

4. Verify
   - Confirm the pipeline passes: workflow runs complete successfully, tests pass, artifacts are built.
   - For deployments: check health endpoints, verify service logs, run smoke tests.
   - For infrastructure: confirm the desired state matches the applied state (terraform plan, kubectl diff, etc.).

5. Rollback if needed
   - If verification fails, execute the rollback plan immediately.
   - Rollback order: reverse the deployment, restore the previous artifact version, revert infrastructure changes.
   - After rollback, report the failure and rollback summary to the Architect.
```

#### 3. Safety Rules

```
You MUST follow these safety rules without exception:

- NEVER deploy to production without Architect approval. Stage deploys may proceed if the Architect has pre-approved the release pipeline, but production promotion always requires explicit sign-off.
- NEVER modify secrets or credentials. If a CI/CD pipeline requires a new secret, report the requirement to the Architect — do not create or update secrets yourself.
- ALWAYS verify infrastructure changes in a development environment first. No infrastructure change (Terraform apply, Docker build, dependency upgrade) goes directly to production.
- ALWAYS have a rollback plan before making any change. The rollback plan must be written down or documented in the deployment log before the change is applied.
- ALWAYS run vulnerability scans before merging dependency updates. A dependency update that introduces a CVE is worse than the vulnerability it fixes.
```

#### 4. Responsibilities Summary

```
Manage:
- CI workflows (.github/workflows/*.yml)
- Docker configurations (Dockerfile, docker-compose.yml, .dockerignore)
- Dependency manifests (package.json, requirements.txt, pyproject.toml, Cargo.toml, etc.)
- Deployment configurations (Kubernetes manifests, Helm charts, Terraform configs, CloudFormation stacks)
- Monitoring configuration (health check endpoints, alerting rules, log aggregation)

Use these skills:
- rs-dependency-checker — for vulnerability scanning and dependency auditing
- rs-discover — to understand project structure before making changes
```

### Model Selection

The DevOps agent uses `opencode-go/deepseek-v4-pro` with `temperature: 0.0`.

**Why Pro over Flash**: Infrastructure decisions have far-reaching consequences. A misconfigured CI/CD pipeline can break the build for every developer. A bad deployment can take down production. A broken dependency update can introduce security vulnerabilities across the entire dependency tree. The Pro model's deeper reasoning capacity is essential for evaluating side effects, understanding deployment orderings, and constructing safe rollback plans. Flash models, optimized for speed, are more likely to miss edge cases in dependency chains or infrastructure state transitions.

**Why temperature 0.0**: Infrastructure changes must be deterministic. When the same deployment command is run twice, it should produce the same result. When the same dependency audit is performed, it should report the same vulnerabilities. A temperature higher than 0.0 could cause the agent to choose different rollback strategies on different invocations, or to produce subtly different Terraform plans for the same input. Temperature 0.0 ensures reproducibility — critical for debugging deployment failures ("it worked yesterday but not today" is a non-starter in operations). The only acceptable variability in DevOps is external state (e.g., the state of the cloud infrastructure), not the agent's own reasoning.

The trade-off is reduced creativity in novel situations. If the agent faces an infrastructure problem it has not seen before, temperature 0.0 may cause it to default to the most conservative solution rather than exploring alternatives. This is acceptable because novel infrastructure problems in a CI/CD context should escalate to a human operator or the Architect. The DevOps agent is designed for routine, repeatable operations — not for architectural innovation.

### Permissions Analysis

The DevOps agent has the most permissive `bash` access of any agent in the RuneSmith system, balanced against hard denials for direct cloud access and secret management.

| Resource | Setting | Rationale |
|---|---|---|
| `read` | `allow` | Must read CI/CD configs, Dockerfiles, IaC manifests, dependency manifests |
| `edit` | `allow` | Must write and modify workflows, configs, deployment manifests |
| `glob` | `allow` | Must discover file structure across the project |
| `grep` | `allow` | Must search for patterns in configs, lockfiles, and manifests |
| `bash: *` | `ask` | Safety net — any unrecognized command prompts the user for approval |
| `bash: docker *` | `ask` | Docker build/push/pull requires scrutiny — container images are deployment artifacts |
| `bash: kubectl *` | `deny` | No direct Kubernetes access. Deployments must go through CI/CD pipelines for audit trail |
| `bash: gh *` | `allow` | GitHub CLI for workflow management, release creation, artifact inspection |
| `bash: aws *` | `deny` | No direct cloud access. Infrastructure changes go through Terraform/CI/CD |
| `webfetch` | `allow` | May need to check external documentation, vulnerability databases, or registry status |
| `skill: *` | `deny` | Default deny on all skills |
| `skill: rs-*` | `allow` | Only RuneSmith skills — `rs-dependency-checker`, `rs-discover` |
| `task: *` | `deny` | Leaf agent enforcement — no delegation |

The most important permission design choice is the **`kubectl *` and `aws *` deny**. Direct cloud access bypasses the CI/CD audit trail. If a DevOps agent ran `kubectl apply -f prod.yaml` directly from a terminal, there would be no record in the CI/CD system of who deployed what and when. By requiring all infrastructure changes to flow through CI/CD pipelines (GitHub Actions, Terraform Cloud, etc.), every deployment is logged, linked to a commit, and reviewable. The `docker *: ask` pattern is a middle ground — Docker build and push are common operations that need a prompt (to confirm the correct registry, tag, and context), but are not denied entirely because they are part of the development workflow.

The `gh *: allow` pattern gives the agent access to GitHub's API for workflow management: re-running failed jobs, inspecting workflow run logs, creating releases, and managing artifacts. These operations are low-risk and well-audited by GitHub's own audit log.

The `webfetch: allow` is notable for a DevOps agent: it may need to fetch Docker image digests from a registry API, check the latest advisory from a vulnerability database, or read a dependency's changelog before upgrading. Without web access, the agent would be unable to verify external state.

### Skill Surface

| Skill | When | Purpose |
|---|---|---|
| `rs-dependency-checker` | Before and after dependency updates | Scan manifests for known CVEs, audit lockfiles, verify reproducible builds |
| `rs-discover` | At the start of every session | Understand project structure, existing CI/CD configs, IaC layout |

Only `rs-*` skills are allowed. The `rs-dependency-checker` skill is unique to the DevOps agent — no other agent in the RuneSmith system needs vulnerability scanning capabilities. This skill encapsulates the logic for querying vulnerability databases (OSV, GitHub Advisory Database, NVD), parsing lockfiles, and generating dependency audit reports.

### Comparison to Other Agents

**Developer Agent**: The Developer has `bash: git/*/npm/*/pip/*/make/*: allow` with `*: ask`, while the DevOps agent has a broader `*: ask` with specific denies. The Developer is allowed to run `git commit` and `npm install` without prompting because those are core to the implementation loop. The DevOps agent, by contrast, must prompt on `docker build` and is denied `kubectl` entirely. The Developer has `temperature: 0.3` for creative variability; the DevOps agent has `temperature: 0.0` for determinism.

**Architect Agent**: The Architect has `bash: *: deny` with only `git *: allow` and `gh *: allow` — it does not need shell access because it plans and delegates rather than executes. The DevOps agent has the broadest bash surface of any leaf agent. The Architect has `task: allow` for delegation; the DevOps agent has `task: deny`.

**Spec Writer Agent**: The Spec Writer has `bash: *: deny` with only `gh *: allow` — it is purely analytical. The DevOps agent is the operational counterpart: it executes, deploys, and manages rather than analyzes and documents.

## Analysis

The DevOps agent design is shaped by a fundamental tension: it needs **more shell access than any other agent** (to run Docker, CI/CD tools, package managers, infrastructure CLI tools) while also being **the highest-risk agent** (a mistake in infrastructure can take down production). The design resolves this tension through three mechanisms:

**1. Hard denies on direct cloud access.** By denying `kubectl` and `aws`, the agent is forced to use CI/CD pipelines for all infrastructure changes. This creates an audit trail, enforces review gates (the pipeline requires approval steps), and prevents unreviewed production changes. The cost is reduced operational speed — a hotfix that needs a fast deployment must wait for the pipeline to run. This is an acceptable trade-off for a cooperative where multiple developers share infrastructure.

**2. Temperature 0.0 for deterministic operations.** Infrastructure changes must be repeatable. The same deploy command with the same inputs should always produce the same result. Temperature 0.0 eliminates variability in the agent's decision-making, making deployment logs predictable and debuggable. If a deployment fails, the replay will produce the same reasoning, which simplifies root cause analysis.

**3. Prompt-level safety rules for production gates.** The "NEVER deploy to production without Architect approval" rule is enforced purely by the system prompt, not by the permission model. This is a deliberate choice: the permission model cannot distinguish between a staging deployment and a production deployment (both run `kubectl` or `terraform apply`), so the safety rule must live in the prompt. The `kubectl: deny` rule is the structural backup — if the agent were to ignore the prompt and try to deploy to production directly, it would be blocked by the permission model anyway. The defense-in-depth approach (prompt + permissions) provides layered safety.

**4. `rs-dependency-checker` as a required pre-flight step.** Before any dependency update is applied, the agent must run the vulnerability scanner. This prevents the common failure mode where a dependency is updated to fix one issue but introduces a CVE in the process. The skill encapsulates external API calls to vulnerability databases and produces structured audit reports that can be reviewed before merge.

## Recommendations

1. **Implement `rs-dependency-checker` before the DevOps agent goes live.** The vulnerability scanning workflow is the DevOps agent's highest-frequency task. Without it, the agent cannot safely manage dependencies. The skill should support at minimum: pip (requirements.txt, pyproject.toml), npm (package-lock.json), and GitHub Actions (action version pinning).

2. **Add a `rollback` skill (`rs-rollback`)** that encapsulates the rollback workflow for common deployment patterns (Docker rollback to previous tag, Terraform state rollback, npm package version revert). This would make the "always have a rollback plan" rule mechanically enforceable rather than prompt-dependent.

3. **Monitor the `bash: ask` prompting frequency.** If the DevOps agent prompts the user too often (e.g., on every `ls` or `cat`), consider adding specific allow patterns for common read-only commands (`ls *`, `cat *`, `docker ps`, `docker images`). The goal is to prompt only for write or state-changing operations.

4. **Consider a `rs-health-check` skill** for post-deployment verification. The skill would define health check templates (HTTP endpoint checks, log pattern matching, metric threshold validation) that the agent runs after every deployment. This would standardize the verification step across all environments and projects.

5. **Evaluate whether `aws *: deny` should become `aws *: ask` for read-only commands.** Commands like `aws s3 ls`, `aws ec2 describe-instances`, and `aws cloudtrail lookup-events` are read-only and useful for diagnostics. A pattern like `"aws sts get-caller-identity": allow` could give the agent just enough AWS access for authentication verification without exposing write operations. However, this increases the attack surface — a future vulnerability in the agent prompt could trick the model into writing infrastructure state. The current hard deny is the safer default.
