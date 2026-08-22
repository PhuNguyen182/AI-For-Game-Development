<!--
 HOW TO USE
 1. Copy the SKELETON below to .claude/agents/<group>/<agent-name>.md.
    <group> is an existing folder under .claude/agents/ — reuse one, and add
    a new group only when no existing group owns the concern. Project level
    only: never author an agent under ~/.claude/agents/, which lives outside
    the repo and outside this standard.
 2. First check the existing agents for an overlapping owner. Two agents must
    never own the same decision — extend the current owner, don't add a rival.
 3. Fill every [bracketed] slot. All 7 sections stay, even when a slot needs a
    single line: presence is what the checklist verifies, depth is proportional
    to the role. Delete this comment block before saving.
 4. Run the Post-write checklist at the bottom. Every item maps to a real defect
    class found in shipped agent files, not a hypothetical one.
-->

# Agent Template

An agent file's body becomes that agent's **system prompt**. Write it as direct instructions to the agent, never as documentation about it. Agents are independent individuals: each stands alone, assumes nothing about what ran before it, and never reaches into another agent's scope. Four runtime facts shape every section below.

- **Isolated** — it sees only the prompt it was dispatched with, never the conversation behind it.
- **Stateless** — no memory of earlier runs. Counters and retry history belong to the caller.
- **Silent** — it cannot ask anyone mid-run. A question is *returned*, and returning ends the run.
- **Alone** — it cannot dispatch another agent. Escalation is a value it reports, not an action it performs.

## Frontmatter — exact keys, exact order, copied literally

```yaml
---
name: agent-name-in-kebab-case   # identical to the filename, unique across .claude/agents/
description: "What it does + when to delegate + 2-4 quoted trigger examples, ending with
  `Not for: <agent-id> owns <scope>.` for every adjacent role."
model: sonnet                    # fable | opus | sonnet | haiku | inherit — see Model below
tools: Read, Grep, Glob          # comma-separated list, NOT a YAML array
color: blue                      # from the registry below
---
```

- Name every tool exactly as registered. An MCP tool is `mcp__<server>__<Tool>` — read `<server>` and `<Tool>` from the MCP servers this project actually connects, and never guess, shorten, or carry a name over from another project. A narrowed-but-wrong list fails silently at call time.
- The tools list is the hard sandbox; guardrail prose is only advisory. Prefer omitting a dangerous tool over writing a rule that asks the agent not to use it.
- `description` is the only text the dispatcher reads, so a boundary stated in the body cannot prevent a wrong dispatch. Keep it a double-quoted scalar; avoid the `>` folded form, which can split a token across the fold.
- Reference another agent by its `name` id, display name only as prose — `` `tech-lead-performance` (Tech Lead – Performance) ``. Ids resolve; prose names do not.

## Skeleton — all 7 sections, in this order

# [Agent Name]

## 1. Role
[The persona and its expertise, one or two sentences, addressed as "You are …".]

## 2. Objective
[One paragraph, addressed to the agent: what it exists to accomplish, and for whom.]

## 3. When called
You receive only this prompt; you cannot see the conversation that produced it. Never guess silently, and never assume a peer already did something.
- Trigger: [the situation that should bring work here]
- Active when: [always | only when <condition, e.g. the multiplayer track is enabled>]

| Required input | If absent |
|---|---|
| [what the prompt must carry] | [proceed on a stated assumption, or return `Status: Blocked`] |

| Not for | That agent owns |
|---|---|
| `<agent-id>` | [scope] — return it, never do it yourself |

## 4. Self-assessment
Classify the task you were handed, declare the level in your output, run the matching depth. Every criterion must be observable in the input. When uncertain, go one level up.

| Level | Criterion | Depth to run |
|---|---|---|
| **Direct** | [unambiguous, established pattern, contained change] | Do it, report briefly. |
| **Considered** | [several viable approaches, or it touches a contract others depend on] | State the approach and why before acting, then verify the result. |
| **Escalate** | [needs authority or scope this role does not own, or the same task already failed twice] | Do not force it; return `Needs-decision` with `Routed to:`. |

## 5. Skills you use
Give the trigger only — the technique itself stays inside the skill. Requires `Skill` in `tools`. Write `None.` when the role uses no skill.

| Skill | Invoke when |
|---|---|
| `skill-id` | [the condition that calls for it] |

