---
name: [skill-name-in-kebab-case]
description: >
  [Retrieval index, not a summary. 50–100 words. THIS TEXT IS THE ONLY THING
  READ when deciding whether to open the skill — the body, `references/`, and
  any file path named here are NOT fetched first. A symbol absent from this
  text cannot be matched on, and a description cannot delegate its job to a
  file. Three ordered parts:
  (1) SURFACE — the distinctive symbols a request will match on: package ID,
  namespaces, class/attribute/method names, Editor paths, config keys. Keep
  the ones no sibling skill shares; the exhaustive inventory belongs in §4
  and `references/`, which load only after the skill opens.
  (2) WHEN — the task shapes that should open this skill, in the requester's
  words, not the documentation's.
  (3) NOT FOR — every boundary as ONE terse list, never a paragraph each:
  "Not for: <concern> (`owning-skill`), <concern> (`owning-skill`)."
  Symbols over prose. A vague description fails silently: it never fires and
  never reports that it didn't.]
---

<!--
=====================================================================
 AUTHORING THIS SKILL — delete this block once the file is filled in
=====================================================================
 1. Path: .claude/skills/<group>/<skill-name>/SKILL.md
    <group> is an OPEN set — Appendix A.2 lists the groups this project has
    today and gives the test for adding a new one.
    `name:` above MUST equal the leaf folder name — NOT the group path.
 2. Obey the Writing mandate in Appendix A.1 — it is binding, not advisory.
 3. Fill every [bracketed] slot. Sections 1–8 are mandatory and keep their
    numbers; do not add, drop, renumber, or reorder them. The "Bundled
    resources" block is deliberately unnumbered so §1–§8 stay stable
    whether or not the skill ships extra files.
 4. Budget (Appendix A.3): body < 200 lines, 100–150 optimal, and no
    single line over 150–180 words. Push depth into references/*.md and
    cite each file at its point of use in §4. Every file in that folder is
    authored per `skill-reference-template.md` (same folder as this file).
 5. The skill folder must be drop-in portable across projects — obey the
    Portability contract in Appendix A.4.
 6. Appendix A and Appendix B are authoring aids — delete both before
    shipping.
=====================================================================
-->

# [Skill Name — Technical Subject + Scope]

## Bundled resources
<!-- Inventory of every file shipped inside this skill folder. Delete this
     whole block if the skill ships none; delete any table that has no rows.
     Every path is relative to THIS file (Appendix A.4). Listing a file here
     is not enough — cite it again at its point of use in §4. -->

### References
Read-only context, loaded on demand so SKILL.md itself stays short. Each file
follows `skill-reference-template.md`. "Read when" is a real condition, not a
restatement of the topic — it is what lets Claude open one file instead of all
of them.

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
[One paragraph. The correct result this skill guarantees, and the specific failure modes it prevents — named concretely: "without corrupting numeric data across locales, leaking file handles, or materializing a whole file into memory", not "ensures best practices".]

## 2. Role
[One or two sentences. The expertise Claude adopts while the skill is active, anchored to its track: "Act as the <specialty> specialist for the <track> track — the tool reached for whenever <concrete situation>."]

## 3. When to invoke this skill
- [Positive trigger — a concrete task shape, naming the API/symbol it resolves to.]
- [Positive trigger — a symptom the requester reports, not the solution's name.]
- [Positive trigger — a file/asset/config type being edited.]
- Negative trigger: [what this looks like but is not] — that's `neighbour-skill`.
- Negative trigger: [second boundary] — that stays with `other-skill`/`role-name`.

## 4. How to use this skill
[Numbered, imperative, decision-ordered — earlier steps constrain later ones. Bold the directive, then justify it in one clause. Close the bold **before** any punctuation — `**Directive**, per …` and `**Directive** — why`, never `**Directive.**` or `**Directive,**` — because a reference file's `Covers:` line quotes this text verbatim and a swallowed period breaks the match. Every step ends in a decision or a named criterion that produces one. Cite bundled files inline at their point of use.]

1. **[Hard constraint that must be settled first]** — [why; what breaks otherwise].
2. **[Default technique]**, per [topic-a.md](references/topic-a.md). [Escalation condition: reach for the heavier option only once <condition> — don't pre-build it (YAGNI).]
3. **[Choice between two valid techniques]** — [the criterion that decides it. Never "it depends".]
4. **[Deterministic step delegated to a script]** — run [scripts/name.py](scripts/name.py) rather than reproducing its logic by hand; resolve its path against this skill's own folder.
5. **[Step governed by a project rule]**, per `coding-principles.md`'s <section name> section.
6. **[Verification step]** — [what must be measured or confirmed before the result is claimed, per `performance-and-algorithms.md`'s Verification section].
7. **[Fallback when required input is missing or ambiguous]** — [ask, or proceed on a flagged assumption. Never leave this undefined.]

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
<!-- Pick the archetype by what the skill DELIVERS, never by which group
     folder it sits in — a new group would otherwise have no archetype.
     Above is the *technique* archetype: the skill applied a method and
     reports what it did and where. A *decision/gate* skill — one whose
     deliverable is a verdict — replaces the last two lines with
     `- Decision: <option>`, or an explicit `PASSED / BLOCKED` plus
     `- Routed to: <role>`. Both archetypes stay a literal, copy-pasteable
     block — never a prose description of what the output should contain. -->

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```
<!-- Never pad these three. A limitation that doesn't exist, a concern that is
     really a limitation, or a remediation with no trigger condition are all
     noise. Omit the field instead. -->

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

## A.1 Writing mandate

Binding on every skill in this set.

| Rule | In practice |
|---|---|
| **Domain language** | Name the actual API, type, attribute, setting, threshold, and unit. "Configure the component appropriately" is unusable; "set `Rigidbody2D.collisionDetectionMode` to `Continuous`" is the standard. |
| **Concision** | Cut every sentence that does not change what Claude does. No filler, no restating the heading, no hedging qualifiers. |
| **Clear, coherent structure** | One idea per bullet, decision-ordered steps, parallel phrasing across sections. A reader should be able to act from §4 alone without reconstructing intent from prose. |
| **Definitive resolution** | Every step terminates in a decision or in a named criterion that produces one. "It depends" is never an output — state the deciding factor. Ambiguity gets an explicit fallback in §4 and §8, never silence. |
| **Conditional report tail** | On request, the §6 output carries `Known limitations` / `Latent concerns` / `Future remediation`. Unrequested, it stays out. |

## A.2 Placement

Path is `.claude/skills/<group>/<name>/SKILL.md`; `name:` equals the **leaf** folder only, kebab-case, unique across **all** groups — not merely within its own.

`<group>` is an **open set, project-local**. A group partitions skills by *who reaches for them and for what kind of work*, not by subject matter. The groups below are this project's set today, not the schema:

| Group | Contains | Primary consumers |
|---|---|---|
| `client/` | Implementation technique — Unity APIs, C# libraries, rendering, tooling | Client-track engineer agents |
| `architecture/` | Decision frameworks for hard-to-reverse technology choices | CTO, Technical Architect |
| `qa/` | Verification and gating method — audits, scans, test design, evidence discipline | QA-track agents |
| `live-ops/` | Production incident and operations procedures | crash-anr-investigator |
| `research/` | External-source evidence gathering and screening | researcher |
| `devops/` | Repository and version-control procedure — history operations, recovery, forensics, and the Unity-specific git surface | git-expert |

**Adding a group.** It is well-formed when it can fill all three columns without overlapping an existing row — a body of work with a consumer the current groups do not serve. Do not open a group to shelve a single skill that already fits one. Every skill belongs to exactly one group; a skill that plausibly fits two means either the groups are cut wrong or the skill is doing two jobs, which §1 should have caught.

**Nothing inside a skill depends on its group.** That is what the Portability contract (A.4) buys: no file may reference a group path, so the same folder drops into a differently-named group in another project with no edit. Consequently the group set may differ per project, and the archetype a skill's §6 uses is chosen by what it delivers — not by which folder it sits in.

## A.3 Normative rules

| Scope | Rule |
|---|---|
| Frontmatter | Exactly two keys: `name`, `description`. **MUST** — no other keys. |
| `description` | 50–100 words, naming the distinctive API/symbol surface and closing with a terse **Not for:** list — `<concern> (owning-skill)` per boundary, one line — covering every adjacent skill. Nothing outside this text is read at retrieval time; a file path named here is inert. **MUST** |
| `description` — line breaks | The `>` folded scalar joins lines with a space, so no line may end mid-token — not on `/`, `(`, `[`, or a hyphen. A line ending `` `A`/ `` renders as `` `A`/ `B` ``, splitting the alternation. Break between words instead. **MUST** |
| Structure | Sections 1–8, numbered, in order, none omitted. **MUST** |
| Bundled resources | Present iff the folder ships files beyond SKILL.md; one table per type, only the tables that have rows. Unnumbered, directly under the H1. **MUST** |
| §3 | Every boundary in `description` restated as a `Negative trigger:` bullet. **MUST** |
| §4 | Each step bolds its directive, states *why*, and resolves to a decision; cite every bundled file inline at its point of use; name the governing `.claude/rules/*.md` file as ``` `file.md`'s <Section> section ```. **MUST** |
| §4 — directive text | No punctuation inside the closing `**`: write `**Directive** — why`, never `**Directive.**`. The bolded span is a quotable key, and `Covers:` matches it verbatim. **MUST** |
| §5 | Final bullet is `Out of scope:`, routing each excluded concern to the owning skill or role. **MUST** |
| §6 | A literal fenced block, not prose. Technique archetype ends `Layer:` + `Known limitations:`; decision/gate archetype ends `Decision:` or a verdict + `Routed to:`. Extended report defined and marked request-only. **MUST** |
| `references/*.md` | Each file follows `skill-reference-template.md`: no frontmatter, `Source:` + `Covers:` header, one topic per file, tables carrying a `Source` column, and a `Covers:` line quoting the §4 directive(s) it serves — never a step number or range. **MUST** |
| §7 | 2–4 Input/Output pairs, ≥1 of which is a declined wrong suggestion. **SHOULD** |
| §8 | Guardrails as `Never …` imperatives, each with its consequence. **SHOULD** |
| Size — file | Body **< 200 lines**, hard ceiling. **MUST** — **100–150 lines** is the target band; overflow moves to `references/*.md`, never into denser lines. **SHOULD** |
| Size — line | **≤ 150–180 words** per line (whitespace-separated tokens). A line past that is carrying more than one idea — split the step. **MUST** |
| Language | English throughout, per `.claude/rules/language-and-comments.md`. **MUST** |

The body loads in full the moment the skill triggers, so every line is a
standing context cost paid on every invocation — the budget is what keeps a
skill cheap enough to be worth firing. The two limits fail differently: an
over-long *file* means content belongs in `references/*.md`; an over-long
*line* means one step is doing several things and needs splitting, and no
amount of moving content elsewhere fixes it.

When no sibling skill is adjacent, the `Not for:` list names the owning
**role** instead (`tech-lead-performance`, `technical-artist`). A skill with
nothing at all to exclude has an unbounded scope, not a clean one — find the
nearest confusable concern and say where it goes. An empty `Not for:` is
never the answer.

Where the words actually go: measured on a 251-word description, the symbol
surface cost ~40 words and the boundaries cost **162** — written as one
`Do not use this for X — that's Y` paragraph per neighbour. Compressing those
same four boundaries to a single `Not for:` list, with every symbol kept,
lands at 74 words. So the budget is met by fixing the boundary *form*, never
by dropping symbols, and never by moving them into a reference file — a
reference is invisible at the moment retrieval happens.

## A.4 Portability contract

A skill folder is a self-contained, drop-in unit. It must resolve identically after being copied into any project, under any group folder, with or without its neighbours present. That holds only if **no link ever escapes the skill's own folder**.

| Target | Correct form | Why |
|---|---|---|
| Bundled file, cited from `SKILL.md` | `[topic-a.md](references/topic-a.md)`, `[name.py](scripts/name.py)` | Relative to SKILL.md; survives any relocation. |
| Sibling reference, cited from another reference | `[topic-b.md](topic-b.md)` | Same directory; no traversal. |
| Own SKILL.md, cited from a reference | `[SKILL.md](../SKILL.md)` | One level up, still inside the skill folder. |
| **Another skill** | ``` `other-skill-name` ``` — backticked name, **never a path** | The other skill may be absent, renamed, or in a different group in the target project. |
| **Project rule file** | ``` `coding-principles.md`'s <Section> section ``` — filename, **never a link** | Rules live outside the skill folder; a name degrades to a readable mention, a broken link does not. |
| Upstream documentation | Full `https://` URL | Absolute and project-independent by nature. |

Forbidden in every file of the skill: absolute paths, project-rooted paths (`.claude/skills/…`), and any `../../` traversal that leaves the skill folder. A cross-skill path such as `../../other-skill/references/x.md` is the most common breakage — it silently assumes both skills sit in the same group folder in every project. Reference the other skill by name.

Scripts follow the same rule for citation; at execution time, resolve `scripts/<name>` against the directory the skill was loaded from, not the shell's working directory.

# APPENDIX B — Pre-ship checklist (authoring aid; delete before shipping)

Each item maps to a distinct silent-failure mode — a skill that never fires, or one that fires and misleads.

- [ ] `name` equals the leaf folder name, kebab-case, unique project-wide; frontmatter has only `name` + `description`.
- [ ] `description` is 50–100 words and names real symbols/APIs — prose-only descriptions never match retrieval.
- [ ] `description` ends with one `Not for:` list naming **every** adjacent skill and the concern it owns — not a paragraph per neighbour.
- [ ] `description` carries every symbol retrieval must match; none has been displaced into `references/`, which retrieval never sees.
- [ ] No `description` line ends mid-token, which the `>` fold would split with a space: `sed -n '/^description: >/,/^---$/{/^---$/d;p}' SKILL.md | grep -nE '[/([-]$'` returns nothing.
- [ ] Sections 1–8 are all present, numbered, and in order — none added, dropped, renumbered, or reordered.
- [ ] Every `description` boundary reappears as a §3 `Negative trigger:` bullet.
- [ ] What `description` promises is what §4 actually instructs — no promise the workflow doesn't deliver.
- [ ] No step, guardrail, or example resolves to "it depends" — each names its deciding criterion.
- [ ] No §4 directive closes its bold over punctuation: `grep -nE '^\s*[0-9]+\. \*\*.*[.,;:]\*\*' SKILL.md` returns nothing — a swallowed period makes the directive unquotable by `Covers:`.
- [ ] §4 defines behaviour for missing/ambiguous input; §8 defines it for the failure cases.
- [ ] Any destructive or hard-to-reverse action is gated on explicit user confirmation in §8.
- [ ] Skill produces code or technical documents → §4 names the governing `.claude/rules/*.md` sections.
- [ ] §5 ends with `Out of scope:`; §6 is a literal copy-pasteable block matching its archetype, plus the request-only extended report.
- [ ] §7 carries 2–4 Input/Output examples, at least one of which declines a plausible wrong suggestion.
- [ ] Every bundled file exists, appears in its "Bundled resources" table, **and** is cited in a §4 step — and every table row points at a file that exists.
- [ ] Every reference passes `skill-reference-template.md`'s own checklist; each "Read when" cell states a condition, not a topic restatement.
- [ ] Portability: `grep -rn '](\.\./\.\./\|](\.claude/\|](/' <skill-folder>` returns nothing; cross-skill and rule-file references are names, not paths.
- [ ] Body < 200 lines (100–150 optimal): `awk 'END{print NR}' SKILL.md`.
- [ ] No line over 150–180 words: `awk 'NF>180 {print FNR": "NF" words"}' SKILL.md` returns nothing.
- [ ] English throughout — body, examples, comments, and every bundled file — per `.claude/rules/language-and-comments.md`.
- [ ] The `AUTHORING THIS SKILL` comment block and both appendices are deleted: `grep -n 'AUTHORING THIS SKILL\|APPENDIX' SKILL.md` returns nothing.
