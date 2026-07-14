# Research Section

Research is the information gained using an idea as context and bounded by relevant knowledge. It is the final analysis of ideas + knowledge, and forms the basis for Proposals and/or ADRs.

## Topic Folders

Each research topic is a kebab-case folder containing:

| File | Required | Purpose |
|---|---|---|
| `README.md` | Yes | Basic description and index |
| Atomic `.md` files | Yes (2+) | Multiple focused notes, each covering one finding or recommendation |
| `overview.md` | No | Optional summary — only if a single overview is explicitly requested |

**Atomic notes rule:** Break analysis into focused files rather than one comprehensive `overview.md`. Each atomic note covers one finding, recommendation, or component design. Use the README.md as an index linking to all notes in the folder.

### Example

```
research/opencode-runesmith/skills/utilities/
+-- README.md              # Index linking to each atomic note
+-- rs-discover.md         # Discover skill design (one file per skill)
+-- rs-consult.md          # Consult skill design
```

## Sources vs References

- **Sources** (`sources` in frontmatter): Links to Knowledge notes using the `knowledge:` key format (e.g., `- knowledge: "knowledge/technology/databases/postgresql/"`). Paths are relative to the repository root and may target either topic folders or individual `.md` files.
- **References** (`references` in frontmatter): External URLs (blog posts, documentation, papers)

Both must be populated.

## Frontmatter Requirements

All atomic `.md` files (including `overview.md` if present) must include in frontmatter:
- `sources` — links to Knowledge notes that informed this research
- `references` — external URLs used as references
- `last_audit_date` — date of the last accuracy review

`README.md` does not require frontmatter. Other supporting `.md` files may include frontmatter as appropriate.

## Status Lifecycle

`draft` → `exploring` → `proposed` → `accepted` → `completed` / `superseded`