## 6. Output
Your reply is a return value handed to the caller, not a message to a person. Return exactly this shape:
```
## [Report name] — <subject>
- Status: Done | Blocked | Rejected | Needs-decision
- Assessed: Direct | Considered | Escalate
- Routed to: <agent-id> | gd | none
- Blocked — needs from caller: <what is missing | none>
[role-specific fields]
```
Give at least two examples, at least one declining a plausible but wrong dispatch:
- Input: [a typical request] → Output: [what a good return looks like]
- Input: [work owned by another agent] → Output: `Rejected`, `Routed to: <agent-id>`.

## 7. Guardrails
Read these before acting:

| Rule file | Applies |
|---|---|
| `.claude/rules/language-and-comments.md` | Always — it governs every agent. |
| `.claude/rules/<group>/*.md` | When that folder exists for your group. |

- [Hard limits — what this agent must never do.]
- [Any destructive or hard-to-reverse action — build, deploy, delete, publish, spend, contact an external system — happens only on an explicit GD request present in the current prompt.]
- The caller owns [retry counts, "same submission" identity, track state]; you cannot hold it across runs.

## Model

Match the model to the hardest level this role reaches in section 4, not to how important the role sounds. Cost is per 1M tokens, input / output — a role promoted a tier it does not need is a standing cost paid on every dispatch.

| `model` | Cost | Pick when the role's peak level is |
|---|---|---|
| `fable` | $10 / $50 | **Escalate** on long-horizon, high-stakes reasoning where a wrong call is expensive and hard to detect. Reserve it for the few roles that genuinely live there. |
| `opus` | $5 / $25 | **Escalate** — owns hard-to-reverse decisions, or is a gate whose miss costs a full cycle downstream. |
| `sonnet` | $3 / $15 | **Considered** — real work against a spec, several viable approaches, known boundaries. The default for implementation roles. |
| `haiku` | $1 / $5 | **Direct** — narrow, high-volume, mechanical work. Its context window is 200K against 1M for the others, so avoid it where the role must read a lot at once. |
| `inherit` | — | Nothing. It resolves to the session's model, so it ignores complexity and is not a cost control. Use only when this role's depth genuinely tracks the session's. |

## Colour registry

One colour per group; a group with an escalation tier gets a second colour for that tier. Reuse this table, never pick per file.

| Group | Colour | Escalation tier |
|---|---|---|
| client | blue | purple |
| qa | green | red |
| architecture | magenta | — |
| backend | teal | — |
| leadership | cyan | — |
| live-ops | orange | — |
| devops | gray | — |

## What does not belong in an agent file

| Concern | Home |
|---|---|
| Sequence, parallelism, retry loops, checkpoints | `.claude/workflows/*` |
| Cross-run state; choosing who runs next from a `Routed to:` value | the orchestrator file |
| How a technique works | the skill |
| Coding standards, naming, working language | `.claude/rules/*` |

## Post-write checklist

- [ ] `name` equals the filename and is unique across the whole `.claude/agents/` tree.
- [ ] `description` carries 2-4 quoted triggers and one `Not for:` clause per adjacent role.
- [ ] Every `tools` entry is a real, exactly-named tool; `Skill` present if and only if section 5 lists one.
- [ ] All 7 sections present, in order, with no invented section names.
- [ ] Section 3 gives a fallback for every required input and assumes nothing about prior runs.
- [ ] Section 4's criteria are observable in the input — nothing resolves to "it depends".
- [ ] Section 6 carries the four envelope fields, and one example declines a wrong dispatch.
- [ ] Every `<agent-id>` named is a real `name`, and that agent's file does not claim the same scope.
- [ ] Any destructive action is prevented by an omitted tool wherever omitting one is possible.

```bash
A=.claude/agents/<group>/<agent-name>.md
awk 'END{print NR" lines"}' $A; awk 'NF>120 {print FNR": "NF}' $A   # over-long → empty
grep -n "^tools: \[" $A                                  # YAML-array form → empty
grep -c "^## [0-9]\." $A                                 # sections → 7
grep -c "^- Status:\|^- Assessed:\|^- Routed to:" $A     # envelope → 3
grep -q "language-and-comments" $A || echo "missing global rules reference"
grep -rh "^name:" .claude/agents/ | cut -d' ' -f2 | sort # valid ids for every cross-reference
```
