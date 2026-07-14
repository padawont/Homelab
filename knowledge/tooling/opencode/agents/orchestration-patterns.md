---
title: "Orchestration Patterns for Multi-Agent Systems"
status: draft
author: "refactorartist (Khalid Zubair)"
date: 2026-06-07
tags:
  - opencode
  - agents
  - orchestration
  - patterns
sources:
  - url: "https://opencode.ai/docs/agents"
    title: "OpenCode Agents Documentation"
  - url: "https://opencode.ai/docs/tools"
    title: "OpenCode Tools Documentation"
last_audit_date: 2026-06-07
---

# Orchestration Patterns for Multi-Agent Systems

When a single agent isn't enough, you need to coordinate multiple agents working together toward a shared goal. This note documents the four primary orchestration patterns used in OpenCode multi-agent systems, with particular attention to their implementation in the `@runicengines/opencode-runesmith` plugin for the RunicEngines cooperative.

Understanding these patterns is essential for Python developers building complex agent workflows. Each pattern maps to familiar programming concepts — a Django developer will recognize hub-and-spoke as a view that calls multiple service functions, and a Flask developer will see chain-of-responsibility in the WSGI middleware stack.

---

## Hub-and-Spoke Pattern

The hub-and-spoke pattern uses a single orchestrator agent — the hub — that delegates work to specialist subagents — the spokes. The hub plans the work, dispatches tasks via `task()`, collects results, and synthesizes the final output. Spokes never delegate further; they receive a prompt, execute, and return.

```
                        ┌──────────────┐
                        │  Architect   │
                        │   (Hub)      │
                        └──────┬───────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
       ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
       │  Spec-      │ │  Developer  │ │  Reviewer   │
       │  Writer     │ │             │ │             │
       └─────────────┘ └─────────────┘ └─────────────┘
              │                          │
       ┌──────▼──────┐           ┌──────▼──────┐
       │  Tester     │           │  Security   │
       │             │           │  Auditor    │
       └─────────────┘           └─────────────┘
```

### How It Works

The hub agent receives a high-level goal (e.g., "Build JWT auth for the API gateway"). It decomposes this into stages and delegates each stage to a specialist:

1. Hub invokes **spec-writer** to produce a design document.
2. Hub reads the spec, then invokes **developer** to implement.
3. Hub invokes **reviewer** to inspect the diff.
4. Hub invokes **tester** to generate test coverage.
5. Hub aggregates all outputs into a final report.

### Code Example

```typescript
// Inside the Architect agent's context — invoked automatically by the model
// when it decides to delegate a task:

const spec = await task({
  name: "spec-writer",
  prompt: `Design a JWT authentication system for the API gateway.
Consider: token expiry, refresh flow, blacklisting, and key rotation.
Output a markdown design document.`
});

// Architect reviews spec, then delegates implementation:
const implementation = await task({
  name: "developer",
  prompt: `Implement the JWT auth design below.
Use PyJWT and FastAPI. Include middleware hooks.
\n\n${spec}`
});

// Architect delegates review:
const review = await task({
  name: "reviewer",
  prompt: `Review this PR for security issues, code style, and correctness.
${implementation}`
});
```

### Pros

- **Clear control flow** — One agent owns the full context; easy to reason about.
- **Specialist isolation** — Each spoke focuses on one domain; prompts stay narrow and deterministic.
- **Auditable** — The hub's message log contains the complete chain of delegation and results.

### Cons

- **Architect bottleneck** — The hub must process every input and output; it becomes the serialization point.
- **Context window pressure** — The hub accumulates results from all spokes, consuming tokens rapidly.
- **Single point of failure** — If the hub drifts or hallucinates, the entire chain is corrupted.

### Python Developer Analogy

Hub-and-spoke is like a Django class-based view that calls multiple service-layer functions:

```python
class JWTAuthView(APIView):
    def post(self, request):
        spec = SpecService.design_auth_system(request.data)
        implementation = DevService.implement(spec)
        review = ReviewService.check(implementation)
        tests = TestService.write(implementation)
        return Response(self._synthesize(spec, implementation, review, tests))
```

---

## Gated Pipeline Pattern

The gated pipeline runs work through sequential stages where each stage has a gate that must pass before the next stage begins. If a gate fails, the task falls back to the previous stage for remediation.

