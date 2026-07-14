---
title: "Keep a Changelog 2.0.0 — Specification"
status: draft
author: Khalid Zubair
date: 2026-06-14
tags:
  - changelog
  - documentation
  - versioning
  - standard
sources:
  - url: https://keepachangelog.com/en/2.0.0/
    title: "Keep a Changelog v2.0.0"
last_audit_date: 2026-06-14
---

# Keep a Changelog 2.0.0 — Specification

## What Is a Changelog

A changelog is a curated, chronologically ordered list of notable changes for each version of a project. It is distinct from a commit log: commits document incremental steps in source code evolution, whereas a changelog communicates noteworthy differences to end users in a digestible format.

## Why Keep One

A well-maintained changelog makes it easy for users and contributors to see the notable changes between each version. Without one, consumers of the software must dig through git logs, release notes scattered across platforms, or issue trackers to understand what changed.

## Guiding Principles

1. **Changelogs are for humans, not machines.** Entries should be written in plain language that a person can read and understand. Machine parsability is secondary — but a consistent structure makes it easy to parse anyway.
2. **Every version should have an entry.** No versions should be skipped and no releases should go undocumented.
3. **Group changes of the same type.** Changes of the same category (features, fixes, etc.) are listed under the same section heading within a version.
4. **Make versions and sections linkable.** Use Markdown reference-style links so readers can link directly to a specific version or section.
5. **List the latest version first.** Reverse chronological order ensures readers see the most recent release at the top.
6. **Show the release date of each version.** Every version heading includes the release date in ISO 8601 (`YYYY-MM-DD`) format.
7. **Note which versioning scheme you use.** State whether you follow Semantic Versioning or another scheme, so readers can interpret your version numbers.
8. **Write plainly.** Many readers are not native speakers, so favor clear, concise wording.

## File Format

The canonical file is named `CHANGELOG.md` and uses Markdown. Alternative names such as `HISTORY`, `NEWS`, or `RELEASES` exist, but `CHANGELOG.md` is recommended for consistent discoverability across projects.

## Versioning

The standard is compatible with [Semantic Versioning (SemVer)](https://semver.org/spec/v2.0.0.html) (MAJOR.MINOR.PATCH), and the preamble example uses it, but any consistent versioning scheme can be used — including [Calendar Versioning (CalVer)](https://calver.org/), a plain number, or a date. Note which scheme you use so readers can interpret your version numbers. Some projects release continuously and have no version numbers; a changelog still helps by keeping dated entries under `Unreleased`.

## The H1 Preamble

Every changelog should open with a `# Changelog` heading and a short, fixed preamble stating the conventions it follows. See [format.md](format.md#h1-preamble) for the exact template and format conventions.

## Breaking Changes

Mark breaking changes clearly with a `**Breaking:**` marker within the entry. Breaking changes usually go under `Changed` or `Removed`:

```markdown
- **Breaking:** parse() now returns a result object instead of raising.
```

Say what breaks — the word means little until readers know which interface you keep stable: a CLI, a library API, a network protocol, a file format, or a configuration schema. State which one your versioning scheme covers.

For minor breaking changes, a short upgrade note can sit in the entry itself. When the steps are substantial, link to a migration guide or release notes. Keep the `**Breaking:**` marker on the entry within its type section, rather than collecting breaks into a separate section, so anyone scanning `Changed` or `Removed` sees them in place.

## The Unreleased Section

Keep an `Unreleased` section at the top to collect upcoming changes. It shows readers what to expect, and at release time you move its contents into a new version heading. Starting on a project that has no changelog? Begin here, recording notable changes from now on. Reconstructing past releases from version history is also worthwhile.

## Changelogs vs Release Notes

A changelog is the complete, ongoing record: every notable change across every version, kept in one file in the repository. Release notes are an announcement for a single release: a curated selection of headline changes published when that version ships. The changelog is the source; release notes are drawn from it. See [best-practices.md](best-practices.md#changelog-vs-release-notes) for expanded guidance on workflow and automation.

## Curation Over Accumulation

A changelog records *notable* changes, which means some changes are not notable and do not belong in it. Deciding which is which takes judgment, and that judgment is human. See [best-practices.md](best-practices.md#curation-over-accumulation) for practical guidance on curating entries effectively.

## LLM and Agent Guidance

A language model can draft a changelog from a diff in seconds. **Machines can draft, but humans curate** — a model cannot decide what is notable for your readers. See [best-practices.md](best-practices.md#llm-and-agent-changelog-brief) for the drafting brief and practical guidance on LLM-assisted changelog workflows.

## Monorepos

How to handle a monorepo depends on whether it holds one product or many:

- **Unrelated projects** that share a repository each keep their own changelog.
- **A single product made of many parts** (e.g., a framework split into separate libraries) can keep a changelog per component, but should also keep one central changelog. Readers should not have to read a dozen component changelogs to understand what a release means. The per-component changelogs are the detailed record; the central one is the summary.

## Large Changelogs

A single file is usually fine. See [format.md](format.md#large-changelog-archiving) for archiving conventions when the file grows large.

## Date Format

All release dates use the ISO 8601 format: `YYYY-MM-DD`. See [format.md](format.md#yyyy-mm-dd-dating) for the exact heading format.
