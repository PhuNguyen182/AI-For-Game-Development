# Skill template

A skill holds knowledge or a procedure an agent loads on demand. Project rules and role behaviour live elsewhere; cite them by name.

````markdown
---
name: <leaf-folder-name>               # = folder name
description: "<what it covers, distinctive symbols first>. Use when <task in the requester's words>."
when_to_use: "<trigger phrases>"       # only when needed
argument-hint: "[target]"              # only when it takes input
arguments: [target]                    # only when the body reads $target
user-invocable: false                  # domain or method skill; omit for a /command pipeline
---

# <Subject>

- **Not for:** <concern> (`owning-skill`), <concern> (`owning-skill`).
- **Docs:** <base URL, pinned @version when upstream versions it> — <the one version caveat that matters>.

## References
- **[topic.md](references/topic.md):** <a concrete trigger: a symptom or decision, not the topic name>.

## Scripts
- **[x.ps1](scripts/x.ps1):** run `pwsh -NoProfile -File "${CLAUDE_SKILL_DIR}/scripts/x.ps1"` → <what it prints or writes>.
- **[y.cs](scripts/y.cs):** adapt into `<target path>` → <what it provides>.

## Steps
1. **<title>:** <what to do; the criterion that decides>.
2. **<title>:** per [topic.md](references/topic.md).
3. **Missing input:** dispatched agent → `Blocked` or `Needs-decision`; main session → `AskUserQuestion`; otherwise proceed on a stated assumption.
4. **Final check:** walk [checklist.md](checklist.md) before returning.

## Never
- **<limit>:** <a mistake no step forbids> — <its consequence>.

## Output
```
## <Subject> — <target>
- **<Decision axis>:** <choice> — <reason>
```

## Example
- **"<plausible wrong request>":** declined — <why>; did <what> instead.
````

`checklist.md`, beside `SKILL.md`:

```markdown
# <Subject> checklist

## <Optional group>
- [ ] **<title>:** <short description of the check>.
```

## Format
- **Bullets:** every item is `- **<title>:** <short description>`, in every section.
- **Steps:** same shape, numbered because order matters; ordered so each ends in a decision or a criterion that makes one.
- **Fact per bullet:** one; split a bullet that needs "and" twice.
- **Short lines:** no prose paragraphs; a list item past 200 chars warns.
- **Exhaustive criteria:** list every criterion; never trim one to save lines.
- **More lines are fine:** line count is not a budget; line length is.
- **Language:** English throughout.

## Frontmatter
- **`name`:** the leaf folder name, self-describing; it is all that remains when the listing drops a description.
- **`description`:** what the skill covers, distinctive symbols first (package, types, members, settings, commands).
- **`description` trigger:** ends in `Use when <task>`, unless `when_to_use` holds the trigger.
- **`description` limits:** never lists procedure steps; never 'This skill', 'comprehensive', 'Preloaded by'.
- **`when_to_use`:** when needed, the trigger in the requester's words.
- **Length:** `description` + `when_to_use` target ≤120 chars; verify-layer warns past it and fails past 250.
- **`argument-hint`, `arguments`:** when the skill takes input; the body reads it through `$ARGUMENTS` or `$name`.
- **`user-invocable: false`:** required for a domain or method skill; absent only for a `/command` pipeline.
- **`allowed-tools`:** optional; tools usable without a prompt during the invoking turn.

## Sections
- **Always:** `Steps`, unless the skill is a pipeline, standard or method skill.
- **Pipeline, standard, method skills:** may use their own stage or topic headings instead of `Steps`.
- **`References`, `Scripts`, `Never`, `Example`:** only when non-empty.
- **`Output`:** decision fields only.
- **Envelope fields:** status, verification and limitations go in the `agent-protocol` envelope, never in `Output`.
- **No envelope:** a report the main session gives the GD has no envelope; its `Output` may keep a `Status:` line.
- **Examples:** only for a case the steps do not make obvious, usually a declined wrong suggestion; 0–2, one line each.

## Say each fact once
- **SKILL.md:** the procedure.
- **`references/`:** the facts the procedure needs.
- **`scripts/`:** code that runs or is adapted.
- **`checklist.md`:** the checks.
- **Project rules, other skills:** cite by name, never paraphrase.
- **Scope:** lives in `Not for:` alone. No "When to invoke" list, "Out of scope" bullet or negative-trigger list.
- **`Never`:** holds only what no step covers; a guardrail that restates a step is deleted.

## Cut on sight
- **Framing:** Objective, Role and "Act as" paragraphs, motivation, summaries.
- **Meta lines:** "loaded on demand so this file stays short", "read-only context".
- **Common knowledge:** what a strong model already applies (what reflog is, SOLID explained, PascalCase methods).
- **Keep instead:** what this project or version does differently, and non-obvious gotchas.
- **Explanation, not criteria:** cut explanation; never cut a criterion.
- **Authoring notes:** "fetched on", "page truncated". An unverified fact goes in one `Unverified:` line in the reference that holds it.
- **Foreign output fields:** fields that do not apply to the domain (`Layer:` in a git skill).