```
  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  Plan    │ ──► │  Code    │ ──► │  Test    │ ──► │  Review  │
  │  Gate    │     │  Gate    │     │  Gate    │     │  Gate    │
  └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
       │                 │                │                │
       ▼                 ▼                ▼                ▼
   ┌────────┐      ┌────────┐       ┌────────┐       ┌────────┐
   │ Critic │      │  Dev   │       │  Tester│       │Reviewer│
   │approves│      │implements      │runs &  │       │approves│
   │ plan   │      │        │       │passes  │       │        │
   └────────┘      └────────┘       └────────┘       └────────┘
                          ▲                ▲               ▲
                          │                │               │
                          └── fail-back ───┴── fail-back ──┘
```

### Gate Types

| Gate | Critic Agent | Pass Condition | Fail-Back To |
|---|---|---|---|
| Plan gate | Architect / Tech-Lead | Plan is feasible, scoped, and consistent | — (start) |
| Code gate | Developer | Implementation compiles and follows spec | Plan stage |
| Test gate | Test-Specialist | All tests pass, coverage ≥ threshold | Code stage |
| Review gate | Reviewer / Security-Auditor | No critical issues, style compliant | Code stage |

### Circuit Breaker

Each gate has a maximum retry count. Once exceeded, the pipeline halts and escalates to a human:

```typescript
const MAX_RETRIES = 3;
let retries = 0;

while (retries < MAX_RETRIES) {
  const testResult = await task({
    name: "test-specialist",
    prompt: `Run tests for the following implementation:\n${code}`
  });

  if (testResult.passed) break;

  retries++;
  code = await task({
    name: "developer",
    prompt: `Fix the failing tests. Previous attempt (${retries}/${MAX_RETRIES}):\n${testResult.errors}`
  });
}

if (retries === MAX_RETRIES) {
  await task({
    name: "escalation",
    prompt: `Pipeline blocked: tests failed after ${MAX_RETRIES} attempts.`
  });
}
```

### Pros

- **Quality enforcement** — Every gate enforces a hard contract before proceeding.
- **Self-correcting** — Fail-back routing lets the pipeline remediate without human intervention.
- **Deterministic progression** — The sequence is fixed and predictable.

### Cons

- **Serial bottleneck** — Each stage blocks until the previous gate passes. Slow stages (e.g., full test suites) delay everything.
- **Retry explosion** — Without a circuit breaker, a flaky gate loops forever consuming tokens.
- **Rigid** — Adding or removing gates requires restructuring the pipeline.

### Python Developer Analogy

Gated pipeline maps directly to CI/CD stages in GitHub Actions or GitLab CI:

```yaml
# .github/workflows/quality-gates.yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [run: flake8 .]
  test:
    needs: [lint]
    runs-on: ubuntu-latest
    steps: [run: pytest --cov=80]
  security:
    needs: [test]
    runs-on: ubuntu-latest
    steps: [run: bandit -r .]
```

The `needs` keyword is the gate. If `lint` fails, `test` never runs.

---

## Chain-of-Responsibility Pattern

A request passes through a chain of handlers. Each handler decides whether to process the request or pass it to the next link in the chain. Unlike hub-and-spoke, there is no central dispatcher — each node makes an independent decision.

```
  ┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
  │   Issue    │ ──► │   Spec-    │ ──► │  Architect │ ──► │  Developer │
  │  Creator   │     │   Writer   │     │            │     │            │
  └────────────┘     └────────────┘     └────────────┘     └────────────┘
                                                                    │
                                                                    ▼
                                                             ┌────────────┐
                                                             │  Reviewer  │
                                                             │            │
                                                             └────────────┘
```

### How It Works

Each agent in the chain examines the incoming prompt and decides:

- **Process** — Do the work and pass the result downstream.
- **Delegate** — Forward to a more appropriate handler without processing.
- **Terminate** — Return the final result; no further handlers needed.

### Example: Issue-to-PR Pipeline

```typescript
// Spec-Writer receives a raw issue:
const issue = "Add rate limiting to the API gateway";

// Spec-Writer processes it and passes structured requirements downstream:
const spec = await task({
  name: "spec-writer",
  prompt: `Extract requirements from this issue: ${issue}`
});

// Architect receives the spec, assigns scope, passes to Developer:
const design = await task({
  name: "architect",
  prompt: `Scope the implementation for:\n${spec}`
});

// Developer receives the scoped design, implements, passes to Reviewer:
const code = await task({
  name: "developer",
  prompt: `Implement:\n${design}`
});

// Reviewer validates and returns the final result:
const review = await task({
  name: "reviewer",
  prompt: `Review:\n${code}`
});
```

