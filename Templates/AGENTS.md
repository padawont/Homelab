# AGENTS.md — Templates

Reusable document templates for all sections. Copy, don't edit.

## Template inventory

| Template | Path | For section |
|---|---|---|---|
| Idea | `./Templates/ideas/idea.md` | `./01_Ideas/` |
| Knowledge note | `./Templates/knowledge/note.md` | `./02_Knowledge/` |
| Research overview | `./Templates/research/overview.md` | `./03_Research/` |
| Research alternatives index | `./Templates/research/alternatives.md` | `./03_Research/` |
| Research alternative | `./Templates/research/alternative.md` | `./03_Research/` |
| ADR | `./Templates/adr/adr.md` | `./04_ADRs/` |
| Implementation | `./Templates/implementations/service.md` | `./05_Implementations/` |
| GitHub Issue | `./Templates/tasks/issue.md` | For creating new GitHub issues |

## Conventions

- Templates use YAML frontmatter with placeholder values (`""`, `[]`, `YYYY-MM-DD`, `0`)
- Use `<!-- comment -->` blocks as instructions — strip these when copying
- Never edit a template in place; always copy first
- Keep templates in sync with AGENTS.md conventions
- Archive does not need a template — archived files are copies of originals with added frontmatter
