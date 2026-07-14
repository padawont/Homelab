---
title: "Keep a Changelog 2.0.0 — File Format Conventions"
status: draft
author: Khalid Zubair
date: 2026-06-14
tags:
  - changelog
  - documentation
  - markdown
  - formatting
sources:
  - url: https://keepachangelog.com/en/2.0.0/
    title: "Keep a Changelog v2.0.0"
last_audit_date: 2026-06-14
---

# Keep a Changelog 2.0.0 — File Format Conventions

## H1 Preamble

Open the file with a `# Changelog` heading followed by a short, fixed preamble that states which conventions the project follows:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
```

Pin the Keep a Changelog link to the version you follow (e.g., `en/2.0.0/`), so it stays accurate as the convention evolves. Replace the Semantic Versioning reference with whichever versioning scheme your project uses.

## Reverse Chronological Order

Versions are listed newest first, oldest last. This ensures that the most recent release — the one readers care about most — appears at the top of the file.

```markdown
## [2.0.0] - 2026-06-07
## [1.1.0] - 2019-02-15
## [1.0.0] - 2017-06-20
```

## Markdown Heading Structure

- **H1 (`#`):** Used for the document title. The convention uses a single `# Changelog` as the file-level heading.
- **H2 (`##`):** Used for each version heading, including `[Unreleased]`. Format: `## [<version>] - <YYYY-MM-DD>`.
- **H3 (`###`):** Used for change type sections within a version (Added, Changed, etc.).

```markdown
# Changelog

## [Unreleased]

### Added
### Fixed

## [1.1.0] - 2019-02-15

### Added
### Fixed
```

## Per-Release Summaries

A version may optionally open with a short summary before the typed sections — a sentence or two on the theme of the release or a notable change. Use this when a release is worth introducing, and skip it otherwise.

```markdown
## [2.0.0] - 2026-06-07

This major release adds LLM guidance, breaking-change markers, and a redesigned website.

### Added
- New guidance on breaking changes, monorepos, and LLM-generated changelogs.
```

## Version Identifiers

Version identifiers are wrapped in square brackets (`[1.0.0]`). This makes them visually distinct and easier to parse. The version identifier matches the project's versioning scheme (typically SemVer like `1.0.0` without the `v` prefix in the heading, though some projects prefix with `v`).

## YYYY-MM-DD Dating

Every version heading (except `[Unreleased]`) includes a date in ISO 8601 format separated by a hyphen-space:

```markdown
## [1.1.0] - 2019-02-15
```

The `[Unreleased]` heading does not include a date.

## Reference Link Format

At the bottom of the file, reference-style links map each version identifier to a diff URL. This keeps the version headings clean and provides a way to jump to the comparison view.

```markdown
[Unreleased]: https://github.com/your/project/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/your/project/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/your/project/releases/tag/v1.0.0
```

Key conventions:
- **`[Unreleased]`** compares the latest tag to `HEAD` (the current development state).
- **Each released version** compares with its predecessor: `compare/v1.0.0...v1.1.0`.
- **The first release** links directly to its tag (no predecessor to compare with).
- When you cut a release, rename `Unreleased` to the new version in both the heading and its link, then add a fresh, empty `Unreleased` section pointing at `HEAD`.

This pattern ties every version to its tag and links to the exact diff of what changed — the same association a hosted release page makes for you, kept in a file you own instead of a host's database. The link stays out of the heading so the changelog reads cleanly.

## Yanked Releases

Versions that have been retracted due to serious bugs or security issues are marked with `[YANKED]` in the version heading:

```markdown
## [0.0.5] - 2014-12-13 [YANKED]
```

The `[YANKED]` tag is uppercase and bracketed to make it highly visible and programmatically parsable.

## Large Changelog Archiving

A single file is usually fine. If the file becomes hard to navigate, you can move old history into separate archive files. Follow these conventions:

- Link the main file and archive files both ways so readers can find older entries.
- Archive only versions old enough that they will not need editing.
- Do not delete old entries — someone may still upgrade from an old version.

```markdown
<!-- In CHANGELOG.md -->
For older versions, see [CHANGELOG.archive.md](CHANGELOG.archive.md).

<!-- In CHANGELOG.archive.md -->
This file contains archived changelog entries.
For current releases, see [CHANGELOG.md](../CHANGELOG.md).
```