Each agent only knows about the next link in the chain. No single agent holds the full picture.

### Pros

- **Decoupled** — Handlers can be added, removed, or reordered without affecting the rest of the chain.
- **Flexible processing** — Each node applies its own judgment; the chain adapts dynamically.
- **Natural fit for pipelines** — Maps well to document processing, code review flows, and data enrichment.

### Cons

- **Hard to trace** — No central log of the full flow. Debugging requires instrumenting every node.
- **No global context** — Each handler receives only the immediate input. Cross-cutting concerns (e.g., security invariants) are difficult to enforce.
- **Orphan risk** — A handler that crashes or produces no output breaks the chain silently.

### Python Developer Analogy

Chain-of-responsibility is the WSGI / ASGI middleware stack:

```python
class MiddlewareChain:
    def __init__(self):
        self.handlers = [
            SecurityMiddleware(),
            AuthMiddleware(),
            RateLimitMiddleware(),
            Router(),
        ]

    def handle(self, request):
        for handler in self.handlers:
            response = handler.process(request)
            if response is not None:
                return response
        raise ValueError("No handler processed the request")
```

Each middleware either returns a response (terminates the chain) or passes the request to the next middleware.

---

## Skill-Routing Pattern

The skill-routing pattern uses a YAML configuration file to dynamically inject skills into an agent's context based on keyword matching. When an agent is invoked with a prompt containing certain keywords, the router attaches the corresponding skill instructions.

```
  ┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
  │   Incoming   │ ──► │  Skill Router    │ ──► │   Injected   │
  │   Prompt     │     │  (YAML config)   │     │   Agent      │
  └──────────────┘     └──────────────────┘     └──────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │ skill-routing.yaml │
                        │                   │
                        │ developer:        │
                        │   - test-skills   │
                        │ reviewer:         │
                        │   - code-review   │
                        │   - security-scan │
                        └──────────────────┘
```

### Configuration Format

```yaml
# .opencode/skills/skill-routing.yaml
version: 1
routing:
  developer:
    - path: .opencode/skills/writing-tests/SKILL.md
      keywords: ["test", "testing", "unit", "coverage"]
    - path: .opencode/skills/git-workflow/SKILL.md
      keywords: ["commit", "branch", "pr", "merge"]
  reviewer:
    - path: .opencode/skills/code-review/SKILL.md
      keywords: ["review", "audit", "inspect", "security"]
    - path: .opencode/skills/linting/SKILL.md
      keywords: ["style", "lint", "format"]
  architect:
    - path: .opencode/skills/design-review/SKILL.md
      keywords: ["architecture", "design", "modularity"]
```

### How It Works

1. A prompt arrives for an agent role (e.g., `developer`).
2. The router scans the prompt for keywords listed under that role.
3. For each matched keyword group, the corresponding skill file is loaded via `skill()`.
4. The skill instructions are injected into the agent's system prompt before processing.

### Advanced: opencode-swarm Integration

> **Note:** `opencode-swarm` is an experimental/forward-looking concept. It is not a published plugin on npm or in the OpenCode ecosystem as of this writing. The `version: 2` routing format shown below is conceptual and may change or never ship. This section describes a potential direction for future OpenCode development.

The `opencode-swarm` plugin extends skill-routing with agent-to-agent negotiation. When an agent receives a prompt it cannot fully handle, it uses the routing table to discover and delegate to a more appropriate agent, loading the relevant skills as part of the handoff.

```yaml
# opencode-swarm routing table (conceptual)
version: 2
routing:
  triage:
    - target: developer
      match: ["implement", "code", "fix", "feature"]
    - target: reviewer
      match: ["review", "approve", "validate"]
negotiation:
  timeout_seconds: 30
  fallback_strategy: "round_robin"
```

### Pros

- **Configurable without code changes** — Add new skills or reroute agents by editing YAML.
- **Context efficiency** — Skills are loaded on demand; agents only carry relevant instructions.
- **Discoverable** — The routing table serves as a registry of available agent capabilities.

### Cons

- **YAML drift** — The routing table can fall out of sync with on-disk skill files. No automatic validation.
- **Keyword brittleness** — A prompt that uses synonyms (e.g., "examine" instead of "review") may miss the route.
- **Over-injection** — Broad keyword matches can load too many skills, bloating the agent context.

