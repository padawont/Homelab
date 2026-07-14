# ADR Root AGENTS

# Architecture Decision Records (ADRs)

ADRs are the technical decisions on how to solve problems. They follow the MADR (Markdown Any Decision Records) format with PEP-style metadata headers.

ADRs can be based on Proposals or emerge independently from actual development workflows.

## Topic Folders

Each ADR is a folder named `<NNNN>-<kebab-case-title>` containing:

| File | Required | Purpose |
|---|---|---|
| `README.md` | Yes | Basic description |
| `overview.md` | Yes | Full ADR content in MADR format |

## Frontmatter Fields

| Field | Required | Description |
|---|---|---|
| `adr` | yes | Sequential number (e.g., 0001) |
| `title` | yes | Short descriptive title |
| `author` | yes | Name or GitHub handle |
| `status` | yes | `draft` → `final`, `cancelled`, or `superseded` |
| `topic` | yes | The subject area of this decision |
| `technology` | no | Constraint format: `PHP[=7]`, `Python[>3.13]` |
| `date` | final status | Final decision date (YYYY-MM-DD) |
| `date-proposed` | yes | Date first proposed (YYYY-MM-DD) |
| `replaces` | no | Relative path to the ADR folder this one replaces |
| `replaced-by` | no | Relative path to the ADR folder that replaces this one |
| `history` | yes | PR link capturing the conversation and final status |
| `context` | yes | Executive summary of the issue motivating this decision (see body for full detail) |
| `decision` | yes | Executive summary of the change being proposed (see body for full detail, including justification) |
| `consequences` | yes | Executive summary of what becomes easier or harder (see body for full detail) |
| `sources` | no | Reference URLs |
| `references` | no | Additional URLs |

## Status Lifecycle

`draft` → `final` or `cancelled` or `superseded`

## MADR Content Structure

The body of `overview.md` should follow:

1. **Title** — ADR {NNNN}: {Title}
2. **Status** — Current status
3. **Context and Problem Statement** — The issue motivating the decision, framed as a problem
4. **Decision** — The change being proposed or made (include justification)
5. **Consequences** — What becomes easier or harder
6. **Considered Options** — Alternatives considered and why they were rejected (optional)
7. **Compliance** — How compliance will be enforced (optional)
