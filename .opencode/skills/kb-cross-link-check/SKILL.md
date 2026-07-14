---
name: kb-cross-link-check
description: Validate cross-link paths and URLs in Knowledge Base frontmatter — path resolution on disk, URL reachability via webfetch, ADR relative path resolution
---

# kb-cross-link-check

## When to use me

Call this skill after a file is created or edited and you need to verify its cross-links resolve correctly. Use it as part of a review workflow after scaffolding, before merging, or when auditing existing documents. Do NOT use for files without YAML frontmatter.

---

## Before you start

Read the target section's `AGENTS.md` and `templates/AGENTS.md` to determine which cross-link fields are defined for that section. The authoritative field list comes from those files — this skill only defines how to resolve and validate them.

The section `AGENTS.md` files define WHAT cross-link fields exist. This skill defines HOW to check them.

## Check mechanics

### Path resolution

When a cross-link contains a relative filesystem path:

1. Strip trailing slashes from the path.
2. If the path ends with `.md`, check that exact file exists on disk relative to the repo root (or relative to the ADR folder for `replaces`/`replaced-by`).
3. If the path does not end with `.md`, it is a folder reference. Append `/overview.md` and check that file exists.
4. Report the resolved path in the error message so the caller knows exactly what was checked.

### URL verification

When a cross-link contains a URL:

1. Use `webfetch` to attempt to reach the URL. **Requires `webfetch` permission** — if your agent lacks this permission, skip URL reachability checks and report URLs as `status: "unverified"` rather than failing.
2. If the fetch returns a 2xx status code, the link is reachable — report OK.
3. If the fetch returns a 4xx or 5xx status code, fails, or times out, report the failure with the status code or error message.
4. Do NOT validate URL format alone — always verify reachability when possible.

### ADR relative path resolution

`replaces` and `replaced-by` paths are relative to the ADR's **own folder**, not the repo root:

1. Given an ADR at `adr/0015-foo/overview.md` with `replaces: "../0002-bar/"`:
   - Resolve against `adr/0015-foo/` → `adr/0002-bar/`
   - Check `adr/0002-bar/` exists as a directory
   - Check it contains `.md` files (at minimum an `overview.md`)
2. If the resolved path points to a valid ADR folder, report OK.
3. If not, report the resolved path and what was expected.

### Knowledge key resolution (research sources)

Research `sources` use the `knowledge:` key format:

```
sources:
  - knowledge: "knowledge/technology/databases/postgresql/"
```

1. Extract the value after `knowledge:`.
2. Resolve as a relative path from the repo root.
3. If it points to a folder, append `/overview.md` and check existence.
4. If it points to an `.md` file directly, check that file exists.
5. Report which file was checked.

## Validation procedure

For each check, read the file's YAML frontmatter, extract the cross-link field, resolve every entry in it, and report results.

### 1. Parse frontmatter

Read the file and extract its YAML frontmatter. If no frontmatter is present, report that and stop.

### 2. Extract cross-link fields

Based on the section (provided by the caller), determine which fields to check. Reference the section's `AGENTS.md` and `templates/AGENTS.md` for the authoritative field list.

### 3. Resolve and verify each entry

For each entry in each cross-link field:

- **Filesystem path**: Resolve following the Path Resolution mechanics above. Verify the resolved path exists on disk.
- **URL**: Verify reachability following the URL Verification mechanics above.
- **ADR relative path**: Resolve following the ADR Relative Path Resolution mechanics above.

### 4. Collect and report

Collect all broken links. If none are broken, report success. If any are broken, report them following the Error Handling section below.

## Error handling

Follow the fail-and-explain pattern. Report each broken link with the field name and the broken path. Do not silently skip or auto-fix.

### Example messages

- "`ideas/foo/` in `related_ideas` — folder exists but no `overview.md` found"
- "`knowledge/missing-topic/` in `sources` does not exist on disk"
- "URL `https://example.com/broken` in `references` returned status code 404"
- "`replaces` path `../0002-bar/` resolves to `adr/0002-bar/` which does not exist"
- "`knowledge: "knowledge/foo/bar"` in `sources` — resolved to `knowledge/foo/bar/overview.md` which does not exist"

## Response contract

Return results as JSON:

```json
{
  "valid": true,
  "file": "proposals/my-proposal/overview.md",
  "section": "proposals",
  "links": [
    {"field": "related_research", "path": "research/foo/overview.md", "status": "ok", "message": null}
  ]
}
```

On failure:
```json
{
  "valid": false,
  "file": "proposals/my-proposal/overview.md",
  "section": "proposals",
  "links": [
    {"field": "related_research", "path": "research/foo/overview.md", "status": "ok", "message": null},
    {"field": "related_adrs", "path": "adr/0002-bar/overview.md", "status": "broken", "message": "Path `adr/0002-bar/overview.md` does not exist on disk"},
    {"field": "references", "path": "https://example.com/broken", "status": "broken", "message": "URL returned status code 404"}
  ]
}
```

On partial check (webfetch unavailable — URLs skipped):
```json
{
  "valid": false,
  "file": "proposals/my-proposal/overview.md",
  "section": "proposals",
  "links": [
    {"field": "related_research", "path": "research/foo/overview.md", "status": "ok", "message": null},
    {"field": "references", "path": "https://example.com/docs", "status": "unverified", "message": "webfetch permission not available — URL reachability not verified"}
  ]
}
```