### Python Developer Analogy

Skill-routing is like a URL router mapping endpoints to view handlers:

```python
# urls.py — the routing table
from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
]
```

Just as a URL router matches a request path to a view function, the skill router matches prompt keywords to skill files. Django's URL resolver even supports `include()` for sub-routing — analogous to nested routing tables in opencode-swarm.

---

## Comparison Table

| Pattern | Central Control | Best For | Primary Risk | Python Analogy |
|---|---|---|---|---|
| Hub-and-Spoke | Yes (architect) | Complex multi-step workflows | Architect bottleneck / context pressure | Django view calling service layer |
| Gated Pipeline | Yes (gates) | Quality-critical workflows | Serial slowdown / retry explosion | CI/CD stage graph (GitHub Actions `needs`) |
| Chain-of-Responsibility | No | Flexible processing pipelines | Hard to trace / orphan requests | WSGI middleware stack |
| Skill-Routing | Config-driven | Dynamic agent-skill mapping | YAML drift / keyword brittleness | Django URL router → view mapping |

---

## Which Pattern to Use

```
Is the workflow quality-critical (security audit, production deploy)?
│
├── Yes → Is the sequence fixed and known in advance?
│   │
│   ├── Yes ───────── Gated Pipeline
│   │
│   └── No ────────── Hub-and-Spoke (architect decides order dynamically)
│
└── No → Does each stage need independent judgment?
    │
    ├── Yes ───────── Chain-of-Responsibility
    │
    └── No → Are skills the main variable (different skills for different tasks)?
        │
        ├── Yes ───── Skill-Routing
        │
        └── No ────── A single agent is probably sufficient
```

### Hybrid Approaches

The patterns are not mutually exclusive. Common hybrid designs include:

- **Gated Pipeline with Hub-and-Spoke inside each gate** — e.g., the "test gate" spawns a mini hub that coordinates unit tests, integration tests, and security scans in parallel before reporting pass/fail.
- **Chain-of-Responsibility with Skill-Routing at each node** — each handler in the chain uses a routing table to load the appropriate skills before processing its input.
- **Hub-and-Spoke with a Gated Pipeline as the delegate** — the architect delegates to a "quality pipeline" subagent that runs a gated sub-workflow and returns a summary.

---

## Anti-Patterns

### 1. Deep Nesting of Hubs

A hub that delegates to a spoke that itself acts as a hub for other spokes creates deep nesting. This obscures the control flow and multiplies context consumption.

```
❌ Bad:  Hub A → Hub B → Spoke C → Spoke D
✅ Good: Hub A → Spoke C, Hub A → Spoke D  (flat delegation)
```

**Rule**: If a spoke needs to delegate further, promote that spoke to a hub at the same level, or flatten the workflow.

### 2. Missing Circuit Breakers in a Gated Pipeline

A gated pipeline without retry limits can loop forever on a flaky gate, burning through API tokens and budget.

**Rule**: Every gate must define `max_retries` and an escalation path (human alert, skip, or degrade).

### 3. Chain-of-Responsibility Without Timeouts

In a chain where each handler makes an independent decision, a slow or hung handler blocks every downstream node. Without timeouts, the chain stalls indefinitely.

**Rule**: Each handler in the chain should have a `timeout_seconds` and a fallback action (skip, default response, escalate).

### 4. YAML as a Single Source of Truth for Skill-Routing

Treating `skill-routing.yaml` as the authoritative list of agent capabilities leads to drift when skills are added or removed on disk but the routing table is not updated.

**Rule**: Run a validation step — either a CI check or a startup hook — that compares the routing table entries against actual skill file paths on disk.

### 5. Mixing Patterns Without Documentation

Combining hub-and-spoke with chain-of-responsibility or gated pipelines without documenting the flow produces a system that only the original author can debug.

**Rule**: Every multi-agent workflow must include a flow diagram (ASCII or Mermaid) and an explanation of which pattern each segment follows.

---

## See Also

- [composition-patterns](composition-patterns.md) — Primary + specialist subagent workflows, review pipelines, and best practices for pairing agents.
- [interactions](interactions.md) — How the `skill` tool and `task` tool work at the API level.
- [roles](roles.md) — Pre-assembled subagent role profiles for architect, developer, reviewer, test-specialist, and security-auditor.
- [concepts](concepts.md) — What agents are, the primary vs subagent distinction, and the built-in agent roster.
