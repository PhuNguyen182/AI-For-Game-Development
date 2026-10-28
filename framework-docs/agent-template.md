# Agent template

A new agent earns its place only through a distinct tool sandbox, independence from the author (a gate), a distinct model tier, or a distinct activation condition. Domain knowledge alone is a skill.

```markdown
---
name: agent-name                      # = filename
description: "<what it does, ≤250 chars incl. Not for:>. Not for: <x> (`other-agent`)."
model: sonnet                         # opus | sonnet | haiku | inherit
tools: Read, Grep, Glob, Skill        # the hard sandbox; omit what it must never do
skills:                               # preloaded at startup — keep to what every run needs
  - agent-protocol
  - csharp-standards                  # code writers and code-reviewer
  - qa-standards                      # QA, review, build agents
color: blue
---

## Owns
- <artifacts only this agent writes>

## Inputs
- <what the brief must carry> — absent: `Blocked` | <stated default>.

## Skills (on demand)
`skill-a` · `skill-b`

## Return extras
<fields beyond the `agent-protocol` envelope>

## Never
- <hard limits a capable engineer in this role might still break>
```

- Body ≤25 lines, bullets only. Never restate a rule, a standard or the envelope.
- Preload only skills used on every run; list the rest under `Skills (on demand)` and give the agent the `Skill` tool.
