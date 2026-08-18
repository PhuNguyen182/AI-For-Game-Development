<!--
=====================================================================
 HOW TO USE THIS TEMPLATE
=====================================================================
1. Pick a variant first — see "Choosing a variant" below. Don't default
   to FULL for everything; a routine execution role forced into FULL
   just produces a long file nobody reads carefully. If you're
   RETROFITTING an existing agent, a `model: opus` on a file that's
   written in the lean QUICK shape is itself a signal it was probably
   miscategorized — check the table, don't just keep it as-is.
2. Copy the chosen variant's block to: .claude/agents/<group>/[agent-name].md
   (project-level) OR ~/.claude/agents/[agent-name].md (personal, global).
3. Fill in every [bracketed] section. Delete the variant you didn't use
   and this whole comment block before saving.
4. Keep `tools` as narrow as possible — a subagent that only reviews
   code shouldn't have Write/Edit access. When the agent needs an MCP
   tool, use its full namespaced name (e.g. `mcp__unity-mcp__Unity_RunCommand`),
   and verify it against the project's actually-connected MCP servers —
   never guess or shorten a tool name.
5. The body of the file becomes the subagent's SYSTEM PROMPT — write it
   as direct instructions to the agent, not as documentation about it.
6. Before considering the file done, run it through the "Post-write
   validation checklist" at the bottom of this document. Every item
   there maps to a real defect class found in past agent files — it is
   not boilerplate.
=====================================================================
-->

# Agent Template

## Choosing a variant

| Role character | Signal | Variant |
|---|---|---|
| Escalation, leadership, cross-cutting architecture, or advisory judgment | Invoked rarely, on hard/ambiguous problems that routine work already failed to resolve; decisions have wide blast radius or are hard to reverse | **FULL** |
| Routine execution against a clear spec | Invoked constantly, on well-scoped work with a known Input → Output shape; correctness is checked against a Tech Spec or existing convention, not open judgment | **QUICK** |

Rule of thumb: if the agent's job is "make a call nobody else is positioned to make," use FULL. If the agent's job is "do the thing correctly, the way this project always does it," use QUICK. When unsure, start QUICK — it's cheap to upgrade a QUICK agent to FULL later if it turns out to need deeper behavioral specification, but a FULL template filled in half-heartedly for a simple role is worse than the lean version.

The `model` field is a tell, not just a config value: if a file is `model: opus` but shaped as QUICK, that mismatch itself is a defect to fix — either the role really is judgment-heavy and belongs in FULL, or it doesn't and the model should drop to `inherit`/`sonnet`. Don't let the two drift apart.

## Shared conventions (apply to both variants)

- **Model selection**: `opus` for FULL-variant roles (leadership/architecture/tech-lead/escalation — the judgment is the expensive part); `inherit` (or `sonnet`) for QUICK-variant roles doing routine implementation work; use `haiku` only for narrow, high-volume, low-judgment tasks.
- **Rules-file reference**: if this project has `.claude/rules/<group>/*.md` files for the agent's group, the agent's Rules/Guardrails section MUST include an explicit instruction to read them before acting — don't assume the agent will discover them on its own.
- **Tool names**: list tools by their exact registered name, including full MCP prefixes (`mcp__<server>__<Tool>`). A narrowed-but-wrong tool list silently breaks the agent at call time.
- **`color`**: optional but recommended on every agent for quick visual grouping in tooling; pick one color per role-group (or per escalation tier, if a group has both routine and escalation-only roles — e.g. tech-leads get their own tier color distinct from routine engineers in the same group) and reuse it consistently, not one-off per file.
- **Escalation symmetry**: if this agent's file states it escalates TO another agent, or receives escalations FROM another agent, the *other* agent's file must state the matching half of that relationship. A one-sided escalation rule is a silent gap — the receiving agent won't know to expect the handoff, or the sending agent won't know where to route a failure.
- **Ground-truth cross-check**: if this project has an authoritative process/role document (e.g. a team-structure spec), this agent's stated Input/Output must match what that document assigns to the role — no silently dropped or invented responsibilities.
- **Description ↔ body sync**: the `description` field is the only thing the dispatcher reads before delegating. Everything it promises (scope, triggers, output) must actually be delivered by the body below it — a description that oversells or undersells the body is a dispatch-time bug, not a style issue.
- **Undefined-input behavior**: every agent will eventually be invoked with incomplete or ambiguous input. State explicitly what this agent does then — ask the caller, proceed on a clearly-flagged assumption, or escalate — rather than leaving it to improvise silently.
- **Destructive/hard-to-reverse actions**: if this role could plausibly touch anything destructive or hard to reverse for this project (build, deploy, publish, delete, force-push, spend money, contact external systems), that must be explicitly gated behind an explicit user/GD request in the current conversation — state this as a hard rule, not an assumption.

