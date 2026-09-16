# Shared — Track Standards Index

Applies to: every agent and the orchestrator. Like `language-and-comments.md`, this file sits above the
groups rather than inside one.

## Why the track standards are not loaded here

Everything under `.claude/rules/` enters **every** session and **every** agent dispatch before a word is
typed. That is correct for a rule the whole project obeys — `security.md`, `orchestration.md`,
`language-and-comments.md`. It was wrong for the two **track** folders: 756 lines of C# style, Unity
performance technique and QA evidence standards were being paid for by the router, by `producer`, by
`researcher` and by `advisor`, none of which will ever write a line of C# or judge a test.

Their `Applies to:` headers were documentation, not a loading mechanism. So they moved:

```text
.claude/rules/       ← loaded always. Project-wide rules only.
.claude/standards/   ← loaded on demand, by the agents whose track they govern.
```

**Nothing was weakened.** A standard binds the code whoever writes it, exactly as before — what changed is
who pays to have it in context. Every agent the standards govern already carries a required-reading table
naming its own files; that table is now the loading mechanism rather than a citation.

## Who reads what, and when

| Standard | Read by | When |
|---|---|---|
| `.claude/standards/client/coding-principles.md` | `csharp-engineer`, `unity-engineer`, `ui-ux-programmer`, `technical-artist`, `netcode-engineer`, `server-authoritative-engineer`, every `tech-lead-*`, `code-reviewer` | Before writing or reviewing any client-track code |
| `.claude/standards/client/code-style-and-layout.md` | the same | With `coding-principles.md` — the two are explicitly not substitutes |
| `.claude/standards/client/naming-convention.md` | the same | Naming any identifier, file or namespace |
| `.claude/standards/client/performance-and-algorithms.md` | the same, plus `performance-qa-engineer` | Any hot path, data-structure choice or engine-level optimization |
| `.claude/standards/client/feature-documentation.md` | the implementing agent that owns a feature root, `code-reviewer` | A feature reaches completion at **A3** or above |
| `.claude/standards/qa/verification-standards.md` | every QA-track agent, `assurance-evaluator` | Before claiming anything is verified |
| `.claude/standards/qa/defect-reporting.md` | every QA-track agent | Before stating a finding |

## The rules that did not move, and why

`security.md`, `orchestration.md`, `task-classification.md`, `effort-allocation.md`, `execution-loop.md`,
`feature-context-reading.md`, `implementation-note.md`, `commit-message.md`, `language-and-comments.md`,
`shell-preference.md`, `unity-tooling-preference.md` and this file stay in `.claude/rules/`. Each one binds
**every** agent regardless of track — an agent that has not read `security.md` cannot know it needed to, and
`orchestration.md` is the ignition without which nothing in `.claude/workflows/` ever runs.

That asymmetry is the whole test for where a file belongs: **a rule you must obey before you know it exists
is loaded; a standard you consult when you reach its domain is read.**

## Rules

- A dispatch brief for a track agent names the standards that agent must read, per
  `workflows/references/development-brief.md`. Naming them is what replaces auto-loading.
- Never copy a standard's content into a brief, a rule or a workflow file — one fact, one home. Cite the path.
- A new project-wide rule goes in `.claude/rules/` and is added to the list above; a new track standard goes
  in `.claude/standards/<track>/` and gets a row in the table above. A file in neither list is unreachable.
- `workflows/tools/verify-workflow-layer.ps1` checks that every standard has a reader and that no path here
  is dangling. A standard nobody is told to read is the same defect as a rule nobody loads.
