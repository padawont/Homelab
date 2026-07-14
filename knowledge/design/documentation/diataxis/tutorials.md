---
title: "Tutorials — Learning-Oriented Documentation"
status: draft
tags: [diataxis, tutorials, pedagogy, learning]
author: "RunicEngines Knowledge Base"
date: 2026-06-14
sources:
  - url: https://diataxis.fr/tutorials/
    title: "Diátaxis — Tutorials"
  - url: https://diataxis.fr/
    title: "Diátaxis — Home"
last_audit_date: 2026-06-14
---

# Tutorials — Learning-Oriented Documentation

A tutorial is an **experience** that takes place under the guidance of a tutor. It is always **learning-oriented** — its purpose is not to help the user get something done, but to help them *learn*.

## Core Identity

A tutorial is a **lesson**: a practical activity in which the student learns by doing something meaningful towards an achievable goal. What the student *does* is not necessarily what they *learn* — through doing, they acquire theoretical knowledge, understanding, familiarity, and the names of things.

### The Teacher-Student Contract

In a tutorial, nearly all responsibility falls on the teacher (the documentation author):

| Responsibility | Description |
|---|---|
| What the pupil learns | The teacher defines the learning objectives |
| What the pupil does | The teacher designs the learning activity |
| The pupil's success | The teacher ensures the lesson is completable |

The pupil's only responsibility is to be attentive and follow directions.

### Requirements for a Good Exercise

A tutorial exercise must be:

- **Meaningful** — the pupil needs a sense of achievement
- **Successful** — the pupil must be able to complete it
- **Logical** — the path through it must make sense
- **Usefully complete** — the pupil encounters all the actions, concepts and tools they need to become familiar with

## The Problem of Tutorials

Tutorials are genuinely difficult to do well. Common challenges include:

- **Conflation with how-to guides** — tutorials and how-to guides are frequently confused
- **Absent teacher** — in documentation, the teacher cannot be present to interact with or respond to the student
- **Maintenance burden** — tutorials consume significant effort and time; changes cascade through the entire learning journey
- **Distinction between learning and doing** — the creator must devise a meaningful learning journey that delivers what needs to be learned

## Key Principles

### Show the Learner Where They Are Going

Inform the learner at the outset what they will accomplish. This helps set expectations and allows them to see themselves building towards the completed goal.

> *"In this tutorial we will create and deploy a scalable web application."*

Avoid presumptuous patterns like *"In this tutorial you will learn…"*

### Deliver Visible Results Early and Often

Let the learner see results and make connections between causes and effects rapidly and repeatedly. Every step should produce a comprehensible result, however small.

### Maintain a Narrative of the Expected

Keep up a running commentary of expectations:

- *"You will notice that…"*
- *"After a few moments, the server responds with…"*
- *"If the output doesn't show…, you have probably forgotten to…"*

This provides continuous feedback that the learner is on the right path.

### Point Out What the Learner Should Notice

Learners are typically too focused on doing to notice important signs. Prompt them in passing — e.g., pointing out how a command line prompt changes.

### Target the Feeling of Doing

The accomplished practitioner experiences a *feeling of doing* — a joined-up purpose, action, thinking, and result. Design tasks that tie purpose and action together to cradle this feeling.

### Encourage and Permit Repetition

Repetition is foundational to learning. Make it possible for steps to be repeated where feasible — watching users follow a tutorial, you may be amazed at how often they repeat a step, just to confirm the same thing happens again.

### Ruthlessly Minimise Explanation

A tutorial is **not** the place for explanation. Explanation distracts from doing. Instead, provide brief signals (e.g., *"We're using HTTPS because it's more secure"*) and link to deeper explanation elsewhere. The user will seek explanation when *they* are ready.

### Focus on the Concrete

Lead the learner from one concrete action and result to another. The mind moves from the concrete and particular towards the general and abstract, naturally — the latter will emerge from the former.

### Ignore Options and Alternatives

Stay focused on what's required to reach the conclusion. Interesting diversions, alternative commands, and different approaches can be left for another time.

### Aspire to Perfect Reliability

A tutorial must inspire confidence. Every action must produce the promised result. A learner who follows directions and doesn't get the expected result will quickly lose confidence — in the tutorial, the tutor, and themselves.

> *"You are required to be present, but condemned to be absent."*

Test extensively through observation of real users to discover flaws and gaps.

## Language of Tutorials

Tutorials use **first-person plural ("we")** to affirm the tutor-learner relationship:

- *"In this tutorial, we will…"*
- *"First, do x. Now, do y."* — step instructions use imperative mood, with "we" reserved for framing statements
- *"Notice that…" / "Let's check…"*
- *"You have built a secure, three-layer hylomorphic stasis engine…"*

The tone is collaborative — you are not alone; we are in this together.

## Anti-Pedagogical Temptations

Avoid these common pitfalls:

- **Abstraction / generalisation** — stay concrete
- **Explanation** — minimise ruthlessly
- **Choices** — ignore options
- **Information** — don't overload
