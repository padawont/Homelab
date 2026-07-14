---
title: "Keep a Changelog 2.0.0 — Change Types and Sections"
status: draft
author: Khalid Zubair
date: 2026-06-14
tags:
  - changelog
  - documentation
  - change-types
sources:
  - url: https://keepachangelog.com/en/2.0.0/
    title: "Keep a Changelog v2.0.0"
last_audit_date: 2026-06-14
---

# Keep a Changelog 2.0.0 — Change Types and Sections

## Defined Change Types

Keep a Changelog defines six standard change types, each representing a category of notable change. Each type is rendered as a third-level Markdown heading (`###`) under a version heading.

There are only six types on purpose. What kind of change it is goes in the type; why it matters goes in the wording of the entry, not in a new type. Keeping to the six leaves every changelog readable the same way, and parseable by the same tools.

### Added

For new features introduced in a version. This includes new functionality, new modules, new APIs, new configuration options, or any capability that did not previously exist.

Examples: new CLI commands, new public methods, new environment variables.

### Changed

For changes to existing functionality that worked as intended. The behavior was correct; now it works differently.

This covers modifications that alter the behavior, interface, or output of existing features without (necessarily) breaking backward compatibility. If the old behavior was a bug, use `Fixed` instead.

Examples: performance improvements, UI redesigns, updated dependencies, altered API responses.

### Deprecated

For features that are soon-to-be removed. Deprecation entries serve as an early warning to users. Features listed here will be removed in a future release, giving consumers time to migrate.

Examples: marking a legacy API as deprecated, retiring an old configuration key.

### Removed

For features that have been removed in this version. Previously deprecated features are typically removed here. Breaking changes that are not preceded by a deprecation warning should be clearly flagged (see [Breaking Changes in spec.md](spec.md#breaking-changes)).

Examples: deleting a deprecated API endpoint, dropping support for an old format.

### Fixed

For bug fixes. The behavior was wrong, and is now correct. If the change addresses an exploitable vulnerability, consider using `Security` instead.

Examples: resolving a crash, fixing incorrect output, patching a race condition.

### Security

For vulnerabilities and security-related fixes. The change addresses a vulnerability. It could fit under `Fixed` or `Changed`, but its urgency and audience are different — security fixes should be immediately visible.

When a `Security` entry has a CVE identifier, lead with it so readers and security tools can match the entry to the advisory:

```markdown
- CVE-2024-12345: out-of-bounds read when parsing malformed input.
```

## Choosing Between Changed, Fixed, and Security

These three types cause the most questions. The 2.0.0 guidance clarifies the distinction:

| Type | Use When |
|---|---|
| **Fixed** | The behavior was wrong, and is now correct. |
| **Changed** | The behavior worked as intended, and now works differently. |
| **Security** | The change addresses a vulnerability. Urgency and audience differ from a routine fix. |

When unsure, ask whether the old behavior was a bug. If it was, use `Fixed`. If it was intentional and you are changing it, use `Changed`.

## What the Six Types Deliberately Exclude

Two common requests are intentionally not added as change types:

- **Dependencies are not a type of change.** A dependency update can be harmless, a fix, or breaking. If it matters to your users, describe its effect under the right type (`Changed`, `Fixed`, or `Security`). If it does not, leave it out.
- **Known issues are not a type.** Known issues are discovered, not changed. Note them on the affected version or in your issue tracker. When one is fixed, it goes under `Fixed`.

Other would-be categories (like `Improved`, `Performance`, `Internal`, or `Housekeeping`) are nearly always better expressed through the existing six. For example, "Rewrote JSON parser; 3x faster on large files" fits under `Changed` rather than requiring a `Performance` type. You can add a category if you genuinely need one, but you rarely will.

## The Unreleased Section

A keep-a-changelog document should include an `Unreleased` section at the top. This section collects changes that have been committed to the development branch but have not yet been included in a numbered release.

**Purpose:**

- Lets consumers see what changes they can expect in upcoming releases.
- At release time, the entire `Unreleased` section is moved into a new version heading. This eliminates the need to write entries retroactively.

The heading format is:

```markdown
## [Unreleased]
```

## Section Ordering Within a Version

When multiple change types are present in a single version, they should follow a consistent ordering. The convention does not mandate a specific order, but the most commonly observed sequence is: Added, Changed, Deprecated, Removed, Fixed, Security.

## Yanked Releases

Versions that have been retracted due to serious bugs or security issues are marked with `[YANKED]` in the version heading. See [format.md](format.md#yanked-releases) for the exact format and conventions.
