# Agent template

A new agent earns its place only through a distinct tool sandbox, independence from the author (a gate), a distinct model tier, or a distinct activation condition. Domain knowledge alone is a skill.

```markdown
---
name: agent-name                      # = filename
description: "<what it does, ≤250 chars incl. Not for:>. Not for: <x> (`other-agent`)."
model: sonnet                         # opus | sonnet | haiku | inherit
tools: Read, Grep, Glob, Skill        # omit what it must never do; a shell lifts the sandbox
skills:                               # preloaded at startup — only what every run needs
  - agent-protocol
  - <role-method-skill>               # if the role has one
  - <every-run-standard>
color: blue
---

## Role
- **Mission:** <what this agent delivers>.
- **Quality bar:** <what a correct result looks like>.
- **Boundary:** <adjacent work> → `other-agent`.

## Owns
- **<artifact>:** <path or pattern> — <condition, if any>.

## Inputs
- **<input>:** <what the brief must carry>. Absent → `Blocked` | <stated default>.

## Method
1. **<step>:** <what to do>.

## Skills (on demand)
### <Group>
- **`skill-a`** (first): <when to invoke>.
- **`skill-b`:** <when to invoke>.

## Checklist
- [ ] **<item>:** <action> — evidence: <what `Verified` cites>.

## Return extras
- **`<Field>:`** <content and format>.

## Never
- **<limit>:** <the forbidden act> → <what to do instead>.
- **Shell:** <the only commands it may run>.
```

## Format
- **Bullets only:** every item is `- **<label>:** <one short line>`; a `Checklist` item is `- [ ] **<label>:** ...`. No prose paragraphs.
- **One fact per bullet:** split a bullet that needs "and" twice.
- **Subsections:** a section past ~8 bullets, or mixing concerns, splits into `###` titles, each with full bullets.
- **Length:** aim for ≤50 lines per file. A soft limit: when the role's content genuinely needs more, go past it; never cut a required item to fit.
- **Exhaustive lists:** `Owns`, `Inputs`, `Skills`, `Checklist`, `Return extras` and `Never` list every item; never trim them to save lines.
- **No restating:** name a rule, standard or the envelope by file or skill; never copy its text.

## Sections
- **Always:** `Role`, `Inputs`, `Checklist`, `Never`.
- **`Owns`:** whenever `tools` has Write or Edit.
- **`Method`:** only when no method skill covers the role's steps; numbered, one line each.
- **`Skills (on demand)`, `Return extras`:** only when non-empty.

## Rules
- **`Role` carries the boundary:** the agent never sees its own `description`, so `Role` restates who owns the adjacent work.
- **`Checklist` is per role, standing:** the brief's acceptance criteria are per task. `Done` needs both passed.
- **Checklist items are checkable:** each names its evidence; `Verified` reports every item `pass | fail | n/a — why`; a fail or a skip → `Partial`, never `Done`.
- **Checklist excludes `agent-protocol`:** side-effect cleanup, evidence paths and the envelope are already there.
- **Shell lifts the sandbox:** Bash or PowerShell can write anywhere. An agent that must not edit but needs a shell lists its allowed commands under `Never`, as `code-reviewer` does.
- **Preload:** `agent-protocol` always; the role's method skill when one exists (`code-review-method`); a standard applied on every run (`csharp-standards` for C# writers and `code-reviewer`, `qa-standards` for QA, review and build agents). Everything else goes under `Skills (on demand)`, and the agent gets the `Skill` tool.
- **On-demand triggers:** give the trigger whenever the skill's name does not make it obvious; mark the one to try first `(first)`.