## Never force a load
- **No forced reads:** no "Read when: starting any task", no "read all/both before ...".
- **Triggers:** each reference has a trigger that some tasks do not meet.
- **Links file:** no root-links.md; a doc base URL and version pin go in the `Docs:` line.

## Cost
- **Loaded content:** stays in context across later turns, so every line is a recurring cost.
- **Compaction:** keeps only the first 5,000 tokens of a skill; critical instructions go near the top.
- **Body size:** ≤8,000 chars, soft. Past it, move facts to references; never cut a criterion to fit.
- **Listing:** all skills share one description budget, 1% of the context window by default, raised through `skillListingBudgetFraction` in `.claude/settings.json`.
- **Listing check:** a description added past the ≤120 target or a new skill can overflow the budget, so check `/context`, which reports its size, after adding skills.
- **Overflow:** the listing drops descriptions of the least-invoked skills first.

## `checklist.md`
- **When:** the skill has acceptance criteria worth checking one by one. Omit otherwise.
- **Location:** `<skill>/checklist.md`, beside `SKILL.md`.
- **Format:** only `- [ ] **<title>:** <short description>` lines, plus an optional H1 and `##` groups.
- **Loading:** a `SKILL.md` step links it and names when to walk it, so it costs nothing until needed.
- **Reporting:** a dispatched agent reports each item in `Verified`.
- **Boundary:** states the check, not the procedure; no repeat of a step.

## Scripts
- **Language:** any programming language that runs and fits the task's context; add one only when the skill needs it.
- **Extension:** the language's real extension, or the name the target tool demands (`Jenkinsfile`, `Fastfile`).
- **Runtime:** the bullet names the runtime when it is not obvious from the command.
- **Runtime absent:** report `Blocked`; never redo the script's job by hand.
- **Invocation:** through the interpreter or runtime with a quoted path, never a bare script path.
- **Run or adapt:** each bullet says which; an adapt file names its target path.
- **`--help`:** the CLI's documentation for a CLI script; a reference does not repeat it.
- **Output:** what the agent needs and nothing else; bound long output (cap it, or print a count plus the file path).
- **Errors:** one line to stderr, no banners.
- **Header:** ≤5 lines in the language's comment form: what it does, and any non-obvious contract.
- **Verified before shipping:** it ran, or compiled for an adapt file; otherwise an `Unverified:` line in its header says so.
- **`.ps1`:** ASCII only, enforced by verify-layer; first choice for shell automation, per the `core.md` shell order.
- **`.sh`:** LF line endings, enforced by verify-layer.
- **`.cs` location:** Unity ignores it under `.claude/`.
- **`.cs` running:** through the `core.md` Unity tool order, or copied in as a temporary Editor helper per `agent-protocol`.
- **`.cs` Editor use:** follows the Editor hold rule.
- **`.js`:** workflow scripts stay in `.claude/workflows/`; `scripts/` holds plain runtime scripts.

## Code in references
- **Threshold:** a fenced block of 15+ lines, or a whole file, moves to `scripts/` in its real language.
- **What stays:** the reference keeps facts and short snippets, and links the file as `../scripts/x.cs`.
- **SKILL.md:** lists the script when it can be used without the reference.

## Portability
- **Links:** never leave the skill folder: `references/x.md`, `scripts/x.py`, `checklist.md`; from a reference, `../SKILL.md`, `../scripts/x.py`.
- **Another skill:** `skill-name` in backticks.
- **A rule file:** `csharp.md` by name.
- **Upstream docs:** full https URL.
- **Script paths:** `${CLAUDE_SKILL_DIR}/scripts/x`, never a hardcoded `.claude/skills/...` path.

## Testing
- **Gate and process skills:** one baseline scenario run without the skill, then with it.
- **Domain skills:** no behaviour test required.

## Checks before shipping
- **Layer:** `/verify-layer` passes.
- **Checks that fail:**
  - **`description`:** a banned phrase, no `Use` trigger, or `description` + `when_to_use` past 250 chars.
  - **Body lines:** a `Latent concerns` line, a `Verified` or `Known limitations` bullet, or an untitled item or prose line.
  - **References and scripts:** a reference or script table, a hardcoded script path, a script not named, or a reference fence of 15+ lines.
- **Checks that warn:** `description` + `when_to_use` past 120 chars, a list item past 200 chars, a body past 8,000 chars.
- **Cited headings:** headings other files cite by name still exist (grep the skill name).
- **References and scripts:** each is named in the body and used in a step.
