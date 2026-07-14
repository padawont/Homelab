---
title: "How-to Guides — Goal-Oriented Documentation"
status: draft
tags: [diataxis, how-to-guides, goals, problem-solving]
author: "RunicEngines Knowledge Base"
date: 2026-06-14
sources:
  - url: https://diataxis.fr/how-to-guides/
    title: "Diátaxis — How-to Guides"
  - url: https://diataxis.fr/
    title: "Diátaxis — Home"
last_audit_date: 2026-06-14
---

# How-to Guides — Goal-Oriented Documentation

How-to guides are **directions** that guide the reader through a problem or towards a result. They are always **goal-oriented** — concerned with *work*, navigating from one side to the other of a real-world problem-field.

## Core Identity

A how-to guide helps the user get something done, correctly and safely. It guides the user's *action*.

> Examples: *How to calibrate the radar array*; *How to use fixtures in pytest*; *How to configure reconnection back-off policies.*

> Non-example: *How to build a web application* — that is not addressing a specific goal or problem, it's a vastly open-ended sphere of skill.

A rich list of how-to guides frames what a product can actually *do*, making it an encouraging suggestion of capabilities.

## Written from the User's Perspective

**How-to guides must be written from the perspective of the user, not of the machinery.** A how-to guide is defined by the needs of a user — a human project. It should show what the human needs to do, with the tools at hand, to obtain the result they need.

### Meaningful vs Mechanical Guidance

| Mechanical (poor) | Meaningful (good) |
|---|---|
| *"To shut off the flow of water, turn the tap clockwise."* | *"How much water to run, and how vigorously, for a certain purpose."* |
| *"Select the appropriate options and press Deploy."* | *"What database configuration options align with particular real-world needs."* |

Tools appear in how-to guides as incidental bit-players — the means to the user's end, not the focus.

## What How-to Guides Are Not

### Not Tutorials

How-to guides are wholly distinct from tutorials:

| Aspect | Tutorial | How-to Guide |
|---|---|---|
| Purpose | Learning (study) | Doing (work) |
| User state | Novice, learning | Already competent, task-focused |
| Scope | Complete end-to-end | Task-specific, bounded |
| Structure | Pedagogical sequence | Logical sequence of actions |

### Not Mere Procedures

Real-world problems do not always offer themselves up to linear solutions. Sequences in a how-to guide may need to fork and overlap, with multiple entry and exit points. The guide often requires the user to rely on their judgement.

## Key Principles

### Address Real-World Complexity

A how-to guide must be adaptable to real-world use-cases. You can't address every possible case, so find ways to remain open to a range of possibilities so the user can adapt your guidance to their needs.

### Omit the Unnecessary

Practical usability is more helpful than completeness. A how-to guide should start and end in a reasonable, meaningful place, requiring the reader to join it up to their own work.

### Provide a Set of Instructions

A how-to guide describes an *executable solution*. It's in the form of a contract: if you're facing this situation, then you can work through it by taking these steps. "Actions" include physical acts, thinking, and judgement.

### Describe a Logical Sequence

The fundamental structure is a *sequence* implying logical ordering in time. Sometimes ordering is imposed by the way things must be (step two requires step one). Sometimes ordering is subtler — one operation may help set up the user's thinking in a way that benefits the next.

### Seek Flow

Ground your sequences in the patterns of the *user's* activities and thinking so the guide acquires smooth progress. Ask yourself:

- What are you asking the user to think about?
- How will their thinking flow from subject to subject?
- How long must they hold thoughts open before they can be resolved?
- If they must jump back to earlier concerns, is this necessary?

At its best, how-to documentation anticipates the user — the documentation equivalent of a helper who has the tool you were about to reach for, ready to place it in your hand.

### Pay Attention to Naming

Choose titles that say exactly what a how-to guide shows:

| Title | Assessment |
|---|---|
| *How to integrate application performance monitoring* | Good — clear about what it shows |
| *Integrating application performance monitoring* | Ambiguous — could be about whether or how |
| *Application performance monitoring* | Very bad — could be about anything |

## Language of How-to Guides

Use **conditional imperatives** from the user's perspective:

- *"This guide shows you how to…"*
- *"If you want x, do y."*
- *"To achieve w, do z."*
- *"Refer to the x reference guide for a full list of options."*

Avoid polluting the practical guide with every possible thing the user might do — link to reference instead.
