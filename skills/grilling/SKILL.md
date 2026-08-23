---
name: grilling
description: |
  Grill the user relentlessly about a plan, decision, or idea until
  reaching shared understanding, resolving each branch of the design tree.
  Use when the user wants to stress-test their thinking, get grilled on a
  design, or uses any "grill" trigger phrase (e.g. "grill me").
allowed-tools: Read, Glob, Grep, Agent
model: sonnet
effort: high
license: MIT
metadata:
  origin: "https://github.com/ebal5/agent-skills"
  upstream: "mattpocock/skills"
  upstream-path: "skills/productivity/grilling"
  upstream-ref: "main"
  upstream-sha: 5b15a47f2d7150f545fbcacbfe381787fc0230dc
---

<!-- Based on https://github.com/mattpocock/skills (MIT License, Copyright (c) 2026 Matt Pocock) -->

Interview the user relentlessly until you reach a shared understanding. Map
this as a **design tree**: every decision branches into the decisions that
hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose
prerequisites are already settled: the questions you can ask _now_ without
guessing at answers you haven't heard yet. Ask the whole frontier in one
round: number each question and give your recommended answer. Then wait for
the user's answers before the next round.

Each question should be formatted like so:

```text
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the
frontier outward and unblock questions that depended on them. Recompute the
frontier and ask the next round. A question whose answer depends on another
question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs
a fact from the environment (filesystem, tools, etc.), look it up yourself,
and dispatch a sub-agent when the search is broad enough to be worth it;
don't ask the user for anything you could look up yourself. Don't block on it:
a running exploration is an unsettled prerequisite, so only the questions
downstream of it wait for the result; ask the rest of the frontier now. The
_decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design
tree visited, nothing left silently assumed. Do not act on it until the user
confirms you have reached a shared understanding.
