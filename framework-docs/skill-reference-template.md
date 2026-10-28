<!--
=====================================================================
 SKILL REFERENCE TEMPLATE — authoring blueprint for references/*.md
=====================================================================
 Companion to [skill-template.md](skill-template.md), which governs
 SKILL.md itself. This file governs every file under a skill's
 `references/` folder.

 Division of labour — do not blur it:
   SKILL.md       = the procedure. What to do, in what order, deciding what.
   references/*.md = the context that procedure needs. API surface, caveats,
                     upstream links, worked syntax. Never a second procedure.

 A reference file exists for exactly one reason: SKILL.md would exceed its
 budget (< 200 lines, 100–150 optimal, ≤150–180 words per line) if this
 content sat inline. That budget does NOT apply here — a reference loads
 only on demand, so its own limits are looser and set in Appendix A below.
 If the content does not serve a §4 step, it does not belong in the skill.

 HOW TO USE THIS FILE — it differs from skill-template.md:
   skill-template.md IS the file you fill in; you copy it whole and replace
   its [bracketed] slots.
   THIS file is a guide that CONTAINS skeletons. You copy only the fenced
   skeleton block of your chosen archetype into the new reference file —
   never this file itself, and never its prose or appendices.

 Procedure:
   1. Every file obeys Part 1 (header contract, presentation, sourcing).
   2. Pick ONE archetype — Part 2, 3, or 4 — and copy its skeleton.
   3. Obey the Writing mandate in skill-template.md's Appendix A.1; it is
      binding here too.
   4. Check the finished file against Appendix B before shipping.
 Appendix A and B stay in THIS file permanently — they are the standard, not
 boilerplate to be deleted from it.
=====================================================================
-->

# PART 1 — Header contract (every reference file, no exceptions)

A reference file carries **no YAML frontmatter**. It opens with exactly these four elements, in this order, then its body.

```markdown
# <Topic> — <the specific API surface this file holds>

Source: [<page title>](<full https URL>), [<page title>](<full https URL>).
Covers: SKILL.md §4 — **"<the step's bolded directive, quoted verbatim>"**.

<One to three sentences: what this file holds, and the single decision it
exists to serve. State any boundary a reader would otherwise have to
reverse-engineer — including what deliberately lives in a sibling skill.>
```

**`Source:`** — the upstream pages this file was distilled from, as full `https://` URLs. Plural `Sources:` when more than one. Content that is synthesized rather than sourced says so explicitly: `Not sourced from a single URL — synthesized from <what>.`

**`Covers:`** — quote the step's **bolded directive text**, never its ordinal.

> `Covers: SKILL.md §4 — **"Pick the allocator by actual data lifetime"**.` ✅
> `Covers SKILL.md step 6.` ❌ — renumbering §4 silently invalidates the pointer, with no error and no test to catch it.

Quote the bolded span **exactly**, punctuation included. §4 directives close the
bold before any punctuation ([skill-template.md](skill-template.md)'s A.3), so
the quote carries none either — the sentence's own period sits outside the
closing `**`. A directive written `**…alone.**` puts a period inside the key and
no quote can match it; fix the directive, not the quote.

Section numbers `§1`–`§8` are frozen by [skill-template.md](skill-template.md)'s Appendix A.3 and are safe to cite; step ordinals inside §4 are not.

A file serving several steps quotes each directive, comma-separated — quoting a *range* reintroduces the ordinal coupling this rule exists to remove:

| Case | Form |
|---|---|
| One step | `Covers: SKILL.md §4 — **"<directive>"**.` |
| Several steps | `Covers: SKILL.md §4 — **"<directive A>"**, **"<directive B>"**.` |
| A step's escalation branch only | `Covers: SKILL.md §4 — **"<directive>"**, escalation branch.` |
| `root-links.md` | `Covers: the whole skill — provenance and version anchor for every file in this folder.` |

Serving more than two or three directives is a signal the file holds more than one topic — split it rather than widening the header.

**Table of contents** — required once the file exceeds ~120 lines. Place it directly under the orientation paragraph, one anchor link per `##` heading, so the file can be navigated instead of read whole.

## Presentation — tables by default

Body content is **tabular wherever it enumerates anything**: API surfaces, options, parameters, components, thresholds, comparisons, failure modes. Prose is the exception, not the default. A table forces one fact per cell, makes an omission visible as an empty cell, and lets Claude extract the row it needs without parsing a paragraph.

These rules govern `references/*.md` only. SKILL.md's own Bundled resources tables are set by [skill-template.md](skill-template.md) and do not carry a `Source` column.

Only these forms are exempt:

| Non-table form | Why it is allowed |
|---|---|
| The orientation paragraph | 1–3 sentences of framing — there is nothing to enumerate. |
| The table of contents | An anchor list is navigation, not content. |
| A fenced code block | A compiling snippet must stay verbatim and multi-line. |
| A bolded `**Critical caveat**:` line | Deliberately breaks the table rhythm so a skim cannot miss it. |
| A closing note that binds the whole file | It governs every row rather than being one — e.g. the version-pin rule in `root-links.md`. |

## Row-level sourcing

**Every table ends with a `Source` column**, and every row's cell links the exact upstream page — with its in-page anchor when the page covers several topics. The file-level `Source:` header states where the *file* came from; the column states where each *row* came from, which is what makes an individual claim checkable without re-reading the whole page.

| Rule | Consequence |
|---|---|
| A row with no source | Unverifiable — source it or cut it. |
| A row sourced to a page root when the page has anchors | Link the anchor; a page-root link makes the reader search. |
| A row pointing inside this skill's own folder | Use the sibling link form in Appendix A.1, not a URL. |
| A row synthesized rather than sourced | Write `synthesized` in the cell, never leave it blank. |

---

# PART 2 — Archetype R: `root-links.md`

Every skill built from external documentation ships this file, and it is the first row of the References table in SKILL.md. It is the provenance record and the version anchor for the whole folder.

```markdown
# Root Links — <Product> <version>

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to <Product> <version>. Anything this skill
cites resolves under one of these roots; anything that does not is out of
scope for the skill, not merely undocumented here.

| Root | Holds | Source |
|---|---|---|
| Manual | <conceptual and how-to material> | [<Product> Manual index](https://.../@<version>/manual/index.html) |
| Scripting API | <type and member reference> | [<Product> API index](https://.../@<version>/api/index.html) |

Every other link in this `references/` folder is a specific page under these
roots, pinned to `@<version>`, each verified to resolve before inclusion.
Keep the `@<version>` segment when following any link from this skill —
a different version's API may differ. Consult the live site for anything not
covered here; <product> adds features between releases.
```

`root-links.md` is the one file whose `Source:` names its roots in prose rather than linking them, because those URLs are the file's own content — they appear, linked, in the table below it.

**Version pinning is mandatory** when upstream publishes versioned docs. Pin once here, use the same pin in every sibling file, and never mix pins inside one skill. Unversioned upstream docs (a library site with no version in the URL) say so instead of inventing a pin.

---

# PART 3 — Archetype L: annotated link index

**Use when** upstream documentation is authoritative, current, and better read at the source than paraphrased — most Unity package and platform SDK skills. The file is a routing layer: it tells Claude which page answers which question, and carries just enough fact inline that an obvious call needs no fetch at all.

```markdown
# <Topic> — <the specific API surface this file holds>

Source: [<page>](<url>).
Covers: SKILL.md §4 — **"<step directive>"**.

<Orientation: the decision this file serves. Name the sibling skill that owns
any adjacent concern, by backticked name.>

## <Concept group>

| Subject | What it decides | Source |
|---|---|---|
| `<exact type/member/setting>` | <the fact that settles a choice: threshold with its unit, the failure mode and what triggers it, the constraint not implied by the name> | [<page>](<url>) |
| `<exact type/member/setting>` | <...> | [<page>](<url>#<anchor>) |

## API index

| Type | Source |
|---|---|
| `<Type\<T\>>` | [<api page>](<url>) |
| `<Type\<T\>>` | [<api page>](<url>) |
```

**The `What it decides` cell is the deliverable, not the link.** It must settle something — `Allocator.TempJob` must be disposed within ~4 frames or it raises a leak warning; a `ParallelWriter` can append but cannot grow capacity, so pre-size the list. A cell that restates the page title is dead weight: cut the row or write the fact.

The `API index` table is the sole two-column form, used where the type name is itself the whole entry. Everywhere else the middle column is mandatory. Escape generics as `Type\<T\>` so Markdown does not eat the brackets.

---

# PART 4 — Archetype D: distilled reference

**Use when** upstream is scattered across many small pages, is unversioned, or the skill needs worked syntax at hand — library skills (CsvHelper, Spine) and anything whose value is a correct code shape rather than a pointer.

````markdown
# <Topic> — <the specific API surface this file holds>

Sources: [<page>](<url>), [<page>](<url>), [<page>](<url>).
Covers: SKILL.md §4 — **"<step directive>"**.

<Orientation: the mechanism in one or two sentences — the registration call,
the lifecycle hook, the precondition every technique below assumes.>

## <Technique / concept>

| Member | Effect | Use when | Source |
|---|---|---|---|
| `<method/attribute/option>` | <what it does to the data or object> | <the condition that selects it over its siblings> | [<page>](<url>) |
| `<method/attribute/option>` | <...> | <...> | [<page>](<url>) |

```csharp
<minimal compiling snippet — no ellipses, no placeholder identifiers where a
real one would compile. One snippet per table, showing the shape the rows
above cannot convey.>
```

## <Comparison / variant set>

| Variant | <axis 1> | <axis 2> | Source |
|---|---|---|---|
| `<variant>` | <value> | <value> | [<page>](<url>) |

**Critical caveat**: <ordering constraint, silent-failure mode, or platform
limitation — bolded so it survives a skim.>
````

A code fence earns its place only where the **shape** is the point — a registration call, a class-map body, a lifecycle override. Everything a table can hold (which member, what it does, when to pick it, where it came from) belongs in the table above the fence, not in comments inside it.

Headings follow the **decision order a reader arrives in**, not upstream's table-of-contents order. Cross-link a sibling file at the point the reader needs it — `see [type-conversion.md](type-conversion.md)` — rather than duplicating its content.

**Cap a distilled file at ~250 lines.** Past that it is covering more than one topic: split by topic, or by component, and let the References table in SKILL.md route between them.

---
---

# APPENDIX A — Normative rules

| Scope | Rule |
|---|---|
| Frontmatter | None. A reference file is plain Markdown. **MUST** |
| Filename | kebab-case, `.md`, named for the topic it holds — not `notes.md`, `misc.md`, `part2.md`. **MUST** |
| H1 | Exactly one, first line, naming the topic and its API surface. **MUST** |
| `Source:` | Full `https://` URLs; or an explicit statement that the content is synthesized; or, in `root-links.md` alone, a prose pointer to the roots tabulated below it. **MUST** |
| `Covers:` | One of the four forms in Part 1 — single directive, comma-separated directives, directive + escalation branch, or `root-links.md`'s whole-skill declaration. Never a step ordinal or range. **MUST** |
| Orientation | 1–3 sentences stating the decision this file serves, directly under the header. In `root-links.md` it states what the pin covers instead. **MUST** |
| Table of contents | Required above ~120 lines; anchor link per `##`. **MUST** |
| Scope | One topic per file. Split at ~250 lines. **SHOULD** |
| Archetype | One of R / L / D per file, not a blend. **SHOULD** |
| Presentation | Enumerable content is a table. Prose only in the five forms Part 1 exempts: orientation, TOC, code fence, `**Critical caveat**:` line, whole-file closing note. **MUST** |
| Row sourcing | Every table ends with a `Source` column; every row's cell links the exact page (with anchor where the page is multi-topic), a sibling file, or the word `synthesized`. Never blank. **MUST** |
| `What it decides` (L) | Every cell carries a fact that settles a choice; never a restatement of the page title. **MUST** |
| Snippets (D) | Compile as written — real identifiers, no ellipses. **MUST** |
| Version pin | Pinned once in `root-links.md`; identical across every sibling file. **MUST** when upstream is versioned |
| Procedure | No step lists, no workflow, no output format — those live in SKILL.md. **MUST** |
| Duplication | Do not restate what SKILL.md already says; a symbol appears in both only when it is decision-critical in both. **SHOULD** |
| Registration | Every file appears in SKILL.md's References table **and** is cited inline in a §4 step. An uncited file is dead weight. **MUST** |
| Language | English throughout, per `.claude/rules/language-and-comments.md`. **MUST** |

## A.1 Portability

Identical contract to [skill-template.md](skill-template.md)'s Appendix A.4 — no link may leave the skill folder.

| Target | Correct form |
|---|---|
| Sibling reference | `[topic-b.md](topic-b.md)` |
| Own SKILL.md | `[SKILL.md](../SKILL.md)` |
| **Another skill** | ``` `other-skill-name` ``` — backticked name, **never a path** |
| **Project rule file** | ``` `coding-principles.md`'s <Section> section ``` — filename, **never a link** |
| Upstream documentation | Full `https://` URL |

`../../other-skill/references/x.md` is the single most common breakage: it assumes both skills sit in the same group folder in every project, and fails silently the moment one skill travels alone. Name the other skill instead.

# APPENDIX B — Pre-ship checklist (run against the finished reference file)

- [ ] No frontmatter; exactly one H1 on line 1; filename matches the topic.
- [ ] `Source:` present with full URLs, or synthesis stated explicitly.
- [ ] `Covers:` quotes every §4 directive the file serves, verbatim — **`grep -rnE 'steps? [0-9]' <skill-folder>/references` must return nothing**. `root-links.md` declares whole-skill coverage instead.
- [ ] Each quoted directive string-matches a §4 bolded span exactly; neither side swallows punctuation into the bold.
- [ ] Orientation paragraph states the decision served, and names the sibling skill owning any adjacent concern.
- [ ] File >120 lines → has a TOC; file >250 lines → split instead.
- [ ] One archetype, applied consistently through the file.
- [ ] Every enumerable block is a table; prose survives only as orientation, TOC, code fence, `**Critical caveat**`, or a whole-file closing note.
- [ ] Every table ends with a `Source` column, and no cell in it is blank.
- [ ] (L) Every `What it decides` cell settles something; two-column form only for the `API index` table.
- [ ] (D) Every snippet compiles as written; every caveat that can fail silently is bolded.
- [ ] Version pin identical to `root-links.md`; every URL verified to resolve.
- [ ] Nothing here restates what SKILL.md already says, unless the symbol is decision-critical in both.
- [ ] No procedure, no output format, no workflow — SKILL.md owns those.
- [ ] Listed in SKILL.md's References table with a real "Read when" condition, and cited in a §4 step.
- [ ] English throughout, per `.claude/rules/language-and-comments.md`.
- [ ] Portability: `grep -rn '](\.\./\.\./\|](\.claude/\|](/' <skill-folder>` returns nothing.
