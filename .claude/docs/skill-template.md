---
name: [skill-name-in-kebab-case]
description: >
  [One to three sentences: what this skill does AND when Claude should use it.
  This description is the ONLY thing Claude sees before deciding to open the
  skill, so front-load concrete trigger phrases and contexts. Be a little
  "pushy" — Claude tends to under-trigger skills, so spell out situations
  explicitly rather than being vague. Include at least 2 concrete, quoted
  trigger phrases, and at least one explicit negative trigger if this skill
  could plausibly be confused with a nearby task it should NOT handle.
  Example: "Use this skill whenever the user asks to generate a changelog,
  mentions 'release notes', or wants a summary of commits between two git
  tags — even if they don't say 'changelog' explicitly. Do not use it for a
  single one-line commit message the user dictates verbatim."]
---

<!--
=====================================================================
 HOW TO USE THIS TEMPLATE
=====================================================================
1. Copy this file to: .claude/skills/[skill-name]/SKILL.md
   (project-level)  OR  ~/.claude/skills/[skill-name]/SKILL.md (personal)
2. Fill in every [bracketed] section below.
3. Delete this comment block and any section you don't need.
4. Keep the body under ~500 lines. If it grows past that, move detail
   into references/*.md files and link to them instead of inlining.
5. If this skill needs helper scripts, put them in scripts/ next to
   this file and call them with bash — don't paste long code inline.
6. Before considering the file done, run it through the "Post-write
   validation checklist" (§10) at the bottom of this document. Every
   item there maps to a real way a skill silently fails to trigger or
   silently misleads Claude — it is not boilerplate.
=====================================================================
-->

# [Skill Name]

## 1. Objective (why this skill exists)
[One paragraph. What outcome does this skill produce for the user?
What problem does it solve that Claude can't already do well on its own?
Example: "Ensures every generated commit message follows Conventional
Commits format so CI tooling and changelogs stay parseable."]

## 2. Role (what persona/expertise Claude should adopt)
[Describe the expertise or perspective Claude should take on while this
skill is active. Example: "Act as a senior release engineer who cares
about clean, machine-parseable git history and reproducible releases."]

## 3. When to invoke this skill (trigger conditions)
Claude should consult this skill when:
- [Explicit trigger phrase or request, e.g. "user says 'write release notes'"]
- [Implicit context, e.g. "user is looking at a CHANGELOG.md file"]
- [File/extension trigger, e.g. "a .proto file is being edited"]
- [Negative trigger — when NOT to use it, e.g. "do not use for simple one-line
  commit messages the user dictates verbatim"]

## 4. How to use this skill (workflow)
Describe the step-by-step process Claude should follow, in imperative form.

1. [Step 1 — e.g. "Run `git log <last-tag>..HEAD --oneline` to gather commits"]
2. [Step 2 — e.g. "Group commits by type: feat, fix, chore, docs, refactor"]
3. [Step 3 — e.g. "Draft the changelog section using the format in §6"]
4. [Step 4 — e.g. "Show the draft to the user before writing any file"]
5. [If required input/context is missing or ambiguous: the concrete fallback
   — ask the user / proceed on a clearly-flagged assumption — don't leave
   this undefined]
6. [If this project has a shared cross-cutting rule file, e.g.
   `.claude/rules/shared/language-and-comments.md`, and this skill produces
   code or technical documents: instruct Claude to read and follow it]
7. [Step N — continue until the task is complete]

## 5. Specific goals / tasks this skill performs
List the concrete, checkable outcomes this skill is responsible for:
- [Goal 1, e.g. "Every entry links to its PR number"]
- [Goal 2, e.g. "Breaking changes are called out in a dedicated section"]
- [Goal 3, e.g. "Output matches the exact Markdown template below"]

## 6. Output format
ALWAYS use this exact structure for the final result:
```
[Paste the literal template/schema/format the output must follow.
This removes ambiguity and gives Claude something to pattern-match to.
A prose description of what the output should contain is not enough —
this must be a literal, copy-pasteable template.]
```

## 7. Examples
**Example 1**
- Input: [what the user asked / what state the repo was in]
- Output: [what the skill produced]

**Example 2**
- Input: [...]
- Output: [...]

## 8. Edge cases & guardrails
- [What to do if input is missing/ambiguous]
- [What NOT to do — e.g. "never force-push", "never delete existing entries"]
- [When to ask the user for clarification vs. make a reasonable assumption]
- [If this skill could plausibly trigger a destructive or hard-to-reverse
  action — deploy, publish, delete, force-push, spend money, contact an
  external system — state explicitly that it must be gated behind explicit
  user confirmation in the current conversation, not assumed from context]

## 9. Bundled resources (optional)
[Every script, reference doc, or asset this skill uses must be listed
below in its own table, grouped by type. One row per file. Do not mix
types in the same table — keep scripts, references, and assets separate
so Claude can quickly see what's executable vs. what's read-only context
vs. what's used directly in output. Every path listed here must actually
exist in the skill's directory — see §10.]

### 9.1 Scripts
Executable code for deterministic/repetitive tasks — Claude runs these with Bash rather than reimplementing the logic inline.

| File path | Purpose | When to run it | Input | Output |
|---|---|---|---|---|
| `scripts/[name].py` | [what it does] | [trigger condition, e.g. "before writing final output"] | [args/files it expects] | [what it produces] |
| `scripts/[name].sh` | [what it does] | [trigger condition] | [args/files it expects] | [what it produces] |

### 9.2 References
Documentation loaded into context only when needed — keeps SKILL.md itself short.

| File path | Contents | When to read it |
|---|---|---|
| `references/[name].md` | [what detail/spec/schema it holds] | [e.g. "only when handling the AWS variant"] |
| `references/[name].md` | [...] | [...] |

### 9.3 Assets
Files used directly in the output (templates, icons, fonts, boilerplate).

| File path | Purpose | Used in |
|---|---|---|
| `assets/[name]` | [what it is] | [where/how it's inserted into the final deliverable] |
| `assets/[name]` | [...] | [...] |

[If a category has no files, delete that subsection entirely rather than leaving an empty table.]

## 10. Post-write validation checklist

Run through every item before treating a skill file as done. Each one maps to a real way a skill fails silently — either it never triggers, or it triggers and misleads Claude:

- [ ] `name` matches the skill's directory name exactly (`.claude/skills/<name>/SKILL.md`), kebab-case, and is unique across the project's whole skill set.
- [ ] `description` gives Claude at least 2 concrete, quoted trigger phrases — not an abstract restatement of the skill's purpose. This is the only thing Claude sees before deciding to invoke the skill, so vagueness here means the skill silently never fires.
- [ ] `description` states at least one explicit negative trigger if the skill could plausibly be confused with a nearby task it should NOT handle.
- [ ] SKILL.md body stays under ~500 lines; anything longer has been moved into `references/*.md` and linked, not left inlined.
- [ ] Every script/reference/asset path listed in §9's tables actually exists in the skill's directory — a listed-but-missing file breaks the skill the moment Claude tries to use it.
- [ ] `description`'s promise matches what §4's workflow actually instructs Claude to do — nothing promised in the trigger description that the workflow doesn't deliver.
- [ ] Behavior under missing/ambiguous input is explicit in §8, not left for Claude to improvise.
- [ ] Any destructive or hard-to-reverse action this skill could trigger is explicitly gated behind explicit user confirmation in §8.
- [ ] If this skill produces code or technical documents in a project that has a shared cross-cutting rule file (e.g. a language/comment convention, a naming convention), §4's workflow explicitly tells Claude to read and follow it.
- [ ] §6's output format is a literal, copy-pasteable template — not just a prose description of what the output should contain.
