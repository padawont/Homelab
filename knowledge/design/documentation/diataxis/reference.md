---
title: "Reference — Information-Oriented Documentation"
status: draft
tags: [diataxis, reference, information, technical-description]
author: "RunicEngines Knowledge Base"
date: 2026-06-14
sources:
  - url: https://diataxis.fr/reference/
    title: "Diátaxis — Reference"
  - url: https://diataxis.fr/
    title: "Diátaxis — Home"
last_audit_date: 2026-06-14
---

# Reference — Information-Oriented Documentation

Reference guides are **technical descriptions** of the machinery and how to operate it. They are always **information-oriented** — containing propositional or theoretical knowledge that a user looks to in their *work*.

## Core Identity

Reference material describes the machinery. It should be **austere** and **wholly authoritative**. One hardly *reads* reference material; one *consults* it.

Reference is like a **map**: it tells you what you need to know about the territory without having to go out and check it yourself. The only purpose of a reference guide is to describe, as succinctly as possible, and in an orderly way.

Whereas tutorials and how-to guides are led by user needs, reference material is led by the **product it describes**.

## Key Principles

### Describe and Only Describe

Neutral description is the key imperative. Style and form must be:

- Austere and uncompromising
- Neutral, objective, factual
- Structured according to the structure of the machinery itself

Resist the temptation to introduce instruction and explanation. Instead, link to how-to guides and explanation where needed.

### Adopt Standard Patterns

Reference material is useful when it is **consistent**. Standard patterns let users find what they need where they expect it, in a format they are familiar with. Reference is not the place for stylistic variety or creative expression.

### Respect the Structure of the Machinery

The structure of the documentation should mirror the structure of the product. Just as a map corresponds to the territory, documentation should correspond to the logical and conceptual arrangement of the code or system.

### Provide Examples

Examples are valuable ways of providing illustration that help readers understand reference, while allowing the writer to avoid becoming distracted from the job of describing. An example of usage of a command can be a succinct way of illustrating context without falling into the trap of trying to explain or instruct.

## Language of Reference

Reference uses **factual statements** to state facts about the machinery and its behaviour:

- *"Django's default logging configuration inherits Python's defaults."*
- *"Sub-commands are: a, b, c, d, e, f."*
- *"You must use a. You must not apply b unless c."*
- *"Never d."*

Provide warnings where appropriate, but stay in the realm of description.

## Auto-Generated Reference

Some reference material (such as API documentation) can be generated automatically by the software it describes. This is a powerful way of ensuring faithful accuracy to the code. However, auto-generated reference alone is rarely sufficient — it must be complemented by well-structured manual reference and the other three documentation modes.
