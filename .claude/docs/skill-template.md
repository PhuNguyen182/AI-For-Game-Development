---
name: [skill-name-in-kebab-case]
description: >
  [Retrieval index, not a summary. This is the ONLY text Claude sees before
  deciding whether to open the skill, so it must contain the tokens an
  incoming request will actually match against. Target 80–250 words, in
  three ordered parts:

  (1) SURFACE — name the concrete technical surface: package ID, namespaces,
  class/attribute/method names, Editor window paths, config keys. Symbols are
  what makes retrieval fire; prose about "best practices" is not.

  (2) WHEN — the task shapes that should open this skill, phrased the way the
  requester phrases them, not the way the docs title them.

  (3) WHAT NOT — one "Do not use this for X — that's `neighbour-skill`"
  clause per adjacent skill this could be confused with. Every boundary gets
  its own clause; an unstated boundary is a skill that fires on the wrong
  task.

  Be explicit and pushy. Skills under-trigger far more often than they
  over-trigger, and a vague description fails silently — it never fires and
  never reports that it didn't.]
---

<!--
=====================================================================
 AUTHORING THIS SKILL — delete this block once the file is filled in
=====================================================================
 1. Path: .claude/skills/<group>/<skill-name>/SKILL.md
    <group> ∈ client | architecture | live-ops  (see Appendix A.1)
    `name:` above MUST equal the leaf folder name — NOT the group path.
 2. Fill every [bracketed] slot. Sections 1–8 are all mandatory and keep
    their numbers; do not add, drop, renumber, or reorder them. The
    "Bundled resources" block is deliberately unnumbered so §1–§8 stay
    stable whether or not the skill ships extra files.
 3. Keep SKILL.md under ~180 lines. Push depth into references/*.md and
    cite each file at its point of use in §4.
 4. The skill folder must be self-contained and drop-in portable across
    projects — obey the Portability contract in Appendix A.3.
 5. Appendix A (conventions) and Appendix B (checklist) at the bottom of
    this template are authoring aids — delete both before shipping.
=====================================================================
-->

# [Skill Name — Technical Subject + Scope]

## Bundled resources
<!-- Inventory of every file shipped inside this skill folder. Delete this
     whole block if the skill ships none; delete any table that has no rows.
     Every path is relative to THIS file (Appendix A.3). Listing a file here
     is not enough — cite it again at its point of use in §4. -->

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | [upstream doc/API root links this skill was built from] | [starting any task in this domain] |
| [topic-a.md](references/topic-a.md) | [specific concepts/API surface it holds] | [the concrete condition that makes it worth loading] |

### Scripts
Deterministic logic Claude executes with Bash instead of reimplementing inline.

| File | Purpose | Run when | Input → Output |
|---|---|---|---|
| [scripts/name.py](scripts/name.py) | [what it does] | [trigger, e.g. "before writing final output"] | [args/files] → [what it produces] |

### Assets
Files inserted verbatim into the deliverable (templates, boilerplate, config stubs).

| File | Purpose | Used in |
|---|---|---|
| [assets/name.ext](assets/name.ext) | [what it is] | [where it lands in the output] |

## 1. Objective
[One paragraph, outcome-first: what correct result this skill guarantees, and which specific failure modes it prevents. Name the failures concretely — "without silently corrupting numeric data across locales, leaking file handles, or materializing a huge file into memory" beats "ensures best practices are followed".]

## 2. Role
[One or two sentences. The expertise Claude adopts while the skill is active, anchored to a track: "Act as the <specialty> specialist for the client track — the tool reached for whenever <concrete situation>."]

## 3. When to invoke this skill
- [Positive trigger — a concrete task shape, naming the API/symbol it resolves to.]
- [Positive trigger — a symptom the requester reports, not the solution's name.]
- [Positive trigger — a file/asset/config type being edited.]
- Negative trigger: [what this looks like but is not] — that's `neighbour-skill`.
- Negative trigger: [second boundary] — that stays with `other-skill`/`role-name`.

## 4. How to use this skill
[Numbered, imperative, decision-ordered — earlier steps constrain later ones. Bold the directive, then justify it. Cite bundled files inline at their point of use, and name the governing `.claude/rules/*.md` file where a project rule applies.]

1. **[Hard constraint that must be settled first]** — [why; what breaks otherwise].
2. **[Default technique]**, per [topic-a.md](references/topic-a.md). [State the escalation condition: reach for the heavier option only once <condition> — don't pre-build it (YAGNI).]
3. **[Choice between two valid techniques]** — [the criterion that decides it, not "it depends"].
4. **[Deterministic step delegated to a script]** — run [scripts/name.py](scripts/name.py) rather than reproducing its logic by hand; resolve its path against this skill's own folder.
5. **[Step governed by a project rule]**, per `coding-principles.md`'s <section name> section.
6. **[Verification step]** — [what must be measured/confirmed before the result is claimed, per `performance-and-algorithms.md`'s Verification section].
7. **[Fallback when required input is missing or ambiguous]** — [ask, or proceed on a flagged assumption; never leave this undefined].

## 5. Specific goals / tasks this skill performs
- [Concrete, checkable deliverable.]
- [Concrete, checkable deliverable.]
- Out of scope: [adjacent concern] (`other-skill`), [adjacent concern] (`role-name`).
<!-- The "Out of scope:" bullet is mandatory and always last. -->

## 6. Output format
```
## [Skill Subject] Work — <feature/system name>
- [Decision axis]: <options> — rationale
- [Decision axis]: <options, or "not applicable">
- [Rule-compliance line]: <what was confirmed, per the governing rule>
- [Verification line]: <measurement/evidence, or how it was confirmed>
- Layer: <Game.Core.* / Game.Client.* / Editor-only>
- Known limitations: <...>
```
<!-- Above is the *technique* archetype (client/). For a *decision* or *gate*
     skill (architecture/, live-ops/), replace the last two lines with
     `- Decision: <option>` or an explicit `PASSED / BLOCKED` verdict plus
     `- Routed to: <role>`. Both archetypes stay a literal, copy-pasteable
     block — never a prose description of what the output should contain. -->

## 7. Examples
**Example 1**
- Input: [realistic request, with the state of the code/project that makes it concrete]
- Output: [what the skill produced — named APIs, chosen options, and the rule that drove each choice]

**Example 2**
- Input: [a plausible but wrong suggestion, quoted: "just do X, it's simpler"]
- Output: declined — [why it fails], [what was done instead, citing the rule].
<!-- Keep at least one refusal example: it teaches the boundary that the
     positive examples cannot. -->

**Example 3**
- Input: [an edge case that exercises a different branch of §4]
- Output: [...]

## 8. Edge cases & guardrails
- Never [the highest-cost mistake in this domain] — [the concrete consequence].
- Never [a shortcut that looks correct locally but breaks a project rule] — per `coding-principles.md`'s <section> section.
- Never [premature complexity this skill's power invites] — that's speculative complexity YAGNI already forbids.
- If [input is missing/ambiguous], [ask rather than assume / proceed on a stated assumption] — do not guess.
- [If this skill can trigger anything destructive or hard to reverse — build, deploy, publish, delete, force-push, spend money, call an external system — state here that it requires explicit user confirmation in the current conversation, never inferred from context.]

---
---

# APPENDIX A — Conventions (authoring aid; delete before shipping)

## A.1 Placement

| Group | Contains | Primary consumers |
|---|---|---|
| `client/` | Implementation technique — Unity APIs, C# libraries, rendering, tooling | Client-track engineer agents |
| `architecture/` | Decision frameworks for hard-to-reverse technology choices | CTO, Technical Architect |
| `live-ops/` | Production incident and operations procedures | crash-anr-investigator |

Path is `.claude/skills/<group>/<name>/SKILL.md`; `name:` equals the **leaf** folder only, kebab-case, unique across all groups.

## A.2 Normative rules

| Scope | Rule |
|---|---|
| Frontmatter | Exactly two keys: `name`, `description`. **MUST** — no other keys. |
| `description` | **MUST** enumerate the concrete API/symbol surface, **MUST** carry ≥1 `Do not use…` boundary clause naming the skill that owns it instead. |
| Structure | Sections 1–8, numbered, in order, none omitted. **MUST** |
| Bundled resources | Present iff the folder ships files beyond SKILL.md; one table per type, only the tables that have rows. Unnumbered, directly under the H1. **MUST** |
| §3 | Every boundary in `description` restated as a `Negative trigger:` bullet. **MUST** |
| §4 | Each step bolds its directive and states *why*; cite every bundled file inline at its point of use; name the governing `.claude/rules/*.md` file as ``` `file.md`'s <Section> section ```. **SHOULD** |
| §5 | Final bullet is `Out of scope:`, routing each excluded concern to the owning skill or role. **MUST** |
| §6 | A literal fenced block, not prose. Technique archetype ends `Layer:` + `Known limitations:`; decision/gate archetype ends `Decision:` or a verdict + `Routed to:`. **MUST** |
| §7 | 2–4 Input/Output pairs, ≥1 of which is a declined wrong suggestion. **SHOULD** |
| §8 | Guardrails as `Never …` imperatives, each with its consequence. **SHOULD** |
| Size | SKILL.md ≤ ~180 lines; overflow moves to `references/*.md`. **SHOULD** |
| Language | English throughout, per `.claude/rules/language-and-comments.md`. **MUST** |

## A.3 Portability contract

A skill folder is a self-contained, drop-in unit. It must resolve identically after being copied into any project, under any group folder, with or without its neighbours present. That holds only if **no link ever escapes the skill's own folder**.

| Target | Correct form | Why |
|---|---|---|
| Bundled file, cited from `SKILL.md` | `[topic-a.md](references/topic-a.md)`, `[name.py](scripts/name.py)` | Relative to SKILL.md; survives any relocation of the folder. |
| Sibling reference, cited from another reference | `[topic-b.md](topic-b.md)` | Same directory; no traversal. |
| Own SKILL.md, cited from a reference | `[SKILL.md](../SKILL.md)` | One level up, still inside the skill folder. |
| **Another skill** | ``` `other-skill-name` ``` — backticked name, **never a path** | The other skill may be absent, renamed, or in a different group in the target project. |
| **Project rule file** | ``` `coding-principles.md`'s <Section> section ``` — filename, **never a link** | Rules live outside the skill folder and may not exist elsewhere; a name degrades to a readable mention, a broken link does not. |
| Upstream documentation | Full `https://` URL | Absolute and project-independent by nature. |

Forbidden in every file of the skill: absolute paths, project-rooted paths (`.claude/skills/…`), and any `../../` traversal that leaves the skill folder. A cross-skill path such as `../../other-skill/references/x.md` is the single most common breakage — it silently assumes both skills sit in the same group folder in every project. Reference the other skill by name and let the reader open it.

Scripts follow the same rule for citation; at execution time, resolve `scripts/<name>` against the directory the skill was loaded from rather than assuming the shell's working directory.

# APPENDIX B — Pre-ship checklist (authoring aid; delete before shipping)

Each item maps to a distinct silent-failure mode — a skill that never fires, or one that fires and misleads.

- [ ] `name` equals the leaf folder name, kebab-case, unique project-wide; frontmatter has only `name` + `description`.
- [ ] `description` names real symbols/APIs (not just capability prose) — otherwise retrieval never matches.
- [ ] `description` has a `Do not use…` clause for **every** adjacent skill, each naming the owner.
- [ ] Every `description` boundary reappears as a §3 `Negative trigger:` bullet.
- [ ] What `description` promises is what §4 actually instructs — no promise the workflow doesn't deliver.
- [ ] §4 defines behaviour for missing/ambiguous input; §8 defines it for the failure cases.
- [ ] Any destructive or hard-to-reverse action is gated on explicit user confirmation in §8.
- [ ] Skill produces code or technical documents → §4 names the governing `.claude/rules/*.md` sections.
- [ ] §5 ends with `Out of scope:`; §6 is a literal copy-pasteable block matching its archetype.
- [ ] Every bundled file exists, appears in its "Bundled resources" table, **and** is cited in a §4 step — and every table row points at a file that exists.
- [ ] Portability: `grep -rn '](\.\./\.\./\|](\.claude/\|](/' <skill-folder>` returns nothing; cross-skill and rule-file references are names, not paths.
- [ ] Body ≤ ~180 lines; both appendices deleted.
