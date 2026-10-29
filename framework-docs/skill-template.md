---
name: <leaf-folder-name>
description: "<≤250 chars, verify-layer fails past it. Distinctive symbols first (package, types, members, settings, commands), then `Use when <task in the requester's words>`. No filler: never 'This skill', 'comprehensive', 'Preloaded by'.>"
---

<!-- Copy the block below into SKILL.md, fill the <slots>, delete what does not apply,
     then check it against "Authoring rules" further down. Optional frontmatter keys:
     `user-invocable: false`, `allowed-tools: ...`. -->

# <Subject>

Not for: <concern> (`owning-skill`), <concern> (`owning-skill`).
Docs: <base URL, pinned @version when upstream versions it> — <the one version caveat that matters>.

| Reference | Read when |
|---|---|
| [topic.md](references/topic.md) | <a concrete trigger — a symptom or decision, not the topic name> |

| Script | Run |
|---|---|
| [x.py](scripts/x.py) | `<command line>` → <what it prints or writes> |

## Steps
1. **<Directive>** — <why, one clause>. <Deciding criterion or escalation condition.>
2. **<Directive>**, per [topic.md](references/topic.md).
3. **<Missing or ambiguous input>** — <ask, or proceed on a stated assumption>.

## Never
- <A mistake no step already forbids> — <its consequence>.

## Output
```
## <Subject> — <target>
- <Decision axis>: <choice> — <reason>
- Verified: <evidence, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "<plausible wrong request>" → declined: <why>; did <what> instead.

<!--
=====================================================================
Authoring rules (not shipped)
=====================================================================
Every line of SKILL.md is paid on every invocation. A line earns its place only
if Claude would act differently without it.

Say each fact once
- SKILL.md = the procedure. references/ = facts the procedure needs.
  Project rules and other skills = cite by name, never paraphrase them.
- Scope lives in `Not for:` alone. No "When to invoke" list, no "Out of scope"
  bullet, no negative-trigger list: the description and `Not for:` already route.
- A guardrail that restates a step is deleted. `## Never` holds only what no
  step covers. Omit the section when it would be empty.
- Examples only for a case the steps do not make obvious (usually a declined
  wrong suggestion). 0–2 examples, one line each.

Cut on sight
- Objective / Role / "Act as" paragraphs, motivation, summaries.
- Meta lines: "loaded on demand so this file stays short", "read-only context".
- Knowledge a strong model already applies (what reflog is, SOLID explained,
  PascalCase methods). Keep only what this project or this version does
  differently, and non-obvious gotchas.
- Authoring and provenance notes ("fetched on", "page truncated"). An
  unverified fact goes in one `Unverified:` line in the reference that holds it.
- Output fields that do not apply to the domain (`Layer:` in a git skill).

Never force a load
- No "Read when: starting any task", no "read all/both before ...". Each
  reference has a trigger that some tasks do not meet.
- No root-links.md. A doc base URL and version pin go in the `Docs:` line.

Shape
- Tables and bullets over prose; one idea per bullet; steps decision-ordered,
  each ending in a decision or a criterion that makes one.
- Target ≤ 120 lines. verify-layer warns past 500 (past 120 for a
  user-invocable pipeline); the description fails past 250 chars.
- English throughout.

Scripts
- `--help` is the CLI's documentation. A reference does not repeat it.
- Print what the agent needs and nothing else: bound long output (cap it,
  or print a count plus the file path), one-line errors to stderr, no banners.
- Docstring ≤ 5 lines: what it does, and any non-obvious contract.

Portability
- Links never leave the skill folder: `references/x.md`, `scripts/x.py`,
  `../SKILL.md` from a reference. Another skill: `skill-name` in backticks.
  A rule file: `csharp.md` by name. Upstream docs: full https URL.
- Resolve `scripts/` against the skill's own folder at run time.

Checks before shipping
- `/verify-layer` passes.
- Headings other files cite by name still exist (grep the skill name).
- Every reference and script appears in its table and is used in a step.
=====================================================================
-->
