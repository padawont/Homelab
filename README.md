# Homelab PKM

Personal Knowledge Management system for my homelab infrastructure.

```
Idea → Knowledge → Research → ADR → Implementation
                                    └──► Archive
```

## Repository Structure

| Folder | Purpose |
|---|---|
| `01_Ideas/` | Raw concepts, wishlist items, new tech spottings |
| `02_Knowledge/` | General tech concepts, syntax guides, theory |
| `03_Research/` | Deep dives combining ideas + knowledge into an ADR plan |
| `04_ADRs/` | Architectural Decision Records with mermaid diagrams |
| `05_Implementations/` | Live running setups — configs and overview |
| `06_Archive/` | Failed experiments, rejected proposals, retired services |
| `Templates/` | Reusable document templates |

## Pipeline

| Step | Input | Output |
|---|---|---|
| Idea → Knowledge | Raw concept | Structured reference note |
| Knowledge → Research | Knowledge + Ideas + online docs | Plan for ADR, with alternatives |
| Research → ADR | Research doc | Decision record with mermaid diagrams |
| ADR → Implementation | ADR | Live service (overview + configs) |
| Any → Archive | Archived content | Moved, purged after 31 days |

### Dependency Rules

- **Ideas**: stand alone
- **Knowledge**: stand alone
- **Research**: requires at least one Knowledge note or online documentation
- **ADR**: requires a Research doc
- **Implementation**: requires an ADR + Knowledge note(s)
