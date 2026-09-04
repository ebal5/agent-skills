---
name: show-me
description: |
  Help the user understand the current topic visually. Pick the smallest
  view that makes the key point clear: pseudocode, call tree, component
  tree, file tree, Mermaid, diff, or one focused HTML artifact.

  以下の依頼時に使用:
  - 「show me」「図で」「図解して」「可視化して」「絵にして」
  - 「構造を見せて」「フローを描いて」「どう変わるか見せて」
  - 今の議論の選択肢・構造・差分を図で示したいとき

  以下では使用しない:
  - このセッションの実装内容を段階的に理解したい場合（→ teach-me を使う）
  - 自分の計画を批判的に詰めてほしい場合（→ grilling を使う）
allowed-tools: Read, Glob, Grep, Write, Artifact
model: sonnet
effort: medium
license: MIT
metadata:
  origin: "https://github.com/ebal5/agent-skills"
  upstream: "humanlayer/skills"
  upstream-path: "plugins/show-me/skills/show-me"
  upstream-ref: "main"
  upstream-sha: 3c2629142c5d437428269b1b722b08c0b87f574d
---

<!-- Based on https://github.com/humanlayer/skills (MIT License,
     Copyright (c) 2026 HumanLayer) -->

Help the user understand the current topic of conversation visually. Skip
the preamble and keep prose brief. Pick the smallest view that makes the
key point clear.

- Show logic or an algorithm as pseudocode:

```text
on(save)
  if content is unchanged
    return cached result
  write new content
  return fresh result
```

- Show runtime control flow as a call tree:

```text
submitForm
  createSession
    persistPrompt
    launchAgent
  navigateToSession
```

- Show UI structure as a component tree, including state and module
  boundaries that matter:

```tsx
<SessionPage> (apps/example/src/routes/session.tsx)
  useSessionEvents()
  <SessionToolbar>
    <RunSkillButton> (packages/ui)
```

- Show file responsibility or a broad refactor as a shallow file tree:

```text
src/
├── commands/       # parses user actions
├── sessions/       # owns session state
└── transport/      # sends API requests
```

- Show component interaction, control flow, or data flow with Mermaid:

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Daemon
    User->>UI: choose command
    UI->>Daemon: send expanded prompt
    Daemon-->>UI: stream result
```

- Use `diff` when the point is what changes and the surrounding shape
  already exists. Match the diff shape to the topic.

For a component change:

```diff
 <SessionPage>
   useSessionEvents()
   <SessionToolbar>
+    <RunSkillButton />
   <SessionTimeline>
+    <SkillResultCard />
```

For a file-layout change:

```diff
 src/
 ├── commands/
+│   └── show-me.ts       # expands the slash command
 ├── sessions/
-└── transport.ts
+└── transport/
+    ├── client.ts
+    └── stream.ts
```

For a call-tree or call-stack change:

```diff
 submitForm
   createSession
     persistPrompt
+    expandSkillMention
     launchAgent
-  navigateToSession
+  navigateToSession
+    subscribeToEvents
```

For a state or control-flow change:

```diff
 on(save)
-  write content
+  if content is unchanged
+    return cached result
+  write new content
+  invalidate cache
```

- Show the whole block when most of it is new, when omitted context would
  hide ownership or order, or when the user needs a copyable target shape:

```ts
function expandSkill(command: string): string {
  const skillName = command.slice(1)
  return `use the ${skillName} skill`
}
```

- For a visual UI, layout, state comparison, or concept too dense for
  Mermaid, write one focused HTML file — a diagram, an infographic, or a
  short slide deck, whichever fits the point. Match the product's colors,
  type, spacing, and components; use real labels and data; support desktop
  and mobile. Then publish it as an Artifact so the user can look at it:

```text
Write(path/to/show-me-{description}.html)
Artifact(file_path: path/to/show-me-{description}.html)
```

Give the page a `<title>` and, on its first publish, a `favicon`. Re-publish
the same file path to update the same page rather than creating a new one.
Where the Artifact tool is unavailable, save the file and hand the user its
path.

### guidance

Place each visual next to the short text it supports. Keep only the calls,
files, props, states, and boundaries needed to answer the user's current
question or the options to resolve the current discussion point.

You may use one of these, you may use several, it is unlikely you will use
all of them. Use your judgement and don't overwhelm the user.