---

## VARIANT: FULL — for judgment-heavy / escalation roles

```yaml
---
name: [agent-name-in-kebab-case]
description: >
  [One to three sentences describing what this subagent is for and,
  critically, WHEN the main Claude session should delegate to it.
  Claude Code decides whether to invoke this subagent based on this
  description, so be specific about trigger situations. Example:
  "Use this agent to review pull requests for security issues. Invoke
  it whenever the user asks for a code review, security audit, or
  before merging a PR — even if they just say 'check this over'."]
tools: [Read, Grep, Glob, Bash]   # optional — omit to inherit all tools;
                                  # list only what this agent actually needs
model: opus                      # optional — sonnet | opus | haiku | inherit
color: [optional — one color per role-group/escalation-tier, reused consistently]
---
```

# [Agent Name]

## 1. Objective (what this agent exists to accomplish)
[One paragraph, written as if speaking to the agent itself. Example:
"You exist to catch security vulnerabilities and unsafe patterns in
pull requests before they merge, so the human reviewer only needs to
focus on logic and design."]

## 2. Role (persona and scope of expertise)
[Describe who this agent should act as. Example: "You are a senior
application-security engineer. You are thorough, skeptical by default,
and you explain risk in terms a non-security engineer can act on."]

## 3. When you are called (context you can assume)
- [What kind of request triggers this agent, e.g. "a PR diff or set of
  changed files is provided"]
- [What the calling session expects back, e.g. "a structured list of
  findings, not a full rewrite of the code"]
- [What you should assume is already done, e.g. "tests have already run;
  you are not responsible for running the test suite"]
- [What escalates TO this agent and what this agent escalates further UP
  to, if applicable — e.g. "called after routine implementation failed 3
  times; escalate strategic/hard-to-reverse tech decisions to CTO."
  Confirm the reciprocal file states the matching half (see Escalation
  symmetry above).]

## 4. How you should work (operating instructions)
1. [Step 1 — e.g. "Read every changed file with Read/Grep before opining"]
2. [Step 2 — e.g. "Classify each finding as Critical / High / Medium / Low"]
3. [Step 3 — e.g. "For each finding, cite the exact file and line"]
4. [Step 4 — e.g. "Never modify files yourself — only report findings"]
5. [If input is incomplete or ambiguous: state the concrete fallback —
   ask the caller / proceed on a flagged assumption / escalate — don't
   leave this undefined]
6. [Step N — continue as needed; delete steps that don't apply rather
   than padding the list to look thorough]

## 5. Specific goals / responsibilities
- [Goal 1, e.g. "Flag injection risks (SQL, command, template)"]
- [Goal 2, e.g. "Flag missing authorization checks on new endpoints"]
- [Goal 3, e.g. "Flag secrets or credentials committed in plaintext"]
- [Explicitly state what is OUT of scope, e.g. "Do not comment on code
  style or naming — that is handled by a different agent/linter."]

## 6. Output format
ALWAYS return your findings in this exact structure:
```
[Paste the literal report/response schema the agent must return.
e.g.:
## Findings
### [Severity] [Short title]
- File: path/to/file.ext:line
- Issue: ...
- Recommendation: ...
]
```

## 7. Examples
**Example 1**
- Input: [brief description of the diff/situation given to the agent]
- Output: [what a good response looks like]

**Example 2**
- Input: [...]
- Output: [...]

## 8. Guardrails
- [Hard constraints — e.g. "never run destructive Bash commands",
  "never push or merge anything"]
- [If applicable: "Before acting, read `.claude/rules/<group>/*.md` and follow them."]
- [If applicable: gate any destructive/hard-to-reverse action behind an
  explicit user/GD request in the current conversation — see Shared
  conventions above]
- [When to escalate/ask instead of guessing]
- [Tone/verbosity constraints, e.g. "be concise — the calling agent
  will summarize you for the human"]

---

## VARIANT: QUICK — for routine execution roles

```yaml
---
name: [agent-name-in-kebab-case]
description: "[When the main session should delegate to this agent, plus
  2-4 concrete trigger examples in quotes — same specificity bar as FULL,
  just written inline instead of as a paragraph. Example: 'Implements UI
  screens from the Tech Spec and wires them to gameplay state. Examples:
  \"build the inventory panel from the Tech Spec\", \"make the HUD
  responsive across PC and mobile\".']"
model: inherit                   # inherit | sonnet | opus | haiku
tools: [Read, Write, Edit, Bash] # exact tool names, incl. full MCP prefixes
color: [optional — match the role-group's/tier's color]
---
```

You are the [Agent Name] — [one-sentence role summary].

## Input
[What this agent receives to act on — a spec, a piece of code, a report from another agent.]

## Task
[What this agent does with that input, in 1-3 sentences. State any hard scope boundary here if one role's job could be confused with a neighboring role's — e.g. "own X; Y belongs to [other agent], don't duplicate it."]

## Output
[What this agent produces and hands off, and to whom/what happens next. If another agent or automated step parses this output, state the expected shape explicitly rather than leaving it prose-only.]

## Rules
- [If applicable: "Before writing any code, read `.claude/rules/<group>/*.md` and follow them."]
- [Any hard boundary this role must never cross — e.g. "never build/deploy without explicit user request", "never reimplement logic owned by another module"]
- [If input is incomplete or ambiguous: the concrete fallback — ask / flagged assumption / escalate]
- [If this role's failures or hard blockers should route to a specific escalation partner, name it here — and confirm that partner's own file states it receives escalations from here]
- [Scope discipline — e.g. "stay scoped to what was asked; flag unrelated issues separately instead of fixing them here"]

---

## Post-write validation checklist

Run through every item before treating an agent file as done. Each one maps to a real defect class seen in practice, not a hypothetical:

- [ ] YAML frontmatter parses cleanly — any `: ` or embedded `"` inside `description` is inside a properly quoted/escaped string, not a bare scalar.
- [ ] `name` matches the filename exactly (kebab-case) and is unique across the *entire* `.claude/agents/` tree, not just its own folder.
- [ ] `description` gives the dispatcher at least 2 concrete, quoted trigger examples — not a vague restatement of the role's title.
- [ ] `model` matches the variant/role heuristic. A mismatch (e.g. `opus` on a QUICK-shaped file) means the variant choice itself is probably wrong — fix that, not just the model value.
- [ ] Every entry in `tools` is a real, exactly-named built-in or MCP tool, verified against what's actually connected in this project — not recalled from memory or guessed.
- [ ] If this agent's group has a `.claude/rules/<group>/*.md` folder, the Rules/Guardrails section explicitly instructs reading it before acting.
- [ ] Header structure matches the chosen variant exactly — no invented, one-off section names that diverge from every other agent in the set.
- [ ] Any stated escalation relationship is symmetric — the partner agent's file states the matching half.
- [ ] Stated Output matches what the project's authoritative process document (if one exists) assigns to this role — nothing silently dropped or added.
- [ ] `description`'s promise matches what the body actually instructs the agent to do.
- [ ] Behavior under missing/ambiguous input is explicit, not left for the agent to improvise.
- [ ] Any destructive or hard-to-reverse action this role could plausibly take is explicitly gated behind an explicit user/GD request in the current conversation.
