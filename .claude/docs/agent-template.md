<!--
 HOW TO USE
 1. Before adding an agent, check the roster. A new agent type earns its place only through a distinct tool
    sandbox, independence from the author (a gate), a distinct model tier, or a distinct activation condition.
    Domain knowledge alone belongs in a skill. Extend the current owner rather than add a rival.
 2. Copy the SKELETON to .claude/agents/<agent-name>.md — flat, project level only.
 3. Write as few words as the role allows. Delete this comment block before saving.
-->

# Agent Template

An agent file's body is that agent's system prompt: direct instructions, never documentation. The agent is
isolated (sees only its brief), stateless (counters belong to the caller), silent (a question is returned, and
returning ends the run) and alone (escalation is a value it reports, not an action). It already knows this, and
`.claude/rules/` loads on its own — never restate either.

## Frontmatter

```yaml
---
name: agent-name                 # identical to the filename
description: "<scope, one or two sentences>. Not for: `<agent-id>` (<scope>); ..."
model: sonnet                    # fable | opus | sonnet | haiku | inherit
tools: Read, Grep, Glob          # comma-separated, never a YAML array
color: blue
---
```

- `description` is the only text the dispatcher reads; a boundary stated only in the body cannot prevent a wrong
  dispatch. Keep it a double-quoted scalar.
- `tools` is the hard sandbox. Omit a dangerous tool rather than forbid it in prose. Name MCP tools exactly as the
  connected server registers them. Shell holders get `PowerShell` before `Bash` (`shell-preference.md`).
- Reference other agents by `name` id, in backticks.

## Skeleton

~~~markdown
<What the agent does and why it exists — one to three sentences, addressed as "you".>

## Inputs
- <what the brief must carry> — absent: <`Blocked` | the stated assumption it proceeds on>.

## Skills
- `skill-id` — <when to invoke>.

## Read
- `.claude/standards/<track>/<file>.md` — <when>.

## Return
```
Status: Done | Blocked | Rejected | Needs-decision
Routed to: <agent-id> | gd | none
Needs: <missing input | none>
<role fields — reuse the field names the workflows already read>
```
<One line on non-obvious statuses, e.g. findings are still `Done`; when to return `Needs-decision`.>

## Never
- <hard limits only — what a capable engineer in this role might still do wrong here>
~~~

Omit `## Skills` or `## Read` when empty. In `## Skills`, put every skill name before the item's first ` — `;
the verifier reads only that part.

## Model

| `model` | Cost (in / out per 1M) | Pick when the role's hardest call is |
|---|---|---|
| `fable` | $10 / $50 | Long-horizon, high-stakes, hard to detect when wrong |
| `opus` | $5 / $25 | A hard-to-reverse decision, or a gate whose miss costs a full cycle |
| `sonnet` | $3 / $15 | Real work against a spec — the default for implementers |
| `haiku` | $1 / $5 | Narrow, mechanical, high volume; 200K context |
| `inherit` | — | Only when the role's depth tracks the session's |

## Colour

| Group | Colour | | Group | Colour |
|---|---|---|---|---|
| client | blue | | backend | teal |
| qa | green; gates red | | direction | cyan |
| architecture | magenta | | live-ops | orange |
| devops | gray | | | |

## Does not belong in an agent file

| Concern | Home |
|---|---|
| Sequence, retries, checkpoints, who runs next | `.claude/workflows/*` |
| How a technique works | the skill |
| Coding standards, naming, language | `.claude/rules/*`, `.claude/standards/*` |

## Checklist

- [ ] `name` equals the filename; every `<agent-id>` named exists and does not claim the same scope.
- [ ] `description` states scope and one `Not for:` entry per adjacent owner.
- [ ] Every tool is real and exactly named; `Skill` present only when `## Skills` exists.
- [ ] Every input has an `absent:` fallback; the envelope carries `Status`, `Routed to`, `Needs`.
- [ ] Nothing restates a rule file, the runtime facts above, or another section.
- [ ] `workflows/tools/verify-workflow-layer.ps1` passes.
